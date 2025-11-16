"""
Background Processor Service
APScheduler-based task queue management for Render-compatible background processing
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging
import atexit
import threading

from database.db import get_session
from database.models import Job

logger = logging.getLogger(__name__)


class BackgroundProcessor:
    """
    Background task processor using APScheduler
    Render-compatible (no Redis needed)
    """
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize background processor
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.scheduler = None
        self.job_callbacks: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._started = False
        
    def start(self):
        """Start the scheduler"""
        if self._started:
            logger.warning("Background processor already started")
            return
        
        with self._lock:
            if self._started:
                return
            
            # Configure job stores and executors
            jobstores = {
                'default': MemoryJobStore()
            }
            
            executors = {
                'default': ThreadPoolExecutor(max_workers=self.max_workers)
            }
            
            job_defaults = {
                'coalesce': True,  # Combine multiple pending jobs into one
                'max_instances': 1,  # Only one instance of a job at a time
                'misfire_grace_time': 300  # 5 minutes grace period
            }
            
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
            
            # Add event listeners
            self.scheduler.add_listener(self._on_job_executed, EVENT_JOB_EXECUTED)
            self.scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
            
            # Start scheduler
            self.scheduler.start()
            self._started = True
            
            # Register shutdown handler
            atexit.register(self.shutdown)
            
            logger.info(f"Background processor started with {self.max_workers} workers")
    
    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler"""
        if not self._started or not self.scheduler:
            return
        
        with self._lock:
            if self.scheduler:
                self.scheduler.shutdown(wait=wait)
                self.scheduler = None
                self._started = False
                logger.info("Background processor shut down")
    
    def add_job(
        self,
        job_id: int,
        func: Callable,
        args: Optional[tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        run_date: Optional[datetime] = None,
        job_type: str = "default"
    ) -> str:
        """
        Add a job to the scheduler
        
        Args:
            job_id: Database job ID
            func: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            run_date: When to run the job (None = immediately)
            job_type: Type of job
        
        Returns:
            APScheduler job ID
        """
        if not self._started:
            self.start()
        
        scheduler_job_id = f"job_{job_id}_{job_type}"
        
        # Store callback for job completion
        self.job_callbacks[scheduler_job_id] = {
            "job_id": job_id,
            "func": func,
            "args": args or (),
            "kwargs": kwargs or {}
        }
        
        # Add job to scheduler
        if run_date:
            self.scheduler.add_job(
                func=func,
                trigger='date',
                run_date=run_date,
                id=scheduler_job_id,
                args=args or (),
                kwargs=kwargs or {},
                replace_existing=True
            )
        else:
            # Run immediately
            self.scheduler.add_job(
                func=func,
                trigger='date',
                run_date=datetime.utcnow(),
                id=scheduler_job_id,
                args=args or (),
                kwargs=kwargs or {},
                replace_existing=True
            )
        
        logger.info(f"Added job {scheduler_job_id} (DB job {job_id}) to scheduler")
        return scheduler_job_id
    
    def remove_job(self, scheduler_job_id: str):
        """
        Remove a job from the scheduler
        
        Args:
            scheduler_job_id: APScheduler job ID
        """
        if not self.scheduler:
            return
        
        try:
            self.scheduler.remove_job(scheduler_job_id)
            if scheduler_job_id in self.job_callbacks:
                del self.job_callbacks[scheduler_job_id]
            logger.info(f"Removed job {scheduler_job_id} from scheduler")
        except Exception as e:
            logger.warning(f"Failed to remove job {scheduler_job_id}: {e}")
    
    def get_job_status(self, scheduler_job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a scheduled job
        
        Args:
            scheduler_job_id: APScheduler job ID
        
        Returns:
            Job status dictionary or None
        """
        if not self.scheduler:
            return None
        
        try:
            job = self.scheduler.get_job(scheduler_job_id)
            if job:
                return {
                    "id": scheduler_job_id,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "pending": job.next_run_time is not None
                }
        except Exception as e:
            logger.warning(f"Failed to get job status for {scheduler_job_id}: {e}")
        
        return None
    
    def list_jobs(self) -> list:
        """
        List all scheduled jobs
        
        Returns:
            List of job dictionaries
        """
        if not self.scheduler:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "func": job.func.__name__ if hasattr(job.func, '__name__') else str(job.func)
            })
        
        return jobs
    
    def _on_job_executed(self, event):
        """Handle job execution completion"""
        job_id = event.job_id
        logger.debug(f"Job {job_id} executed successfully")
        
        # Update database job status if callback exists
        if job_id in self.job_callbacks:
            db_job_id = self.job_callbacks[job_id]["job_id"]
            try:
                db = get_session()
                try:
                    job = db.query(Job).filter(Job.id == db_job_id).first()
                    if job and job.status == "running":
                        # Job completed - status will be updated by task worker
                        pass
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Failed to update job {db_job_id} status: {e}")
    
    def _on_job_error(self, event):
        """Handle job execution error"""
        job_id = event.job_id
        exception = event.exception
        logger.error(f"Job {job_id} failed with error: {exception}")
        
        # Update database job status
        if job_id in self.job_callbacks:
            db_job_id = self.job_callbacks[job_id]["job_id"]
            try:
                db = get_session()
                try:
                    job = db.query(Job).filter(Job.id == db_job_id).first()
                    if job:
                        job.status = "failed"
                        job.error = str(exception)
                        job.completed_at = datetime.utcnow()
                        db.commit()
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Failed to update job {db_job_id} error status: {e}")


# Global instance
background_processor = BackgroundProcessor()

