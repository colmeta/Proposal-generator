"""
Auto Proposal Generation Worker
Handles automatic proposal generation using knowledge base
"""

from typing import Dict, Any
import logging
from core.workflow_orchestrator import WorkflowOrchestrator
from agents.ceo_agent import CEOAgent
from agents.content.master_writer import MasterWriterAgent
from agents.research.funder_intelligence import FunderIntelligenceAgent

logger = logging.getLogger(__name__)


def generate_proposal_from_knowledge_base(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate proposal automatically using knowledge base
    
    Args:
        input_data: Contains funder_name, funder_info, extracted_info, etc.
    
    Returns:
        Generated proposal
    """
    try:
        funder_name = input_data.get("funder_name")
        funder_info = input_data.get("funder_info", {})
        extracted_info = input_data.get("extracted_info", {})
        user_id = input_data.get("user_id", "default")
        
        logger.info(f"Generating auto proposal for {funder_name} (user: {user_id})")
        
        # Initialize agents
        writer = MasterWriterAgent()
        ceo = CEOAgent()
        
        # Build proposal content from extracted info
        proposal_sections = {
            "executive_summary": "",
            "problem_statement": "",
            "solution": "",
            "methodology": "",
            "budget": extracted_info.get("budget", {}),
            "timeline": "",
            "team": extracted_info.get("team", []),
            "impact": "",
            "projects": extracted_info.get("projects", []),
            "activities": extracted_info.get("activities", [])
        }
        
        # Generate proposal using Master Writer
        proposal_data = {
            "funder_info": funder_info,
            "extracted_info": extracted_info,
            "sections": proposal_sections,
            "project_focus": input_data.get("project_focus"),
            "budget_amount": input_data.get("budget_amount")
        }
        
        # Write proposal
        writer_result = writer.process(proposal_data)
        
        # CEO review
        ceo_review = ceo.review_proposal(
            proposal=writer_result.get("proposal", {}),
            requirements=funder_info.get("requirements", {}),
            research_data={"extracted_info": extracted_info}
        )
        
        if not ceo_review.get("approved"):
            logger.warning(f"Proposal not approved: {ceo_review.get('feedback')}")
            # Still return proposal but with review feedback
        
        return {
            "status": "success",
            "proposal": writer_result.get("proposal", {}),
            "ceo_review": ceo_review,
            "funder": funder_name,
            "knowledge_base_used": True
        }
    
    except Exception as e:
        logger.error(f"Error generating auto proposal: {e}")
        raise

