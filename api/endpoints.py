"""
Flask REST API endpoints for job management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional
import logging
import base64
from werkzeug.utils import secure_filename

from database.db import get_session, init_db
from database.models import Job, Project
from workers.task_worker import TaskWorker, execute_task_async
from services.background_processor import background_processor
from core.workflow_orchestrator import WorkflowOrchestrator
from services.document_processor import document_processor
from services.website_scraper import website_scraper
from services.knowledge_base import knowledge_base

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


@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """
    Upload and process a document (PDF, DOCX, images, text)
    Extracts information and stores in knowledge base
    
    Accepts:
    - file: File upload (multipart/form-data)
    - OR document_data: Base64 encoded file with filename
    - document_type: Type of document (project_report, team_profile, budget, etc.)
    - user_id: User ID (optional)
    """
    try:
        # Check if file is uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            filename = secure_filename(file.filename)
            file_content = file.read()
            file_type = filename.split('.')[-1].lower()
        
        # Check if base64 encoded data is provided
        elif 'document_data' in request.json:
            data = request.json
            document_data = data.get('document_data')
            filename = data.get('filename', 'document')
            
            try:
                # Decode base64
                file_content = base64.b64decode(document_data)
                file_type = filename.split('.')[-1].lower() if '.' in filename else 'txt'
            except Exception as e:
                return jsonify({"error": f"Invalid base64 data: {e}"}), 400
        
        else:
            return jsonify({"error": "No file or document_data provided"}), 400
        
        # Get document type
        document_type = request.form.get('document_type') or request.json.get('document_type', 'general')
        user_id = request.form.get('user_id') or request.json.get('user_id', 'default')
        
        # Process document
        logger.info(f"Processing document: {filename} (type: {document_type})")
        processed = document_processor.process_document(
            file_content=file_content,
            filename=filename,
            file_type=file_type
        )
        
        # Extract structured information
        structured_info = document_processor.extract_structured_info(
            text=processed['text'],
            document_type=document_type
        )
        
        # Store in knowledge base
        knowledge_base.add_document(
            document_id=f"{user_id}_{filename}",
            content=processed['text'],
            metadata={
                "filename": filename,
                "file_type": file_type,
                "document_type": document_type,
                "user_id": user_id,
                "char_count": processed.get('char_count', 0),
                "word_count": processed.get('word_count', 0),
                "structured_info": structured_info
            }
        )
        
        return jsonify({
            "status": "success",
            "message": "Document processed and stored in knowledge base",
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


@app.route('/api/documents/upload-urls', methods=['POST'])
def upload_urls():
    """
    Scrape and process content from URLs (websites, social media)
    Extracts information and stores in knowledge base
    
    Body:
    {
        "urls": ["https://example.com", "https://linkedin.com/company/..."],
        "user_id": "user123",
        "extract_structured": true
    }
    """
    try:
        data = request.json
        urls = data.get('urls', [])
        user_id = data.get('user_id', 'default')
        extract_structured = data.get('extract_structured', True)
        
        if not urls:
            return jsonify({"error": "No URLs provided"}), 400
        
        results = []
        for url in urls:
            try:
                logger.info(f"Scraping URL: {url}")
                scraped = website_scraper.scrape_url(url, extract_structured=extract_structured)
                
                if scraped.get('success'):
                    # Store in knowledge base
                    knowledge_base.add_document(
                        document_id=f"{user_id}_{url}",
                        content=scraped.get('text', ''),
                        metadata={
                            "url": url,
                            "platform": scraped.get('platform', 'website'),
                            "title": scraped.get('title'),
                            "user_id": user_id,
                            "structured_info": scraped.get('structured_info', {})
                        }
                    )
                    
                    results.append({
                        "url": url,
                        "status": "success",
                        "platform": scraped.get('platform'),
                        "title": scraped.get('title'),
                        "text_length": len(scraped.get('text', ''))
                    })
                else:
                    results.append({
                        "url": url,
                        "status": "error",
                        "error": scraped.get('error', 'Unknown error')
                    })
            
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e)
                })
        
        return jsonify({
            "status": "success",
            "message": f"Processed {len([r for r in results if r['status'] == 'success'])} URLs",
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing URLs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/proposals/generate-auto', methods=['POST'])
def generate_proposal_auto():
    """
    Automatically generate proposal using knowledge base
    Minimal user input required - system uses uploaded documents
    
    Body:
    {
        "funder_name": "National Science Foundation",
        "funder_website": "https://www.nsf.gov" (optional),
        "user_id": "user123",
        "project_focus": "Education technology" (optional),
        "budget_amount": 500000 (optional),
        "additional_requirements": {} (optional)
    }
    """
    try:
        data = request.json
        funder_name = data.get('funder_name')
        user_id = data.get('user_id', 'default')
        
        if not funder_name:
            return jsonify({"error": "funder_name is required"}), 400
        
        # Retrieve information from knowledge base
        logger.info(f"Generating auto proposal for {funder_name} using knowledge base")
        
        # Search knowledge base for relevant information
        query = f"projects activities team budget {data.get('project_focus', '')}"
        kb_results = knowledge_base.search(
            query=query,
            n_results=10,
            filter_metadata={"user_id": user_id} if user_id != "default" else None
        )
        
        # Extract information from knowledge base
        extracted_info = {
            "projects": [],
            "team": [],
            "activities": [],
            "budget": {},
            "organizational_info": {}
        }
        
        for result in kb_results:
            metadata = result.get('metadata', {})
            structured = metadata.get('structured_info', {})
            
            if 'projects' in structured:
                extracted_info['projects'].extend(structured['projects'])
            if 'team_members' in structured:
                extracted_info['team'].extend(structured['team_members'])
            if 'activities' in structured:
                extracted_info['activities'].extend(structured['activities'])
            if 'budget_items' in structured:
                extracted_info['budget'].update(structured)
        
        # Research funder
        from agents.research.funder_intelligence import FunderIntelligenceAgent
        funder_agent = FunderIntelligenceAgent()
        funder_info = funder_agent.research_funder(
            funder_name=funder_name,
            website=data.get('funder_website'),
            deep_research=True
        )
        
        # Create proposal generation job
        job_data = {
            "task_type": "generate_proposal_auto",
            "input_data": {
                "funder_name": funder_name,
                "funder_info": funder_info,
                "user_id": user_id,
                "extracted_info": extracted_info,
                "project_focus": data.get('project_focus'),
                "budget_amount": data.get('budget_amount'),
                "additional_requirements": data.get('additional_requirements', {})
            }
        }
        
        # Create job in database
        db = get_session()
        try:
            job = Job(
                task_type=job_data["task_type"],
                status="pending",
                result=None
            )
            db.add(job)
            db.commit()
            job_id = job.id
            
            # Execute in background
            execute_task_async(job_id, job_data["input_data"])
            
            return jsonify({
                "status": "success",
                "message": "Proposal generation started",
                "job_id": job_id,
                "funder": funder_name,
                "knowledge_base_used": len(kb_results) > 0,
                "info_sources": len(kb_results)
            }), 202
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error generating auto proposal: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/knowledge-base/search', methods=['POST'])
def search_knowledge_base():
    """
    Search knowledge base for information
    
    Body:
    {
        "query": "search query",
        "user_id": "user123",
        "n_results": 10
    }
    """
    try:
        data = request.json
        query = data.get('query')
        user_id = data.get('user_id', 'default')
        n_results = data.get('n_results', 10)
        
        if not query:
            return jsonify({"error": "query is required"}), 400
        
        results = knowledge_base.search(
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


@app.route('/api/knowledge-base/documents', methods=['GET'])
def list_knowledge_base_documents():
    """
    List all documents in knowledge base for a user
    """
    try:
        user_id = request.args.get('user_id', 'default')
        limit = int(request.args.get('limit', 50))
        
        # Get documents from knowledge base
        # Note: This is a simplified version - actual implementation depends on ChromaDB API
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "message": "Knowledge base documents listing"
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/eligibility/check', methods=['POST'])
def check_eligibility():
    """
    Check if user qualifies for a funding opportunity/contract/loan
    
    Body:
    {
        "funder_name": "National Science Foundation",
        "funder_website": "https://www.nsf.gov" (optional),
        "user_id": "user123",
        "opportunity_type": "grant"  // "grant", "contract", "loan"
    }
    """
    try:
        data = request.json
        funder_name = data.get('funder_name')
        user_id = data.get('user_id', 'default')
        opportunity_type = data.get('opportunity_type', 'grant')
        
        if not funder_name:
            return jsonify({"error": "funder_name is required"}), 400
        
        # Research funder
        from agents.research.funder_intelligence import FunderIntelligenceAgent
        funder_agent = FunderIntelligenceAgent()
        funder_info = funder_agent.research_funder(
            funder_name=funder_name,
            website=data.get('funder_website'),
            deep_research=True
        )
        
        # Get user profile from knowledge base
        user_profile_query = "organization profile team projects budget experience"
        kb_results = knowledge_base.search(
            query=user_profile_query,
            n_results=10,
            filter_metadata={"user_id": user_id} if user_id != "default" else None
        )
        
        # Build user profile from knowledge base
        user_profile = {
            "organization_type": "organization",  # Could be extracted from KB
            "projects": [],
            "team": [],
            "budget": {},
            "experience": [],
            "focus_areas": []
        }
        
        knowledge_base_data = {}
        for result in kb_results:
            metadata = result.get('metadata', {})
            structured = metadata.get('structured_info', {})
            
            if 'projects' in structured:
                user_profile['projects'].extend(structured['projects'])
            if 'team_members' in structured:
                user_profile['team'].extend(structured['team_members'])
            if 'budget_items' in structured:
                user_profile['budget'].update(structured)
            if 'activities' in structured:
                user_profile['experience'].extend(structured.get('activities', []))
        
        # Assess eligibility
        from agents.eligibility_assessor import EligibilityAssessorAgent
        assessor = EligibilityAssessorAgent()
        
        assessment = assessor.assess_eligibility(
            funder_info=funder_info,
            user_profile=user_profile,
            knowledge_base_data=knowledge_base_data
        )
        
        return jsonify({
            "status": "success",
            "funder": funder_name,
            "opportunity_type": opportunity_type,
            "assessment": assessment
        }), 200
    
    except Exception as e:
        logger.error(f"Error checking eligibility: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/proposals/screen', methods=['POST'])
def screen_proposal():
    """
    Screen proposal to ensure it passes funder screening before delivery
    
    Body:
    {
        "proposal": {...},  // Proposal document
        "funder_name": "National Science Foundation",
        "job_id": 123  // Optional: job ID if screening existing proposal
    }
    """
    try:
        data = request.json
        proposal = data.get('proposal')
        funder_name = data.get('funder_name')
        job_id = data.get('job_id')
        
        # If job_id provided, get proposal from job
        if job_id and not proposal:
            db = get_session()
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job and job.result:
                    import json
                    if isinstance(job.result, str):
                        job_result = json.loads(job.result)
                    else:
                        job_result = job.result
                    proposal = job_result.get("proposal", {})
            finally:
                db.close()
        
        if not proposal:
            return jsonify({"error": "proposal is required"}), 400
        
        if not funder_name:
            return jsonify({"error": "funder_name is required"}), 400
        
        # Get funder info
        from agents.research.funder_intelligence import FunderIntelligenceAgent
        funder_agent = FunderIntelligenceAgent()
        funder_info = funder_agent.get_funder_info(funder_name)
        
        if not funder_info:
            funder_info = funder_agent.research_funder(funder_name, deep_research=False)
        
        # Screen proposal
        from agents.screening_pass_agent import ScreeningPassAgent
        screening_agent = ScreeningPassAgent()
        
        screening_result = screening_agent.screen_proposal(
            proposal=proposal,
            funder_info=funder_info,
            requirements=funder_info.get("requirements", {})
        )
        
        return jsonify({
            "status": "success",
            "funder": funder_name,
            "screening_result": screening_result,
            "ready_for_submission": screening_result["will_pass"]
        }), 200
    
    except Exception as e:
        logger.error(f"Error screening proposal: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/eligibility/compare', methods=['POST'])
def compare_opportunities():
    """
    Compare multiple funding opportunities and rank by eligibility
    
    Body:
    {
        "opportunities": [
            {"name": "NSF", "website": "https://www.nsf.gov"},
            {"name": "NIH", "website": "https://www.nih.gov"}
        ],
        "user_id": "user123"
    }
    """
    try:
        data = request.json
        opportunities_data = data.get('opportunities', [])
        user_id = data.get('user_id', 'default')
        
        if not opportunities_data:
            return jsonify({"error": "opportunities list is required"}), 400
        
        # Research all opportunities
        from agents.research.funder_intelligence import FunderIntelligenceAgent
        funder_agent = FunderIntelligenceAgent()
        
        opportunities = []
        for opp in opportunities_data:
            funder_info = funder_agent.research_funder(
                funder_name=opp.get('name'),
                website=opp.get('website'),
                deep_research=False  # Faster for comparison
            )
            opportunities.append(funder_info)
        
        # Get user profile
        user_profile_query = "organization profile team projects"
        kb_results = knowledge_base.search(
            query=user_profile_query,
            n_results=5,
            filter_metadata={"user_id": user_id} if user_id != "default" else None
        )
        
        user_profile = {"projects": [], "team": [], "budget": {}}
        for result in kb_results:
            structured = result.get('metadata', {}).get('structured_info', {})
            if 'projects' in structured:
                user_profile['projects'].extend(structured['projects'])
            if 'team_members' in structured:
                user_profile['team'].extend(structured['team_members'])
        
        # Compare opportunities
        from agents.eligibility_assessor import EligibilityAssessorAgent
        assessor = EligibilityAssessorAgent()
        
        comparison = assessor.compare_opportunities(
            opportunities=opportunities,
            user_profile=user_profile
        )
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "comparison": comparison,
            "top_opportunity": comparison[0] if comparison else None
        }), 200
    
    except Exception as e:
        logger.error(f"Error comparing opportunities: {e}")
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
    
    # Get port from environment (Render sets PORT)
    import os
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

