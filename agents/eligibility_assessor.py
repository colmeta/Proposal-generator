"""
Eligibility Assessor Agent
Assesses whether user qualifies for funding/contracts/loans and provides recommendations
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import re
import logging

logger = logging.getLogger(__name__)


class EligibilityAssessorAgent(BaseAgent):
    """
    Eligibility Assessor Agent - Checks qualification for funding/contracts/loans
    """
    
    def __init__(self):
        super().__init__(
            name="Eligibility Assessor Agent",
            role="Assess eligibility for funding opportunities and provide recommendations",
            task_type="strategy"
        )
    
    def assess_eligibility(
        self,
        funder_info: Dict[str, Any],
        user_profile: Dict[str, Any],
        knowledge_base_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess eligibility for a funding opportunity
        
        Args:
            funder_info: Information about the funder/opportunity
            user_profile: User's profile and information
            knowledge_base_data: Additional data from knowledge base
        
        Returns:
            Eligibility assessment with recommendations
        """
        self.log_action("Assessing eligibility for funding opportunity")
        
        # Extract requirements from funder
        requirements = funder_info.get("requirements", {})
        eligibility_criteria = funder_info.get("eligibility_criteria", [])
        focus_areas = funder_info.get("focus_areas", [])
        
        # Use LLM to assess eligibility
        assessment = self._assess_with_llm(
            funder_info=funder_info,
            user_profile=user_profile,
            knowledge_base_data=knowledge_base_data
        )
        
        # Calculate eligibility score
        eligibility_score = self._calculate_eligibility_score(assessment)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            assessment=assessment,
            funder_info=funder_info,
            user_profile=user_profile
        )
        
        result = {
            "eligible": eligibility_score >= 0.7,  # 70% threshold
            "eligibility_score": eligibility_score,
            "assessment": assessment,
            "requirements_met": assessment.get("requirements_met", []),
            "requirements_missing": assessment.get("requirements_missing", []),
            "strengths": assessment.get("strengths", []),
            "weaknesses": assessment.get("weaknesses", []),
            "recommendations": recommendations,
            "qualification_level": self._get_qualification_level(eligibility_score),
            "next_steps": self._get_next_steps(eligibility_score, recommendations)
        }
        
        self.log_action(
            f"Eligibility assessment complete",
            {"eligible": result["eligible"], "score": eligibility_score}
        )
        
        return result
    
    def _assess_with_llm(
        self,
        funder_info: Dict[str, Any],
        user_profile: Dict[str, Any],
        knowledge_base_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use LLM to assess eligibility"""
        
        # Prepare context
        funder_summary = {
            "name": funder_info.get("name"),
            "focus_areas": funder_info.get("focus_areas", []),
            "eligibility_criteria": funder_info.get("eligibility_criteria", []),
            "requirements": funder_info.get("requirements", {}),
            "mission": funder_info.get("mission"),
            "priorities": funder_info.get("priorities", [])
        }
        
        user_summary = {
            "organization_type": user_profile.get("organization_type"),
            "projects": user_profile.get("projects", []),
            "team": user_profile.get("team", []),
            "budget": user_profile.get("budget", {}),
            "experience": user_profile.get("experience", []),
            "focus_areas": user_profile.get("focus_areas", [])
        }
        
        prompt = f"""As an expert funding advisor, assess whether this organization qualifies for this funding opportunity.

FUNDER INFORMATION:
{json.dumps(funder_summary, indent=2)}

ORGANIZATION PROFILE:
{json.dumps(user_summary, indent=2)}

ADDITIONAL INFORMATION:
{json.dumps(knowledge_base_data or {}, indent=2)}

Assess eligibility and return JSON with:
{{
    "overall_assessment": "detailed assessment text",
    "requirements_met": ["requirement1", "requirement2", ...],
    "requirements_missing": ["requirement1", "requirement2", ...],
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "alignment_score": <0-10>,  // How well aligned with funder priorities
    "eligibility_score": <0-10>,  // Overall eligibility score
    "key_factors": ["factor1", "factor2", ...],
    "qualification_gaps": ["gap1", "gap2", ...],
    "recommendations": ["recommendation1", "recommendation2", ...]
}}

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=3000
            )
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        
        except Exception as e:
            logger.error(f"Error assessing eligibility: {e}")
            return {
                "overall_assessment": "Assessment could not be completed",
                "requirements_met": [],
                "requirements_missing": [],
                "strengths": [],
                "weaknesses": [],
                "alignment_score": 5.0,
                "eligibility_score": 5.0
            }
    
    def _calculate_eligibility_score(self, assessment: Dict[str, Any]) -> float:
        """Calculate overall eligibility score"""
        base_score = assessment.get("eligibility_score", 5.0)
        alignment = assessment.get("alignment_score", 5.0)
        
        # Weighted average
        eligibility_score = (base_score * 0.6 + alignment * 0.4) / 10.0
        
        # Adjust based on requirements
        requirements_met = len(assessment.get("requirements_met", []))
        requirements_missing = len(assessment.get("requirements_missing", []))
        
        if requirements_met + requirements_missing > 0:
            requirement_ratio = requirements_met / (requirements_met + requirements_missing)
            eligibility_score = (eligibility_score * 0.7) + (requirement_ratio * 0.3)
        
        return round(eligibility_score, 2)
    
    def _generate_recommendations(
        self,
        assessment: Dict[str, Any],
        funder_info: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Add LLM-generated recommendations
        llm_recommendations = assessment.get("recommendations", [])
        recommendations.extend(llm_recommendations)
        
        # Add specific recommendations based on gaps
        gaps = assessment.get("qualification_gaps", [])
        for gap in gaps:
            recommendations.append(f"Address gap: {gap}")
        
        # Add recommendations for missing requirements
        missing = assessment.get("requirements_missing", [])
        for req in missing:
            recommendations.append(f"Meet requirement: {req}")
        
        # Add alignment recommendations
        focus_areas = funder_info.get("focus_areas", [])
        user_focus = user_profile.get("focus_areas", [])
        missing_focus = [f for f in focus_areas if f not in user_focus]
        if missing_focus:
            recommendations.append(
                f"Consider aligning with funder focus areas: {', '.join(missing_focus[:3])}"
            )
        
        return recommendations[:10]  # Limit to top 10
    
    def _get_qualification_level(self, score: float) -> str:
        """Get qualification level description"""
        if score >= 0.9:
            return "Highly Qualified"
        elif score >= 0.7:
            return "Qualified"
        elif score >= 0.5:
            return "Partially Qualified"
        elif score >= 0.3:
            return "Minimally Qualified"
        else:
            return "Not Qualified"
    
    def _get_next_steps(
        self,
        score: float,
        recommendations: List[str]
    ) -> List[str]:
        """Get next steps based on eligibility"""
        if score >= 0.7:
            return [
                "Proceed with proposal submission",
                "Review and strengthen proposal",
                "Ensure all required documents are ready",
                "Submit before deadline"
            ]
        elif score >= 0.5:
            return [
                "Address key qualification gaps",
                "Strengthen alignment with funder priorities",
                "Consider alternative funding sources",
                "Reassess after improvements"
            ]
        else:
            return [
                "Significant gaps need to be addressed",
                "Consider alternative funding opportunities",
                "Work on building required qualifications",
                "Reassess eligibility after improvements"
            ]
    
    def compare_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Compare multiple funding opportunities and rank by eligibility
        
        Args:
            opportunities: List of funder/opportunity information
            user_profile: User's profile
        
        Returns:
            Ranked list of opportunities with eligibility scores
        """
        self.log_action(f"Comparing {len(opportunities)} funding opportunities")
        
        assessments = []
        for opp in opportunities:
            assessment = self.assess_eligibility(
                funder_info=opp,
                user_profile=user_profile
            )
            assessments.append({
                "opportunity": opp.get("name", "Unknown"),
                "assessment": assessment,
                "score": assessment["eligibility_score"]
            })
        
        # Sort by score (highest first)
        assessments.sort(key=lambda x: x["score"], reverse=True)
        
        return assessments
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - assess eligibility"""
        funder_info = input_data.get("funder_info", {})
        user_profile = input_data.get("user_profile", {})
        knowledge_base_data = input_data.get("knowledge_base_data")
        
        return self.assess_eligibility(
            funder_info=funder_info,
            user_profile=user_profile,
            knowledge_base_data=knowledge_base_data
        )

