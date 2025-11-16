"""
Project Manager Agent
Task coordination, progress tracking, dependency management, and deadline management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class ProjectManagerAgent(BaseAgent):
    """
    Project Manager Agent - Coordinates tasks, tracks progress, manages dependencies
    """
    
    def __init__(self):
        super().__init__(
            name="Project Manager Agent",
            role="Task coordination, progress tracking, and resource allocation",
            task_type="coordination"
        )
        self.max_concurrent_tasks = 5
        self.default_deadline_days = 30
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process project management request
        
        Args:
            input_data: Contains 'action' and relevant data
        
        Returns:
            Result dictionary
        """
        action = input_data.get("action", "breakdown_tasks")
        
        if action == "breakdown_tasks":
            return self.breakdown_tasks(input_data)
        elif action == "track_progress":
            return self.track_progress(input_data)
        elif action == "manage_dependencies":
            return self.manage_dependencies(input_data)
        elif action == "check_deadlines":
            return self.check_deadlines(input_data)
        elif action == "allocate_resources":
            return self.allocate_resources(input_data)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def breakdown_tasks(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Break down a project into manageable tasks
        
        Args:
            project_data: Project information including name, funder, requirements
        
        Returns:
            Task breakdown with dependencies and estimates
        """
        self.log_action("Breaking down project into tasks", {"project": project_data.get("name")})
        
        project_name = project_data.get("name", "Unknown Project")
        funder_name = project_data.get("funder_name", "Unknown Funder")
        requirements = project_data.get("requirements", {})
        
        prompt = f"""As a project manager, break down this funding proposal project into specific, actionable tasks.

Project: {project_name}
Funder: {funder_name}
Requirements: {json.dumps(requirements, indent=2)}

Create a detailed task breakdown with:
1. Task ID and name
2. Task type (research, writing, review, etc.)
3. Estimated duration (in hours)
4. Dependencies (which tasks must complete first)
5. Priority (high, medium, low)
6. Required resources/agents

Return as JSON:
{{
    "tasks": [
        {{
            "id": "task_1",
            "name": "Task name",
            "type": "research",
            "duration_hours": 4,
            "dependencies": [],
            "priority": "high",
            "description": "Task description"
        }}
    ],
    "estimated_total_hours": 40,
    "critical_path": ["task_1", "task_2"],
    "parallel_tasks": [["task_3", "task_4"]]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                self.log_action("Task breakdown completed", {"task_count": len(result.get("tasks", []))})
                return result
        except Exception as e:
            self.logger.warning(f"Task breakdown LLM call failed: {e}")
        
        # Fallback: Basic task breakdown
        return self._default_task_breakdown(project_data)
    
    def _default_task_breakdown(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Default task breakdown if LLM fails"""
        tasks = [
            {
                "id": "research_1",
                "name": "Funder Research",
                "type": "research",
                "duration_hours": 4,
                "dependencies": [],
                "priority": "high",
                "description": "Research funder requirements and priorities"
            },
            {
                "id": "research_2",
                "name": "Competitive Analysis",
                "type": "research",
                "duration_hours": 3,
                "dependencies": ["research_1"],
                "priority": "high",
                "description": "Analyze competitors and market"
            },
            {
                "id": "strategy_1",
                "name": "Strategy Development",
                "type": "strategy",
                "duration_hours": 6,
                "dependencies": ["research_1", "research_2"],
                "priority": "high",
                "description": "Develop proposal strategy"
            },
            {
                "id": "writing_1",
                "name": "Proposal Writing",
                "type": "writing",
                "duration_hours": 12,
                "dependencies": ["strategy_1"],
                "priority": "high",
                "description": "Write proposal content"
            },
            {
                "id": "review_1",
                "name": "Quality Review",
                "type": "review",
                "duration_hours": 4,
                "dependencies": ["writing_1"],
                "priority": "high",
                "description": "Review and refine proposal"
            }
        ]
        
        return {
            "tasks": tasks,
            "estimated_total_hours": sum(t["duration_hours"] for t in tasks),
            "critical_path": ["research_1", "research_2", "strategy_1", "writing_1", "review_1"],
            "parallel_tasks": []
        }
    
    def track_progress(
        self,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track project progress
        
        Args:
            progress_data: Contains project_id, tasks, and their statuses
        
        Returns:
            Progress report
        """
        self.log_action("Tracking project progress", {"project_id": progress_data.get("project_id")})
        
        tasks = progress_data.get("tasks", [])
        if not tasks:
            return {
                "progress_percent": 0,
                "completed_tasks": 0,
                "total_tasks": 0,
                "status": "not_started"
            }
        
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        total = len(tasks)
        progress = (completed / total * 100) if total > 0 else 0
        
        # Determine overall status
        if progress == 0:
            status = "not_started"
        elif progress == 100:
            status = "completed"
        elif progress >= 75:
            status = "near_completion"
        elif progress >= 50:
            status = "in_progress"
        else:
            status = "early_stage"
        
        # Calculate estimated completion
        in_progress_tasks = [t for t in tasks if t.get("status") == "running"]
        pending_tasks = [t for t in tasks if t.get("status") == "pending"]
        
        estimated_hours_remaining = sum(
            t.get("duration_hours", 0) for t in pending_tasks + in_progress_tasks
        )
        
        return {
            "progress_percent": round(progress, 2),
            "completed_tasks": completed,
            "total_tasks": total,
            "in_progress_tasks": len(in_progress_tasks),
            "pending_tasks": len(pending_tasks),
            "status": status,
            "estimated_hours_remaining": estimated_hours_remaining,
            "tasks": tasks
        }
    
    def manage_dependencies(
        self,
        dependency_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Manage task dependencies and determine execution order
        
        Args:
            dependency_data: Contains tasks with dependencies
        
        Returns:
            Execution plan with dependency resolution
        """
        self.log_action("Managing task dependencies")
        
        tasks = dependency_data.get("tasks", [])
        if not tasks:
            return {"execution_order": [], "ready_tasks": []}
        
        # Build dependency graph
        task_map = {t["id"]: t for t in tasks}
        dependencies = {t["id"]: set(t.get("dependencies", [])) for t in tasks}
        
        # Topological sort to determine execution order
        execution_order = []
        ready_tasks = []
        completed = set()
        
        # Find tasks with no dependencies
        for task_id, deps in dependencies.items():
            if not deps:
                ready_tasks.append(task_id)
        
        # Process tasks
        while ready_tasks:
            task_id = ready_tasks.pop(0)
            execution_order.append(task_id)
            completed.add(task_id)
            
            # Check if any other tasks can now run
            for other_id, deps in dependencies.items():
                if other_id not in completed and deps.issubset(completed):
                    if other_id not in ready_tasks:
                        ready_tasks.append(other_id)
        
        # Check for circular dependencies
        if len(execution_order) < len(tasks):
            remaining = set(task_map.keys()) - set(execution_order)
            self.logger.warning(f"Possible circular dependencies detected: {remaining}")
        
        return {
            "execution_order": execution_order,
            "ready_tasks": [t for t in execution_order if t not in completed or t in ready_tasks],
            "blocked_tasks": list(set(task_map.keys()) - set(execution_order)),
            "dependency_graph": {k: list(v) for k, v in dependencies.items()}
        }
    
    def check_deadlines(
        self,
        deadline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check project deadlines and alert on risks
        
        Args:
            deadline_data: Contains project deadline, tasks, and progress
        
        Returns:
            Deadline analysis with alerts
        """
        self.log_action("Checking project deadlines")
        
        deadline_str = deadline_data.get("deadline")
        tasks = deadline_data.get("tasks", [])
        current_progress = deadline_data.get("progress_percent", 0)
        
        if not deadline_str:
            # Use default deadline
            deadline = datetime.utcnow() + timedelta(days=self.default_deadline_days)
        else:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
            except:
                deadline = datetime.utcnow() + timedelta(days=self.default_deadline_days)
        
        now = datetime.utcnow()
        time_remaining = deadline - now
        days_remaining = time_remaining.total_seconds() / 86400
        
        # Calculate required progress rate
        progress_needed = 100 - current_progress
        if days_remaining > 0:
            daily_progress_needed = progress_needed / days_remaining
        else:
            daily_progress_needed = float('inf')
        
        # Determine risk level
        if days_remaining < 0:
            risk_level = "critical"
            alert = "Deadline has passed!"
        elif days_remaining < 3:
            risk_level = "high"
            alert = "Deadline is very close"
        elif days_remaining < 7:
            risk_level = "medium"
            alert = "Deadline approaching"
        elif daily_progress_needed > 10:
            risk_level = "medium"
            alert = "Progress rate may be insufficient"
        else:
            risk_level = "low"
            alert = "On track"
        
        # Estimate completion based on current rate
        if current_progress > 0:
            elapsed_days = deadline_data.get("elapsed_days", 1)
            if elapsed_days > 0:
                current_rate = current_progress / elapsed_days
                if current_rate > 0:
                    estimated_completion_days = progress_needed / current_rate
                    estimated_completion = now + timedelta(days=estimated_completion_days)
                else:
                    estimated_completion = None
            else:
                estimated_completion = None
        else:
            estimated_completion = None
        
        return {
            "deadline": deadline.isoformat(),
            "days_remaining": round(days_remaining, 1),
            "current_progress": current_progress,
            "progress_needed": progress_needed,
            "daily_progress_needed": round(daily_progress_needed, 2),
            "risk_level": risk_level,
            "alert": alert,
            "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
            "on_track": risk_level in ["low", "medium"] and days_remaining > 0
        }
    
    def allocate_resources(
        self,
        resource_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Allocate resources and agents to tasks
        
        Args:
            resource_data: Contains tasks and available resources
        
        Returns:
            Resource allocation plan
        """
        self.log_action("Allocating resources to tasks")
        
        tasks = resource_data.get("tasks", [])
        available_agents = resource_data.get("available_agents", [])
        max_concurrent = resource_data.get("max_concurrent", self.max_concurrent_tasks)
        
        # Simple allocation: assign agents based on task type
        allocation = {}
        agent_usage = {agent: 0 for agent in available_agents}
        
        for task in tasks:
            task_id = task["id"]
            task_type = task.get("type", "general")
            
            # Find best agent for task type
            assigned_agent = None
            for agent in available_agents:
                if task_type in agent.lower() or "general" in agent.lower():
                    if agent_usage[agent] < max_concurrent:
                        assigned_agent = agent
                        agent_usage[agent] += 1
                        break
            
            if not assigned_agent:
                # Assign to least used agent
                assigned_agent = min(agent_usage.items(), key=lambda x: x[1])[0]
                agent_usage[assigned_agent] += 1
            
            allocation[task_id] = {
                "assigned_agent": assigned_agent,
                "priority": task.get("priority", "medium"),
                "estimated_start": None,  # Would be calculated based on dependencies
                "estimated_duration": task.get("duration_hours", 0)
            }
        
        return {
            "allocation": allocation,
            "agent_usage": agent_usage,
            "utilization": {
                agent: (count / max_concurrent * 100) if max_concurrent > 0 else 0
                for agent, count in agent_usage.items()
            }
        }

