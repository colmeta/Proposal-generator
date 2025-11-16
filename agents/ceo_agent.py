"""
CEO Agent - Final Quality Gate and Approval Authority
Reviews ALL work before delivery. Ensures perfection standard.
"""

from typing import Dict, Any, List, Tuple
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json


class CEOAgent(BaseAgent):
    """
    CEO Agent - Final approval authority.
    Reviews ALL outputs before delivery with perfection standard.
    """
    
    def __init__(self):
        super().__init__(
            name="CEO Agent",
            role="Final quality oversight and strategic approval",
            task_type="quality"
        )
        self.approval_threshold = 9.5  # Minimum quality score (out of 10)
    
    def review_proposal(
        self,
        proposal: Dict[str, Any],
        requirements: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Multi-layer review of proposal
        
        Review layers:
        1. Completeness check (all sections present)
        2. Quality check (professional, compelling)
        3. Compliance check (meets funder requirements)
        4. Differentiation check (stands out from competitors)
        5. Win probability assessment
        6. Final approval or rejection with feedback
        
        Args:
            proposal: The proposal document/data
            requirements: Funder requirements and criteria
            research_data: Research findings about funder and competitors
        
        Returns:
            Review result with approval status, score, and feedback
        """
        self.log_action("Starting comprehensive proposal review")
        
        # Perform all review checks
        completeness = self._check_completeness(proposal, requirements)
        quality = self._check_quality(proposal)
        compliance = self._check_compliance(proposal, requirements)
        differentiation = self._check_differentiation(proposal, research_data)
        win_probability = self._assess_win_probability(
            proposal, requirements, research_data
        )
        
        # Calculate overall score
        overall_score = (
            completeness["score"] * 0.15 +
            quality["score"] * 0.30 +
            compliance["score"] * 0.25 +
            differentiation["score"] * 0.15 +
            win_probability["score"] * 0.15
        )
        
        # Collect all issues
        all_issues = []
        all_issues.extend(completeness.get("issues", []))
        all_issues.extend(quality.get("issues", []))
        all_issues.extend(compliance.get("issues", []))
        all_issues.extend(differentiation.get("issues", []))
        
        # Determine approval
        approved = overall_score >= self.approval_threshold and len(all_issues) == 0
        
        result = {
            "approved": approved,
            "overall_score": round(overall_score, 2),
            "win_probability": win_probability["score"],
            "checks": {
                "completeness": completeness,
                "quality": quality,
                "compliance": compliance,
                "differentiation": differentiation,
                "win_probability": win_probability
            },
            "issues": all_issues,
            "feedback": self._generate_feedback(
                approved, overall_score, all_issues, win_probability
            ),
            "improvements": self._suggest_improvements(all_issues) if not approved else []
        }
        
        if approved:
            self.log_action("Proposal APPROVED for delivery", {"score": overall_score})
        else:
            self.log_action("Proposal REJECTED - requires improvements", {
                "score": overall_score,
                "issues": len(all_issues)
            })
        
        return result
    
    def _check_completeness(
        self,
        proposal: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if all required sections are present"""
        required_sections = requirements.get("required_sections", [
            "executive_summary",
            "problem_statement",
            "solution",
            "methodology",
            "budget",
            "timeline",
            "team",
            "impact"
        ])
        
        proposal_sections = proposal.get("sections", {})
        missing = [s for s in required_sections if s not in proposal_sections]
        
        score = 10.0 if len(missing) == 0 else max(0, 10.0 - (len(missing) * 2))
        
        return {
            "score": score,
            "status": "complete" if len(missing) == 0 else "incomplete",
            "missing_sections": missing,
            "issues": [f"Missing section: {s}" for s in missing]
        }
    
    def _check_quality(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall quality and professionalism"""
        prompt = f"""As a CEO reviewing a funding proposal, assess the overall quality and professionalism.

Proposal content:
{json.dumps(proposal.get('content', {}), indent=2)}

Evaluate on:
1. Writing quality (clarity, professionalism, persuasiveness)
2. Structure and organization
3. Use of evidence and data
4. Professional tone and presentation

Rate from 0-10 and provide specific feedback on any quality issues.
Return JSON: {{"score": <0-10>, "issues": [<list of issues>], "strengths": [<list of strengths>]}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "score": float(result.get("score", 7.0)),
                    "issues": result.get("issues", []),
                    "strengths": result.get("strengths", [])
                }
        except Exception as e:
            self.logger.warning(f"Quality check LLM call failed: {e}")
        
        # Fallback assessment
        content_length = len(str(proposal.get("content", "")))
        has_data = "data" in str(proposal.get("content", "")).lower()
        
        score = 7.0
        issues = []
        if content_length < 1000:
            issues.append("Content too brief")
            score -= 2.0
        if not has_data:
            issues.append("Lacks supporting data/evidence")
            score -= 1.0
        
        return {
            "score": max(0, score),
            "issues": issues,
            "strengths": []
        }
    
    def _check_compliance(
        self,
        proposal: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance with funder requirements"""
        prompt = f"""As a CEO, verify the proposal meets all funder requirements.

Funder Requirements:
{json.dumps(requirements, indent=2)}

Proposal:
{json.dumps(proposal.get('content', {}), indent=2)}

Check:
1. All required criteria are addressed
2. Format requirements are met
3. Deadline and submission requirements
4. Budget constraints
5. Eligibility criteria

Return JSON: {{"score": <0-10>, "issues": [<list of compliance issues>], "compliant": <true/false>}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.2,
                max_tokens=2000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "score": float(result.get("score", 8.0)),
                    "issues": result.get("issues", []),
                    "compliant": result.get("compliant", True)
                }
        except Exception as e:
            self.logger.warning(f"Compliance check LLM call failed: {e}")
        
        # Fallback: basic compliance check
        return {
            "score": 8.5,
            "issues": [],
            "compliant": True
        }
    
    def _check_differentiation(
        self,
        proposal: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if proposal stands out from competitors"""
        competitors = research_data.get("competitors", [])
        
        if not competitors:
            return {
                "score": 8.0,
                "issues": [],
                "note": "No competitor data available"
            }
        
        prompt = f"""As a CEO, assess how well this proposal differentiates from competitors.

Competitor Analysis:
{json.dumps(competitors, indent=2)}

Our Proposal:
{json.dumps(proposal.get('content', {}), indent=2)}

Evaluate:
1. Unique value proposition
2. Competitive advantages highlighted
3. Differentiation from competitors
4. Compelling reasons to choose us

Return JSON: {{"score": <0-10>, "issues": [<differentiation issues>], "differentiators": [<unique strengths>]}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=2000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "score": float(result.get("score", 7.5)),
                    "issues": result.get("issues", []),
                    "differentiators": result.get("differentiators", [])
                }
        except Exception as e:
            self.logger.warning(f"Differentiation check LLM call failed: {e}")
        
        return {
            "score": 7.5,
            "issues": [],
            "differentiators": []
        }
    
    def _assess_win_probability(
        self,
        proposal: Dict[str, Any],
        requirements: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess probability of winning the funding"""
        prompt = f"""As a CEO with extensive experience in funding proposals, assess the win probability.

Funder Requirements:
{json.dumps(requirements, indent=2)}

Research Data:
{json.dumps(research_data, indent=2)}

Proposal Quality:
{json.dumps(proposal.get('content', {}), indent=2)}

Consider:
1. Alignment with funder priorities
2. Proposal quality and completeness
3. Competitive landscape
4. Track record and credibility
5. Budget reasonableness

Rate win probability as a score from 0-10 (where 10 = very high probability of winning).
Return JSON: {{"score": <0-10>, "probability_percent": <0-100>, "key_factors": [<factors affecting win probability>]}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=2000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                score = float(result.get("score", 7.0))
                return {
                    "score": score,
                    "probability_percent": result.get("probability_percent", score * 10),
                    "key_factors": result.get("key_factors", [])
                }
        except Exception as e:
            self.logger.warning(f"Win probability assessment failed: {e}")
        
        return {
            "score": 7.0,
            "probability_percent": 70,
            "key_factors": []
        }
    
    def _generate_feedback(
        self,
        approved: bool,
        score: float,
        issues: List[str],
        win_probability: Dict[str, Any]
    ) -> str:
        """Generate CEO feedback"""
        if approved:
            return (
                f"APPROVED. Quality score: {score}/10. "
                f"Win probability: {win_probability.get('probability_percent', 0)}%. "
                "This proposal meets our standards and is ready for submission."
            )
        else:
            return (
                f"REJECTED. Quality score: {score}/10 (minimum: {self.approval_threshold}). "
                f"Found {len(issues)} issues that must be addressed. "
                "See improvements list for specific actions required."
            )
    
    def _suggest_improvements(self, issues: List[str]) -> List[str]:
        """Generate specific improvement suggestions"""
        if not issues:
            return []
        
        prompt = f"""As a CEO, provide specific, actionable improvement suggestions for these issues:

Issues:
{json.dumps(issues, indent=2)}

Provide concrete, actionable improvements. Return as JSON array: ["improvement 1", "improvement 2", ...]
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=1500
            )
            
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.warning(f"Improvement suggestions failed: {e}")
        
        # Fallback: generic improvements
        return [f"Address: {issue}" for issue in issues[:5]]
    
    def approve_or_reject(
        self,
        work_product: Dict[str, Any],
        standards: Dict[str, Any]
    ) -> Tuple[bool, str, List[str]]:
        """
        Final approval or rejection
        
        Args:
            work_product: The work product to review
            standards: Quality standards to apply
        
        Returns:
            Tuple of (approved: bool, feedback: str, improvements: list)
        """
        review = self.review_proposal(
            work_product,
            standards.get("requirements", {}),
            standards.get("research_data", {})
        )
        
        return (
            review["approved"],
            review["feedback"],
            review["improvements"]
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - CEO review"""
        return self.review_proposal(
            input_data.get("proposal", {}),
            input_data.get("requirements", {}),
            input_data.get("research_data", {})
        )

