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
        
        # Data Science & Visualization - Create executive presentation
        from agents.data_science.visualization_agent import DataVisualizationAgent
        viz_agent = DataVisualizationAgent()
        presentation = viz_agent.create_executive_presentation(
            proposal_data={
                **writer_result.get("proposal", {}),
                **extracted_info
            },
            opportunity_type="funding",
            presentation_style="executive"
        )
        
        # CEO review with screening pass
        final_approval = ceo.final_approval_with_screening(
            proposal=writer_result.get("proposal", {}),
            funder_info=funder_info,
            requirements=funder_info.get("requirements", {})
        )
        
        if not final_approval.get("approved"):
            logger.warning(f"Proposal not approved: {final_approval.get('ceo_review', {}).get('feedback')}")
            # Still return proposal but with review feedback
        
        return {
            "status": "success",
            "proposal": writer_result.get("proposal", {}),
            "executive_presentation": presentation,
            "visualizations": presentation.get("visualizations", []),
            "data_insights": presentation.get("insights", []),
            "ceo_review": final_approval.get("ceo_review", {}),
            "screening_result": final_approval.get("screening_result", {}),
            "ready_for_submission": final_approval.get("ready_for_submission", False),
            "next_steps": final_approval.get("next_steps", []),
            "funder": funder_name,
            "knowledge_base_used": True
        }
    
    except Exception as e:
        logger.error(f"Error generating auto proposal: {e}")
        raise

