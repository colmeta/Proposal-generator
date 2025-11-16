"""
Task Worker
Executes background tasks, calls appropriate agents, and updates job status
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback

from database.db import get_session
from database.models import Job, Project
from core.workflow_orchestrator import WorkflowOrchestrator
from services.background_processor import background_processor

logger = logging.getLogger(__name__)


class TaskWorker:
    """
    Worker that executes background tasks
    """
    
    def __init__(self, orchestrator: Optional[WorkflowOrchestrator] = None):
        """
        Initialize task worker
        
        Args:
            orchestrator: Workflow orchestrator instance (creates new if None)
        """
        self.orchestrator = orchestrator or WorkflowOrchestrator()
        self.logger = logging.getLogger(__name__)
    
    def execute_task(self, job_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task synchronously
        
        Args:
            job_id: Job ID from database
            input_data: Optional input data for the task
        
        Returns:
            Task result dictionary
        """
        db = get_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            # Check if job is cancelled
            if job.status == "cancelled":
                self.logger.info(f"Job {job_id} is cancelled, skipping execution")
                return {"status": "cancelled", "message": "Job was cancelled"}
            
            # Update job status to running
            job.status = "running"
            db.commit()
            
            self.logger.info(f"Executing job {job_id}: {job.task_type}")
            
            # Execute task using orchestrator
            try:
                result = self.orchestrator.execute_task(job_id, input_data)
                
                # Job status is updated by orchestrator
                self.logger.info(f"Job {job_id} completed successfully")
                return result
            
            except Exception as e:
                error_msg = str(e)
                error_trace = traceback.format_exc()
                self.logger.error(f"Job {job_id} failed: {error_msg}\n{error_trace}")
                
                # Update job status
                job.status = "failed"
                job.error = error_msg
                job.completed_at = datetime.utcnow()
                db.commit()
                
                return {
                    "status": "failed",
                    "error": error_msg,
                    "traceback": error_trace
                }
        
        except Exception as e:
            self.logger.error(f"Error executing job {job_id}: {e}")
            raise
        finally:
            db.close()
    
    def execute_task_with_retry(
        self,
        job_id: int,
        input_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Execute a task with automatic retry
        
        Args:
            job_id: Job ID from database
            input_data: Optional input data
            max_retries: Maximum number of retry attempts
        
        Returns:
            Task result dictionary
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = self.execute_task(job_id, input_data)
                
                # Check if task was successful
                if result.get("status") == "failed":
                    if attempt < max_retries:
                        self.logger.warning(
                            f"Job {job_id} failed (attempt {attempt + 1}/{max_retries + 1}). Retrying..."
                        )
                        continue
                    else:
                        return result
                
                return result
            
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    self.logger.warning(
                        f"Job {job_id} error (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying..."
                    )
                else:
                    self.logger.error(f"Job {job_id} failed after {max_retries + 1} attempts")
        
        # All retries exhausted
        return {
            "status": "failed",
            "error": str(last_error) if last_error else "Unknown error",
            "retries_exhausted": True
        }
    
    def cancel_task(self, job_id: int) -> bool:
        """
        Cancel a task
        
        Args:
            job_id: Job ID to cancel
        
        Returns:
            True if cancelled, False otherwise
        """
        db = get_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return False
            
            # Only cancel if pending or running
            if job.status in ["pending", "running"]:
                job.status = "cancelled"
                job.completed_at = datetime.utcnow()
                db.commit()
                
                # Remove from scheduler if scheduled
                scheduler_job_id = f"job_{job_id}_{job.task_type}"
                background_processor.remove_job(scheduler_job_id)
                
                self.logger.info(f"Job {job_id} cancelled")
                return True
            
            return False
        
        finally:
            db.close()


def execute_task_async(job_id: int, input_data: Optional[Dict[str, Any]] = None):
    """
    Execute a task asynchronously using background processor
    
    Args:
        job_id: Job ID from database
        input_data: Optional input data for the task
    """
    worker = TaskWorker()
    
    def task_wrapper():
        """Wrapper function for background execution"""
        try:
            worker.execute_task(job_id, input_data)
        except Exception as e:
            logger.error(f"Async task execution failed for job {job_id}: {e}")
    
    # Add job to background processor
    background_processor.add_job(
        job_id=job_id,
        func=task_wrapper,
        job_type="task_execution"
    )
    
    logger.info(f"Scheduled async execution for job {job_id}")

