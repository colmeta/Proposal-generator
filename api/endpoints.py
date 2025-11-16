"""
Flask REST API endpoints for job management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional
import logging

from database.db import get_session, init_db
from database.models import Job, Project
from workers.task_worker import TaskWorker, execute_task_async
from services.background_processor import background_processor
from core.workflow_orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize components
orchestrator = WorkflowOrchestrator()
task_worker = TaskWorker(orchestrator)


def initialize():
    """Initialize database and background processor"""
    try:
        init_db()
        background_processor.start()
        logger.info("API initialized")
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")

# Initialize on module import
initialize()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "proposal-generator-api"
    }), 200


@app.route('/api/jobs', methods=['POST'])
def create_job():
    """
    Create a new job
    
    Request body:
    {
        "project_id": int,
        "task_type": str,
        "input_data": dict (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        project_id = data.get("project_id")
        task_type = data.get("task_type")
        input_data = data.get("input_data")
        
        if not project_id or not task_type:
            return jsonify({
                "error": "project_id and task_type are required"
            }), 400
        
        # Verify project exists
        db = get_session()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return jsonify({"error": f"Project {project_id} not found"}), 404
            
            # Create job using orchestrator
            job = orchestrator.create_job(
                project_id=project_id,
                task_type=task_type,
                input_data=input_data
            )
            
            # Schedule async execution
            execute_task_async(job.id, input_data)
            
            return jsonify({
                "job_id": job.id,
                "status": job.status,
                "task_type": job.task_type,
                "created_at": job.created_at.isoformat() if job.created_at else None
            }), 201
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_status(job_id: int):
    """
    Get job status
    
    Returns:
    {
        "id": int,
        "project_id": int,
        "task_type": str,
        "status": str,
        "result": dict (optional),
        "error": str (optional),
        "created_at": str,
        "completed_at": str (optional)
    }
    """
    try:
        db = get_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return jsonify({"error": f"Job {job_id} not found"}), 404
            
            return jsonify(job.to_dict()), 200
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/jobs/<int:job_id>/result', methods=['GET'])
def get_job_result(job_id: int):
    """
    Get job result
    
    Returns the result data if job is completed
    """
    try:
        db = get_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return jsonify({"error": f"Job {job_id} not found"}), 404
            
            if job.status != "completed":
                return jsonify({
                    "error": f"Job is not completed. Current status: {job.status}"
                }), 400
            
            return jsonify({
                "job_id": job.id,
                "status": job.status,
                "result": job.result
            }), 200
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error getting job result: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/jobs/<int:job_id>/cancel', methods=['POST'])
def cancel_job(job_id: int):
    """
    Cancel a job
    
    Returns:
    {
        "job_id": int,
        "cancelled": bool,
        "message": str
    }
    """
    try:
        cancelled = task_worker.cancel_task(job_id)
        
        if cancelled:
            return jsonify({
                "job_id": job_id,
                "cancelled": True,
                "message": "Job cancelled successfully"
            }), 200
        else:
            return jsonify({
                "job_id": job_id,
                "cancelled": False,
                "message": "Job not found or cannot be cancelled"
            }), 400
    
    except Exception as e:
        logger.error(f"Error cancelling job: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """
    List all jobs (with optional filters)
    
    Query parameters:
    - project_id: Filter by project ID
    - status: Filter by status (pending, running, completed, failed, cancelled)
    - task_type: Filter by task type
    - limit: Maximum number of results (default: 100)
    - offset: Offset for pagination (default: 0)
    """
    try:
        # Get query parameters
        project_id = request.args.get('project_id', type=int)
        status = request.args.get('status')
        task_type = request.args.get('task_type')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        db = get_session()
        try:
            query = db.query(Job)
            
            # Apply filters
            if project_id:
                query = query.filter(Job.project_id == project_id)
            if status:
                query = query.filter(Job.status == status)
            if task_type:
                query = query.filter(Job.task_type == task_type)
            
            # Order by created_at descending
            query = query.order_by(Job.created_at.desc())
            
            # Apply pagination
            total = query.count()
            jobs = query.offset(offset).limit(limit).all()
            
            return jsonify({
                "jobs": [job.to_dict() for job in jobs],
                "total": total,
                "limit": limit,
                "offset": offset
            }), 200
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/projects/<int:project_id>/jobs', methods=['GET'])
def get_project_jobs(project_id: int):
    """
    Get all jobs for a specific project
    
    Returns list of jobs for the project
    """
    try:
        jobs = orchestrator.get_project_jobs(project_id)
        return jsonify({"jobs": jobs}), 200
    
    except Exception as e:
        logger.error(f"Error getting project jobs: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start background processor
    background_processor.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

