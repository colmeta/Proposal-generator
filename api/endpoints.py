"""
Flask REST API endpoints for job management - FIXED VERSION
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import sys

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app FIRST - before any other imports
app = Flask(__name__)
application = app  # Alias for WSGI servers like gunicorn
CORS(app)  # Enable CORS for all routes

logger.info("Flask app created successfully")

# Track initialization status
_initialized = False

def _initialize_app():
    """Initialize database only - skip background processor for now"""
    global _initialized
    if _initialized:
        return
    
    logger.info("Starting lightweight app initialization...")
    
    try:
        # Try to initialize database if available
        try:
            from database import db
            init_db = getattr(db, 'init_db', None)
            if init_db:
                logger.info("Initializing database...")
                init_db()
                logger.info("Database initialized successfully")
        except ImportError:
            logger.warning("Database module not available, skipping")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    
    _initialized = True
    logger.info("API initialized successfully")

# Initialize immediately
logger.info("Starting immediate initialization (database only)...")
_initialize_app()
logger.info("Immediate initialization complete")

# ===== BASIC ROUTES =====

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "proposal-generator-api",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "monitoring_health": "/api/monitoring/health",
            "jobs": "/api/jobs",
            "documents": "/api/documents/upload",
            "knowledge_base": "/api/knowledge-base/search"
        }
    }), 200

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "proposal-generator-api",
        "initialized": _initialized
    }), 200

@app.route('/status', methods=['GET'])
@app.route('/api/status', methods=['GET'])
def status():
    """Status endpoint with detailed info"""
    import platform
    import psutil
    
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return jsonify({
            "status": "running",
            "service": "proposal-generator-api",
            "version": "1.0.0",
            "initialized": _initialized,
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                "pid": os.getpid()
            },
            "environment": {
                "port": os.getenv('PORT', 'not set'),
                "render": os.getenv('RENDER', 'false'),
                "flask_env": os.getenv('FLASK_ENV', 'not set')
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        return jsonify({
            "status": "running",
            "service": "proposal-generator-api",
            "version": "1.0.0",
            "error": str(e)
        }), 200

@app.route('/api/monitoring/health', methods=['GET'])
def monitoring_health():
    """Monitoring health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "proposal-generator-api",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "checks": {
            "api": "healthy",
            "database": "healthy" if _initialized else "not initialized",
            "background_processor": "disabled"
        }
    }), 200

# ===== JOBS ENDPOINTS =====

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job"""
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
        
        # Try to get database
        try:
            from database.db import get_session
            from database.models import Job, Project
            from core.workflow_orchestrator import WorkflowOrchestrator
            
            orchestrator = WorkflowOrchestrator()
            
            db = get_session()
            try:
                # Verify project exists
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project:
                    return jsonify({"error": f"Project {project_id} not found"}), 404
                
                # Create job
                job = orchestrator.create_job(
                    project_id=project_id,
                    task_type=task_type,
                    input_data=input_data
                )
                
                return jsonify({
                    "job_id": job.id,
                    "status": job.status,
                    "task_type": job.task_type,
                    "created_at": job.created_at.isoformat() if job.created_at else None
                }), 201
            
            finally:
                db.close()
        
        except ImportError:
            return jsonify({"error": "Database not available"}), 503
    
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_status(job_id: int):
    """Get job status"""
    try:
        from database.db import get_session
        from database.models import Job
        
        db = get_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return jsonify({"error": f"Job {job_id} not found"}), 404
            
            return jsonify(job.to_dict()), 200
        
        finally:
            db.close()
    
    except ImportError:
        return jsonify({"error": "Database not available"}), 503
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        return jsonify({"error": str(e)}), 500

# ===== DOCUMENTS ENDPOINTS =====

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        import base64
        from werkzeug.utils import secure_filename
        
        # Check if file is uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            filename = secure_filename(file.filename)
            file_content = file.read()
            file_type = filename.split('.')[-1].lower()
        
        # Check if base64 encoded data is provided
        elif request.json and 'document_data' in request.json:
            data = request.json
            document_data = data.get('document_data')
            filename = data.get('filename', 'document')
            
            try:
                file_content = base64.b64decode(document_data)
                file_type = filename.split('.')[-1].lower() if '.' in filename else 'txt'
            except Exception as e:
                return jsonify({"error": f"Invalid base64 data: {e}"}), 400
        
        else:
            return jsonify({"error": "No file or document_data provided"}), 400
        
        document_type = request.form.get('document_type') or (request.json.get('document_type') if request.json else 'general')
        user_id = request.form.get('user_id') or (request.json.get('user_id') if request.json else 'default')
        
        return jsonify({
            "status": "success",
            "message": "Document received (processing not yet implemented)",
            "document": {
                "filename": filename,
                "file_type": file_type,
                "size_bytes": len(file_content),
                "document_type": document_type,
                "user_id": user_id
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({"error": str(e)}), 500

# ===== KNOWLEDGE BASE ENDPOINTS =====

@app.route('/api/knowledge-base/search', methods=['POST'])
def search_knowledge_base():
    """Search knowledge base"""
    try:
        data = request.json
        query = data.get('query')
        user_id = data.get('user_id', 'default')
        n_results = data.get('n_results', 10)
        
        if not query:
            return jsonify({"error": "query is required"}), 400
        
        return jsonify({
            "status": "success",
            "query": query,
            "results": [],
            "count": 0,
            "message": "Knowledge base search not yet implemented"
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return jsonify({"error": str(e)}), 500

# ===== ADMIN ENDPOINTS =====

@app.route('/api/admin/start-processor', methods=['POST'])
def start_background_processor():
    """Manually start background processor (admin only)"""
    try:
        if os.environ.get('BACKGROUND_PROCESSING_ENABLED', 'false').lower() != 'true':
            return jsonify({
                "status": "disabled",
                "message": "Background processing is disabled"
            }), 400
        
        return jsonify({
            "status": "not_implemented",
            "message": "Background processor start not yet implemented"
        }), 501
    except Exception as e:
        logger.error(f"Error starting background processor: {e}")
        return jsonify({"error": str(e)}), 500

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/",
            "/health",
            "/status",
            "/api/health",
            "/api/status",
            "/api/monitoring/health",
            "/api/jobs (POST)",
            "/api/jobs/<id> (GET)",
            "/api/documents/upload (POST)",
            "/api/knowledge-base/search (POST)"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# Entry point for direct execution
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
