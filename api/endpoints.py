"""
Flask REST API endpoints for job management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app FIRST - before any other imports
app = Flask(__name__)
application = app  # Alias for WSGI servers like gunicorn
CORS(app)  # Enable CORS for all routes

logger.info("Flask app created successfully")

# Lazy-loaded modules - will be imported only when needed
_db_module = None
_background_processor = None
_orchestrator = None
_document_processor = None
_website_scraper = None
_knowledge_base = None
_enhanced_kb = None

def get_db_module():
    """Lazy load database module"""
    global _db_module
    if _db_module is None:
        try:
            from database import db, models
            _db_module = {'db': db, 'models': models}
            logger.info("Database modules loaded")
        except Exception as e:
            logger.error(f"Failed to load database modules: {e}")
            _db_module = {}
    return _db_module

def get_background_processor():
    """Lazy load background processor"""
    global _background_processor
    if _background_processor is None:
        try:
            from services.background_processor import background_processor
            _background_processor = background_processor
            logger.info("Background processor loaded")
        except Exception as e:
            logger.error(f"Failed to load background processor: {e}")
    return _background_processor

def get_orchestrator():
    """Lazy load orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        try:
            from core.workflow_orchestrator import WorkflowOrchestrator
            _orchestrator = WorkflowOrchestrator()
            logger.info("Orchestrator loaded")
        except Exception as e:
            logger.error(f"Failed to load orchestrator: {e}")
    return _orchestrator

def get_document_processor():
    """Lazy load document processor"""
    global _document_processor
    if _document_processor is None:
        try:
            from services.document_processor import document_processor
            _document_processor = document_processor
            logger.info("Document processor loaded")
        except Exception as e:
            logger.error(f"Failed to load document processor: {e}")
    return _document_processor

def get_website_scraper():
    """Lazy load website scraper"""
    global _website_scraper
    if _website_scraper is None:
        try:
            from services.website_scraper import website_scraper
            _website_scraper = website_scraper
            logger.info("Website scraper loaded")
        except Exception as e:
            logger.error(f"Failed to load website scraper: {e}")
    return _website_scraper

def get_knowledge_base():
    """Lazy load knowledge base"""
    global _knowledge_base
    if _knowledge_base is None:
        try:
            from services.knowledge_base import knowledge_base
            _knowledge_base = knowledge_base
            logger.info("Knowledge base loaded")
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
    return _knowledge_base

def get_enhanced_kb():
    """Lazy load enhanced knowledge base"""
    global _enhanced_kb
    if _enhanced_kb is None:
        try:
            from services.knowledge_base_enhanced import EnhancedKnowledgeBase
            _enhanced_kb = EnhancedKnowledgeBase()
            logger.info("Enhanced knowledge base loaded")
        except Exception as e:
            logger.error(f"Failed to load enhanced knowledge base: {e}")
    return _enhanced_kb

# Track initialization status
_initialized = False

def _initialize_app():
    """Initialize database only - skip background processor for now"""
    global _initialized
    if _initialized:
        return
    
    logger.info("Starting lightweight app initialization...")
    
    try:
        db_module = get_db_module()
        if db_module and 'db' in db_module:
            init_db = getattr(db_module['db'], 'init_db', None)
            if init_db:
                logger.info("Initializing database...")
                init_db()
                logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    
    # DON'T start background processor on initialization
    # It will be started manually via separate endpoint if needed
    logger.info("Skipping background processor (start manually via /api/admin/start-processor)")
    
    _initialized = True
    logger.info("API initialized successfully")

# Initialize immediately but only database
logger.info("Starting immediate initialization (database only)...")
_initialize_app()
logger.info("Immediate initialization complete")

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "proposal-generator-api",
        "status": "running",
        "version": "1.0.0"
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "proposal-generator-api",
        "initialized": _initialized
    }), 200

@app.route('/api/admin/start-processor', methods=['POST'])
def start_background_processor():
    """Manually start background processor (admin only)"""
    try:
        if os.environ.get('BACKGROUND_PROCESSING_ENABLED', 'false').lower() != 'true':
            return jsonify({
                "status": "disabled",
                "message": "Background processing is disabled"
            }), 400
        
        processor = get_background_processor()
        if processor:
            processor.start()
            return jsonify({
                "status": "success",
                "message": "Background processor started"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Background processor not available"
            }), 500
    except Exception as e:
        logger.error(f"Error starting background processor: {e}")
        return jsonify({"error": str(e)}), 500

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
        
        # Get database session
        db_module = get_db_module()
        if not db_module or 'db' not in db_module:
            return jsonify({"error": "Database not available"}), 503
        
        get_session = db_module['db'].get_session
        Job = db_module['models'].Job
        Project = db_module['models'].Project
        
        orchestrator = get_orchestrator()
        if not orchestrator:
            return jsonify({"error": "Orchestrator not available"}), 503
        
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
            
            # Execute async (if available)
            try:
                from workers.task_worker import execute_task_async
                execute_task_async(job.id, input_data)
            except ImportError:
                logger.warning("Task worker not available, job will remain pending")
            
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
    """Get job status"""
    try:
        db_module = get_db_module()
        if not db_module or 'db' not in db_module:
            return jsonify({"error": "Database not available"}), 503
        
        get_session = db_module['db'].get_session
        Job = db_module['models'].Job
        
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
        
        # Get document processor
        doc_processor = get_document_processor()
        if not doc_processor:
            return jsonify({"error": "Document processor not available"}), 503
        
        # Process document
        logger.info(f"Processing document: {filename} (type: {document_type})")
        processed = doc_processor.process_document(
            file_content=file_content,
            filename=filename,
            file_type=file_type
        )
        
        # Extract structured information
        structured_info = doc_processor.extract_structured_info(
            text=processed['text'],
            document_type=document_type
        )
        
        # Store in knowledge base
        enhanced_kb = get_enhanced_kb()
        if enhanced_kb:
            enhanced_kb.add_cross_silo_document(
                content=processed['text'],
                metadata={
                    "filename": filename,
                    "file_type": file_type,
                    "document_type": document_type,
                    "user_id": user_id,
                    "char_count": processed.get('char_count', 0),
                    "word_count": processed.get('word_count', 0),
                    "structured_info": structured_info
                },
                document_id=f"{user_id}_{filename}",
                silo_type=document_type
            )
        
        return jsonify({
            "status": "success",
            "message": "Document processed and stored",
            "document": {
                "filename": filename,
                "file_type": file_type,
                "char_count": processed.get('char_count', 0),
                "word_count": processed.get('word_count', 0),
                "structured_info": structured_info
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({"error": str(e)}), 500

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
        
        kb = get_knowledge_base()
        if not kb:
            return jsonify({"error": "Knowledge base not available"}), 503
        
        results = kb.search(
            query=query,
            n_results=n_results,
            filter_metadata={"user_id": user_id} if user_id != "default" else None
        )
        
        return jsonify({
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
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

# Entry point for direct execution
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
