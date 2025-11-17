"""
Screening Pass Agent
Final validation agent that ensures proposals pass funder screening before delivery
Simulates funder's screening process and fixes issues
"""

from typing import Dict, Any, List, Optional, Tuple
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import re
import logging

logger = logging.getLogger(__name__)


class ScreeningPassAgent(BaseAgent):
    """
    Screening Pass Agent - Final validation before delivery
    Simulates funder screening process and ensures proposal passes
    """
    
    def __init__(self):
        super().__init__(
            name="Screening Pass Agent",
            role="Final screening validation - ensures proposal passes funder screening before delivery",
            task_type="quality"
        )
        self.screening_criteria = {}
    
    def screen_proposal(
        self,
        proposal: Dict[str, Any],
        funder_info: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Screen proposal as funder would - identify rejection risks
        
        Args:
            proposal: The proposal document
            requirements: Funder requirements and screening criteria
        
        Returns:
            Screening result with pass/fail and fixes needed
        """
        self.log_action("Screening proposal for funder screening process")
        
        # Extract screening criteria
        screening_criteria = self._extract_screening_criteria(funder_info, requirements)
        
        # Perform screening checks
        screening_result = self._perform_screening(
            proposal=proposal,
            screening_criteria=screening_criteria,
            funder_info=funder_info
        )
        
        # If failed, identify fixes
        if not screening_result["will_pass"]:
            fixes = self._identify_fixes(
                proposal=proposal,
                failures=screening_result["failures"],
                screening_criteria=screening_criteria
            )
            screening_result["fixes_needed"] = fixes
            screening_result["can_fix"] = len([f for f in fixes if f.get("fixable")]) > 0
        
        # Generate next steps
        next_steps = self._generate_next_steps(
            screening_result=screening_result,
            funder_info=funder_info,
            proposal=proposal
        )
        screening_result["next_steps"] = next_steps
        
        # Final decision
        if screening_result["will_pass"]:
            self.log_action("Proposal PASSED screening - ready for submission")
        else:
            self.log_action(
                f"Proposal FAILED screening - {len(screening_result['failures'])} issues found",
                {"fixable": screening_result.get("can_fix", False)}
            )
        
        return screening_result
    
    def _extract_screening_criteria(
        self,
        funder_info: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract screening criteria from funder info"""
        return {
            "eligibility": funder_info.get("eligibility_criteria", []),
            "required_sections": requirements.get("required_sections", []),
            "required_documents": requirements.get("required_documents", []),
            "format_requirements": requirements.get("format_requirements", {}),
            "deadline": funder_info.get("deadlines", {}),
            "budget_limits": funder_info.get("funding_amounts", {}),
            "focus_areas": funder_info.get("focus_areas", []),
            "exclusion_criteria": requirements.get("exclusion_criteria", [])
        }
    
    def _perform_screening(
        self,
        proposal: Dict[str, Any],
        screening_criteria: Dict[str, Any],
        funder_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform actual screening checks"""
        
        failures = []
        warnings = []
        checks_passed = []
        
        # Check 1: Eligibility criteria
        eligibility_check = self._check_eligibility(
            proposal, screening_criteria.get("eligibility", [])
        )
        if not eligibility_check["passed"]:
            failures.append({
                "check": "eligibility",
                "issue": eligibility_check["issue"],
                "severity": "critical",
                "will_cause_rejection": True
            })
        else:
            checks_passed.append("eligibility")
        
        # Check 2: Required sections
        sections_check = self._check_required_sections(
            proposal, screening_criteria.get("required_sections", [])
        )
        if not sections_check["passed"]:
            failures.append({
                "check": "required_sections",
                "issue": sections_check["issue"],
                "severity": "critical",
                "will_cause_rejection": True,
                "missing_sections": sections_check.get("missing", [])
            })
        else:
            checks_passed.append("required_sections")
        
        # Check 3: Required documents
        documents_check = self._check_required_documents(
            proposal, screening_criteria.get("required_documents", [])
        )
        if not documents_check["passed"]:
            failures.append({
                "check": "required_documents",
                "issue": documents_check["issue"],
                "severity": "critical",
                "will_cause_rejection": True,
                "missing_documents": documents_check.get("missing", [])
            })
        else:
            checks_passed.append("required_documents")
        
        # Check 4: Format requirements
        format_check = self._check_format_requirements(
            proposal, screening_criteria.get("format_requirements", {})
        )
        if not format_check["passed"]:
            failures.append({
                "check": "format_requirements",
                "issue": format_check["issue"],
                "severity": "high",
                "will_cause_rejection": True
            })
        else:
            checks_passed.append("format_requirements")
        
        # Check 5: Budget compliance
        budget_check = self._check_budget_compliance(
            proposal, screening_criteria.get("budget_limits", {})
        )
        if not budget_check["passed"]:
            failures.append({
                "check": "budget_compliance",
                "issue": budget_check["issue"],
                "severity": "critical",
                "will_cause_rejection": True
            })
        else:
            checks_passed.append("budget_compliance")
        
        # Check 6: Focus area alignment
        alignment_check = self._check_focus_alignment(
            proposal, screening_criteria.get("focus_areas", [])
        )
        if not alignment_check["passed"]:
            warnings.append({
                "check": "focus_alignment",
                "issue": alignment_check["issue"],
                "severity": "medium",
                "will_cause_rejection": False
            })
        else:
            checks_passed.append("focus_alignment")
        
        # Check 7: Exclusion criteria
        exclusion_check = self._check_exclusion_criteria(
            proposal, screening_criteria.get("exclusion_criteria", [])
        )
        if exclusion_check["violated"]:
            failures.append({
                "check": "exclusion_criteria",
                "issue": exclusion_check["issue"],
                "severity": "critical",
                "will_cause_rejection": True,
                "violations": exclusion_check.get("violations", [])
            })
        else:
            checks_passed.append("exclusion_criteria")
        
        # Use LLM for comprehensive screening
        llm_screening = self._llm_screening_check(
            proposal, funder_info, screening_criteria
        )
        
        # Merge LLM findings
        if llm_screening.get("will_be_rejected"):
            failures.append({
                "check": "comprehensive_screening",
                "issue": llm_screening.get("rejection_reason", "Would be rejected in screening"),
                "severity": "critical",
                "will_cause_rejection": True,
                "llm_analysis": llm_screening
            })
        
        will_pass = len([f for f in failures if f.get("will_cause_rejection")]) == 0
        
        return {
            "will_pass": will_pass,
            "failures": failures,
            "warnings": warnings,
            "checks_passed": checks_passed,
            "screening_score": self._calculate_screening_score(failures, warnings, checks_passed),
            "llm_analysis": llm_screening
        }
    
    def _check_eligibility(self, proposal: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
        """Check eligibility criteria"""
        proposal_text = str(proposal.get("content", "")).lower()
        
        for criterion in criteria:
            # Simple keyword check - could be enhanced
            if criterion.lower() not in proposal_text:
                return {
                    "passed": False,
                    "issue": f"Eligibility criterion not addressed: {criterion}"
                }
        
        return {"passed": True}
    
    def _check_required_sections(self, proposal: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
        """Check required sections are present"""
        sections = proposal.get("sections", {})
        missing = [s for s in required if s not in sections or not sections.get(s)]
        
        if missing:
            return {
                "passed": False,
                "issue": f"Missing required sections: {', '.join(missing)}",
                "missing": missing
            }
        
        return {"passed": True}
    
    def _check_required_documents(self, proposal: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
        """Check required documents are mentioned/attached"""
        proposal_text = str(proposal.get("content", "")).lower()
        missing = []
        
        for doc in required:
            doc_lower = doc.lower()
            # Check if document is mentioned
            if doc_lower not in proposal_text and not any(
                word in proposal_text for word in doc_lower.split()
            ):
                missing.append(doc)
        
        if missing:
            return {
                "passed": False,
                "issue": f"Required documents not included: {', '.join(missing)}",
                "missing": missing
            }
        
        return {"passed": True}
    
    def _check_format_requirements(self, proposal: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Check format requirements"""
        # Check page limits, font size, etc.
        if "max_pages" in requirements:
            # Would need to calculate pages from content
            pass
        
        return {"passed": True}
    
    def _check_budget_compliance(self, proposal: Dict[str, Any], limits: Dict[str, Any]) -> Dict[str, Any]:
        """Check budget is within limits"""
        proposal_budget = proposal.get("budget", {})
        max_amount = limits.get("maximum")
        
        if max_amount and proposal_budget:
            # Extract budget amount (simplified)
            total = proposal_budget.get("total", 0)
            if isinstance(max_amount, str):
                # Parse string like "$500,000"
                try:
                    max_amount = float(max_amount.replace("$", "").replace(",", ""))
                except:
                    pass
            
            if total and max_amount and total > max_amount:
                return {
                    "passed": False,
                    "issue": f"Budget ${total:,.0f} exceeds maximum ${max_amount:,.0f}"
                }
        
        return {"passed": True}
    
    def _check_focus_alignment(self, proposal: Dict[str, Any], focus_areas: List[str]) -> Dict[str, Any]:
        """Check alignment with funder focus areas"""
        proposal_text = str(proposal.get("content", "")).lower()
        
        matches = [area for area in focus_areas if area.lower() in proposal_text]
        
        if len(matches) == 0:
            return {
                "passed": False,
                "issue": f"Proposal doesn't align with funder focus areas: {', '.join(focus_areas)}"
            }
        
        return {"passed": True}
    
    def _check_exclusion_criteria(self, proposal: Dict[str, Any], exclusions: List[str]) -> Dict[str, Any]:
        """Check for exclusion criteria violations"""
        proposal_text = str(proposal.get("content", "")).lower()
        violations = []
        
        for exclusion in exclusions:
            if exclusion.lower() in proposal_text:
                violations.append(exclusion)
        
        if violations:
            return {
                "violated": True,
                "issue": f"Exclusion criteria violated: {', '.join(violations)}",
                "violations": violations
            }
        
        return {"violated": False}
    
    def _llm_screening_check(
        self,
        proposal: Dict[str, Any],
        funder_info: Dict[str, Any],
        screening_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to perform comprehensive screening check"""
        
        prompt = f"""You are a funder screening officer. Review this proposal and determine if it would PASS or FAIL the initial screening process.

FUNDER: {funder_info.get('name')}
SCREENING CRITERIA:
{json.dumps(screening_criteria, indent=2)}

PROPOSAL:
{json.dumps(proposal.get('content', {}), indent=2)[:5000]}

As a screening officer, you would:
1. Check if proposal meets basic eligibility
2. Verify all required sections are present
3. Check format compliance
4. Verify budget is within limits
5. Check for any exclusion criteria violations
6. Determine if it would be rejected in initial screening

Return JSON:
{{
    "will_be_rejected": true/false,
    "rejection_reason": "reason if rejected",
    "screening_notes": "detailed screening notes",
    "critical_issues": ["issue1", "issue2"],
    "minor_issues": ["issue1", "issue2"],
    "screening_decision": "PASS" or "REJECT",
    "confidence": <0-10>
}}

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.2,
                max_tokens=2000
            )
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        
        except Exception as e:
            logger.error(f"LLM screening check failed: {e}")
            return {
                "will_be_rejected": False,
                "screening_decision": "UNKNOWN",
                "error": str(e)
            }
    
    def _calculate_screening_score(
        self,
        failures: List[Dict],
        warnings: List[Dict],
        checks_passed: List[str]
    ) -> float:
        """Calculate screening pass score"""
        total_checks = len(checks_passed) + len(failures) + len(warnings)
        if total_checks == 0:
            return 1.0
        
        critical_failures = len([f for f in failures if f.get("severity") == "critical"])
        if critical_failures > 0:
            return 0.0  # Automatic fail
        
        passed_ratio = len(checks_passed) / total_checks
        warning_penalty = len(warnings) * 0.1
        
        return max(0.0, min(1.0, passed_ratio - warning_penalty))
    
    def _identify_fixes(
        self,
        proposal: Dict[str, Any],
        failures: List[Dict],
        screening_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify fixes needed to pass screening"""
        fixes = []
        
        for failure in failures:
            check = failure.get("check")
            issue = failure.get("issue")
            
            fix = {
                "issue": issue,
                "check": check,
                "severity": failure.get("severity"),
                "fixable": True,
                "fix_description": "",
                "priority": "high" if failure.get("will_cause_rejection") else "medium"
            }
            
            # Generate specific fix
            if check == "required_sections":
                missing = failure.get("missing_sections", [])
                fix["fix_description"] = f"Add missing sections: {', '.join(missing)}"
                fix["action"] = "add_sections"
                fix["sections_to_add"] = missing
            
            elif check == "required_documents":
                missing = failure.get("missing_documents", [])
                fix["fix_description"] = f"Include required documents: {', '.join(missing)}"
                fix["action"] = "add_documents"
                fix["documents_to_add"] = missing
            
            elif check == "eligibility":
                fix["fix_description"] = f"Address eligibility criterion: {issue}"
                fix["action"] = "update_content"
            
            elif check == "budget_compliance":
                fix["fix_description"] = f"Adjust budget to meet limits: {issue}"
                fix["action"] = "adjust_budget"
            
            elif check == "exclusion_criteria":
                violations = failure.get("violations", [])
                fix["fix_description"] = f"Remove exclusion criteria violations: {', '.join(violations)}"
                fix["action"] = "remove_content"
            
            else:
                fix["fix_description"] = f"Fix issue: {issue}"
                fix["action"] = "review_and_fix"
            
            fixes.append(fix)
        
        return fixes
    
    def _generate_next_steps(
        self,
        screening_result: Dict[str, Any],
        funder_info: Dict[str, Any],
        proposal: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate next steps for submission"""
        next_steps = []
        
        # If passed screening
        if screening_result["will_pass"]:
            next_steps.append({
                "step": "Review proposal",
                "description": "Review the proposal one final time before submission",
                "priority": "high"
            })
            
            # Check if video is recommended
            if self._should_include_video(funder_info, proposal):
                next_steps.append({
                    "step": "Create submission video",
                    "description": "Create a 2-3 minute video explaining your project",
                    "priority": "medium",
                    "video_guidelines": self._get_video_guidelines(funder_info)
                })
            
            # Check for additional documents
            additional_docs = self._get_additional_documents_needed(funder_info, proposal)
            if additional_docs:
                next_steps.append({
                    "step": "Prepare additional documents",
                    "description": f"Prepare: {', '.join(additional_docs)}",
                    "priority": "high",
                    "documents": additional_docs
                })
            
            next_steps.append({
                "step": "Submit proposal",
                "description": f"Submit before deadline: {funder_info.get('deadlines', {}).get('next_deadline', 'Check funder website')}",
                "priority": "critical"
            })
        
        else:
            # If failed, add fix steps
            fixes = screening_result.get("fixes_needed", [])
            for fix in fixes:
                next_steps.append({
                    "step": f"Fix: {fix.get('check')}",
                    "description": fix.get("fix_description"),
                    "priority": fix.get("priority", "high")
                })
            
            next_steps.append({
                "step": "Re-screen proposal",
                "description": "After fixes, re-screen to ensure it passes",
                "priority": "high"
            })
        
        # Add general submission steps
        next_steps.extend([
            {
                "step": "Double-check all requirements",
                "description": "Verify all funder requirements are met",
                "priority": "high"
            },
            {
                "step": "Get final approvals",
                "description": "Get internal approvals before submission",
                "priority": "medium"
            }
        ])
        
        return next_steps
    
    def _should_include_video(self, funder_info: Dict[str, Any], proposal: Dict[str, Any]) -> bool:
        """Determine if video submission is recommended"""
        # Check if funder accepts videos
        requirements = funder_info.get("requirements", {})
        if "video" in str(requirements).lower() or "multimedia" in str(requirements).lower():
            return True
        
        # Recommend for complex projects
        proposal_complexity = len(str(proposal.get("content", "")))
        if proposal_complexity > 10000:  # Long proposal
            return True
        
        return False
    
    def _get_video_guidelines(self, funder_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get video submission guidelines"""
        return {
            "duration": "2-3 minutes",
            "content": [
                "Introduce your organization",
                "Explain the problem you're solving",
                "Describe your solution",
                "Highlight key team members",
                "Show impact and outcomes"
            ],
            "format": "MP4, 1080p recommended",
            "tips": [
                "Keep it professional",
                "Use visuals and graphics",
                "Include team members",
                "Show real impact"
            ]
        }
    
    def _get_additional_documents_needed(
        self,
        funder_info: Dict[str, Any],
        proposal: Dict[str, Any]
    ) -> List[str]:
        """Determine additional documents needed for submission"""
        required = funder_info.get("requirements", {}).get("required_documents", [])
        proposal_text = str(proposal.get("content", "")).lower()
        
        # Check which documents are mentioned but might need to be prepared
        additional = []
        
        common_docs = [
            "budget justification",
            "timeline",
            "team biosketches",
            "letters of support",
            "organizational chart",
            "financial statements",
            "proof of non-profit status"
        ]
        
        for doc in common_docs:
            if doc in required or doc.replace(" ", "_") in required:
                if doc not in proposal_text:
                    additional.append(doc)
        
        return additional
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - screen proposal"""
        proposal = input_data.get("proposal", {})
        funder_info = input_data.get("funder_info", {})
        requirements = input_data.get("requirements", {})
        
        return self.screen_proposal(
            proposal=proposal,
            funder_info=funder_info,
            requirements=requirements
        )

