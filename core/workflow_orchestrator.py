"""
Workflow Orchestrator
Main workflow engine that coordinates all agents, manages task flow,
handles errors and retries, and tracks state
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import logging
import traceback
from enum import Enum

from database.db import get_session
from database.models import Project, Job
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowOrchestrator:
    """
    Main workflow orchestrator that coordinates all agents
    """
    
    def __init__(self):
        """Initialize workflow orchestrator"""
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent: BaseAgent, task_types: Optional[List[str]] = None):
        """
        Register an agent with the orchestrator
        
        Args:
            agent: Agent instance (must inherit from BaseAgent)
            task_types: List of task types this agent can handle
                        If None, uses agent's task_type
        """
        if not isinstance(agent, BaseAgent):
            raise ValueError("Agent must inherit from BaseAgent")
        
        if task_types is None:
            task_types = [agent.task_type]
        
        for task_type in task_types:
            if task_type in self.agents:
                self.logger.warning(f"Agent for task type '{task_type}' already registered. Overwriting.")
            self.agents[task_type] = agent
        
        self.logger.info(f"Registered agent: {agent.name} for task types: {task_types}")
    
    def register_agents(self, agents: List[BaseAgent]):
        """
        Register multiple agents at once
        
        Args:
            agents: List of agent instances
        """
        for agent in agents:
            self.register_agent(agent)
    
    def create_project(
        self,
        name: str,
        funder_name: str,
        user_email: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> Project:
        """
        Create a new project
        
        Args:
            name: Project name
            funder_name: Funder name
            user_email: User email
            initial_data: Optional initial project data
        
        Returns:
            Created Project instance
        """
        db = get_session()
        try:
            project = Project(
                name=name,
                funder_name=funder_name,
                user_email=user_email,
                status="draft",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            
            self.logger.info(f"Created project: {project.id} - {name}")
            return project
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to create project: {e}")
            raise
        finally:
            db.close()
    
    def create_job(
        self,
        project_id: int,
        task_type: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Job:
        """
        Create a new job/task
        
        Args:
            project_id: Project ID
            task_type: Type of task
            input_data: Optional input data for the task
        
        Returns:
            Created Job instance
        """
        db = get_session()
        try:
            job = Job(
                project_id=project_id,
                task_type=task_type,
                status=TaskStatus.PENDING.value,
                result=None,
                error=None,
                created_at=datetime.utcnow()
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            
            self.logger.info(f"Created job: {job.id} - {task_type} for project {project_id}")
            return job
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to create job: {e}")
            raise
        finally:
            db.close()
    
    def execute_task(
        self,
        job_id: int,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task/job
        
        Args:
            job_id: Job ID
            input_data: Optional input data (if None, uses job's stored data)
        
        Returns:
            Task result dictionary
        """
        db = get_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            # Get agent for this task type
            agent = self.agents.get(job.task_type)
            if not agent:
                raise ValueError(f"No agent registered for task type: {job.task_type}")
            
            # Update job status
            job.status = TaskStatus.RUNNING.value
            db.commit()
            
            self.logger.info(f"Executing job {job_id}: {job.task_type}")
            
            # Prepare input data
            if input_data is None:
                input_data = {}
            
            # Add project context
            project = db.query(Project).filter(Project.id == job.project_id).first()
            if project:
                input_data["project"] = project.to_dict()
            
            # Execute agent
            try:
                result = agent.process(input_data)
                
                # Mark job as completed
                job.mark_completed(result)
                db.commit()
                
                self.logger.info(f"Job {job_id} completed successfully")
                return result
            
            except Exception as e:
                error_msg = str(e)
                error_trace = traceback.format_exc()
                self.logger.error(f"Job {job_id} failed: {error_msg}\n{error_trace}")
                
                job.mark_failed(error_msg)
                db.commit()
                
                raise
        
        finally:
            db.close()
    
    def execute_task_with_retry(
        self,
        job_id: int,
        input_data: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a task with automatic retry on failure
        
        Args:
            job_id: Job ID
            input_data: Optional input data
            max_retries: Maximum retry attempts (defaults to self.max_retries)
        
        Returns:
            Task result dictionary
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return self.execute_task(job_id, input_data)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    self.logger.warning(
                        f"Job {job_id} failed (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {self.retry_delay}s..."
                    )
                    import time
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Job {job_id} failed after {max_retries + 1} attempts")
        
        raise last_error
    
    def execute_workflow(
        self,
        project_id: int,
        tasks: List[Dict[str, Any]],
        sequential: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a workflow of multiple tasks
        
        Args:
            project_id: Project ID
            tasks: List of task definitions, each with 'task_type' and optional 'input_data'
            sequential: If True, execute tasks sequentially. If False, execute in parallel.
        
        Returns:
            Dictionary with results for each task
        """
        self.logger.info(f"Starting workflow for project {project_id} with {len(tasks)} tasks")
        
        # Create jobs for all tasks
        job_ids = []
        for task in tasks:
            job = self.create_job(
                project_id=project_id,
                task_type=task["task_type"],
                input_data=task.get("input_data")
            )
            job_ids.append(job.id)
        
        results = {}
        
        if sequential:
            # Execute tasks one by one
            for i, job_id in enumerate(job_ids):
                task = tasks[i]
                try:
                    result = self.execute_task_with_retry(job_id, task.get("input_data"))
                    results[task["task_type"]] = result
                except Exception as e:
                    self.logger.error(f"Task {task['task_type']} failed: {e}")
                    results[task["task_type"]] = {"error": str(e)}
                    # Optionally stop on first failure
                    # break
        else:
            # Execute tasks in parallel (simplified - in production, use proper async/threading)
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_job = {
                    executor.submit(
                        self.execute_task_with_retry,
                        job_id,
                        tasks[i].get("input_data")
                    ): (job_id, tasks[i])
                    for i, job_id in enumerate(job_ids)
                }
                
                for future in concurrent.futures.as_completed(future_to_job):
                    job_id, task = future_to_job[future]
                    try:
                        result = future.result()
                        results[task["task_type"]] = result
                    except Exception as e:
                        self.logger.error(f"Task {task['task_type']} failed: {e}")
                        results[task["task_type"]] = {"error": str(e)}
        
        return results
    
    def get_job_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Get job status
        
        Args:
            job_id: Job ID
        
        Returns:
            Job status dictionary or None if not found
        """
        db = get_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                return job.to_dict()
            return None
        finally:
            db.close()
    
    def cancel_job(self, job_id: int) -> bool:
        """
        Cancel a pending or running job
        
        Args:
            job_id: Job ID
        
        Returns:
            True if cancelled, False if not found or already completed
        """
        db = get_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return False
            
            if job.status in [TaskStatus.PENDING.value, TaskStatus.RUNNING.value]:
                job.status = TaskStatus.CANCELLED.value
                job.completed_at = datetime.utcnow()
                db.commit()
                self.logger.info(f"Job {job_id} cancelled")
                return True
            
            return False
        finally:
            db.close()
    
    def get_project_jobs(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all jobs for a project
        
        Args:
            project_id: Project ID
        
        Returns:
            List of job dictionaries
        """
        db = get_session()
        try:
            jobs = db.query(Job).filter(Job.project_id == project_id).all()
            return [job.to_dict() for job in jobs]
        finally:
            db.close()

