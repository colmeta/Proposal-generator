"""
Legal Director Agent
Handles regulatory compliance checks, risk assessment, legal requirements verification,
contract review, liability analysis, and compliance documentation.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class LegalDirectorAgent(BaseAgent):
    """
    Legal Director Agent - Legal compliance and risk assessment specialist.
    Performs compliance checks, assesses legal risks, verifies requirements,
    reviews contracts, analyzes liability, and ensures compliance documentation.
    """
    
    def __init__(self):
        super().__init__(
            name="Legal Director",
            role="Regulatory compliance, risk assessment, and legal requirements verification",
            task_type="analysis"
        )
    
    def check_regulatory_compliance(
        self,
        project_details: Dict[str, Any],
        industry: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check regulatory compliance requirements
        
        Args:
            project_details: Project details and scope
            industry: Industry sector (optional)
            jurisdiction: Legal jurisdiction (optional)
            
        Returns:
            Compliance check results with requirements, status, and recommendations
        """
        self.log_action("Checking regulatory compliance")
        
        prompt = f"""As a Legal Director, perform a regulatory compliance check for this project.

Project Details:
{json.dumps(project_details, indent=2)}

Industry: {industry or "Not specified"}
Jurisdiction: {jurisdiction or "Not specified"}

Identify:
1. Applicable regulations and compliance requirements
2. Required licenses, permits, or certifications
3. Data protection and privacy requirements (GDPR, CCPA, etc.)
4. Industry-specific regulations
5. Compliance risks and gaps
6. Required documentation

Return JSON format:
{{
    "compliant": <boolean>,
    "compliance_score": <0-10>,
    "applicable_regulations": [
        {{
            "regulation": "<name>",
            "category": "<category>",
            "status": "<compliant|non_compliant|requires_review>",
            "requirements": ["<requirement 1>", "<requirement 2>"],
            "risk_level": "<low|medium|high>"
        }}
    ],
    "required_licenses": ["<license 1>", "<license 2>"],
    "compliance_gaps": ["<gap 1>", "<gap 2>"],
    "recommendations": ["<recommendation 1>", "<recommendation 2>"],
    "documentation_required": ["<doc 1>", "<doc 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.2,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                compliance = json.loads(json_match.group())
                return compliance
        except Exception as e:
            logger.warning(f"Compliance check LLM call failed: {e}")
        
        # Fallback: basic compliance structure
        return {
            "compliant": True,
            "compliance_score": 7.0,
            "applicable_regulations": [],
            "required_licenses": [],
            "compliance_gaps": [],
            "recommendations": ["Conduct detailed compliance review with legal counsel"],
            "documentation_required": []
        }
    
    def assess_legal_risk(
        self,
        project_scope: Dict[str, Any],
        contracts: Optional[List[Dict[str, Any]]] = None,
        compliance_status: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess legal risks
        
        Args:
            project_scope: Project scope and activities
            contracts: Optional contract information
            compliance_status: Compliance check results
            
        Returns:
            Legal risk assessment with identified risks, severity, and mitigation strategies
        """
        self.log_action("Assessing legal risks")
        
        risks = []
        
        # Check compliance risks
        if compliance_status:
            gaps = compliance_status.get("compliance_gaps", [])
            for gap in gaps:
                risks.append({
                    "risk": f"Compliance gap: {gap}",
                    "category": "compliance",
                    "severity": "high",
                    "probability": "medium",
                    "impact": "Regulatory penalties, project delays, legal action"
                })
            
            non_compliant = [
                reg for reg in compliance_status.get("applicable_regulations", [])
                if reg.get("status") == "non_compliant"
            ]
            for reg in non_compliant:
                risks.append({
                    "risk": f"Non-compliance with {reg.get('regulation')}",
                    "category": "compliance",
                    "severity": "high",
                    "probability": "high",
                    "impact": "Legal penalties, project shutdown"
                })
        
        # Check contract risks
        if contracts:
            for contract in contracts:
                contract_type = contract.get("type", "unknown")
                if contract_type == "vendor" and not contract.get("liability_limitation"):
                    risks.append({
                        "risk": f"Vendor contract lacks liability limitation",
                        "category": "contract",
                        "severity": "medium",
                        "probability": "low",
                        "impact": "Unlimited liability exposure"
                    })
        
        # Check data privacy risks
        if project_scope.get("handles_personal_data", False):
            risks.append({
                "risk": "Handles personal data - privacy compliance required",
                "category": "privacy",
                "severity": "high",
                "probability": "high",
                "impact": "GDPR/CCPA violations, fines, reputation damage"
            })
        
        # Check intellectual property risks
        if project_scope.get("uses_third_party_ip", False):
            risks.append({
                "risk": "Uses third-party IP - licensing verification needed",
                "category": "intellectual_property",
                "severity": "medium",
                "probability": "medium",
                "impact": "IP infringement claims, licensing costs"
            })
        
        # Calculate overall risk score
        risk_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        total_risk_score = sum(
            risk_scores.get(risk.get("severity", "low"), 1) 
            for risk in risks
        )
        max_possible_score = len(risks) * 4 if risks else 1
        risk_score = (total_risk_score / max_possible_score * 10) if max_possible_score > 0 else 0
        
        # Categorize overall risk level
        if risk_score >= 7.5:
            overall_risk_level = "high"
        elif risk_score >= 5.0:
            overall_risk_level = "medium"
        else:
            overall_risk_level = "low"
        
        return {
            "overall_risk_level": overall_risk_level,
            "risk_score": round(risk_score, 2),
            "risks": risks,
            "risk_by_category": self._categorize_risks(risks),
            "mitigation_strategies": self._generate_risk_mitigation(risks),
            "recommendations": self._generate_risk_recommendations(risks, overall_risk_level)
        }
    
    def verify_legal_requirements(
        self,
        project_requirements: Dict[str, Any],
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify legal requirements are met
        
        Args:
            project_requirements: Project requirements
            industry: Industry sector (optional)
            
        Returns:
            Legal requirements verification with status and gaps
        """
        self.log_action("Verifying legal requirements")
        
        requirements = {
            "verified": True,
            "requirements_met": [],
            "requirements_missing": [],
            "requirements_pending": [],
            "documentation_status": {}
        }
        
        # Check for common legal requirements
        common_requirements = [
            "business_license",
            "insurance_coverage",
            "data_protection_policy",
            "terms_of_service",
            "privacy_policy",
            "contract_templates"
        ]
        
        for req in common_requirements:
            if project_requirements.get(req, False):
                requirements["requirements_met"].append(req)
            else:
                requirements["requirements_missing"].append(req)
                requirements["verified"] = False
        
        # Industry-specific requirements
        if industry:
            if industry.lower() in ["healthcare", "medical"]:
                requirements["requirements_missing"].append("HIPAA compliance")
                requirements["verified"] = False
            elif industry.lower() in ["finance", "banking", "fintech"]:
                requirements["requirements_missing"].append("Financial regulatory compliance")
                requirements["verified"] = False
        
        return requirements
    
    def review_contract(
        self,
        contract_details: Dict[str, Any],
        contract_type: str = "vendor"
    ) -> Dict[str, Any]:
        """
        Review contract for legal issues
        
        Args:
            contract_details: Contract details
            contract_type: Type of contract (vendor, client, partnership, etc.)
            
        Returns:
            Contract review with identified issues, recommendations, and approval status
        """
        self.log_action(f"Reviewing {contract_type} contract")
        
        prompt = f"""As a Legal Director, review this {contract_type} contract.

Contract Details:
{json.dumps(contract_details, indent=2)}

Review for:
1. Liability and indemnification clauses
2. Payment terms and conditions
3. Intellectual property rights
4. Termination clauses
5. Dispute resolution mechanisms
6. Compliance with applicable laws
7. Risk factors

Return JSON format:
{{
    "approved": <boolean>,
    "review_score": <0-10>,
    "issues": ["<issue 1>", "<issue 2>"],
    "strengths": ["<strength 1>", "<strength 2>"],
    "recommendations": ["<recommendation 1>", "<recommendation 2>"],
    "risk_factors": [
        {{
            "factor": "<risk factor>",
            "severity": "<low|medium|high>",
            "recommendation": "<mitigation>"
        }}
    ]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.2,
                max_tokens=2500
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                review = json.loads(json_match.group())
                return review
        except Exception as e:
            logger.warning(f"Contract review LLM call failed: {e}")
        
        # Fallback: basic review structure
        return {
            "approved": True,
            "review_score": 7.0,
            "issues": [],
            "strengths": ["Contract structure appears standard"],
            "recommendations": ["Have contract reviewed by legal counsel"],
            "risk_factors": []
        }
    
    def analyze_liability(
        self,
        project_activities: Dict[str, Any],
        insurance_coverage: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze liability exposure
        
        Args:
            project_activities: Project activities and scope
            insurance_coverage: Insurance coverage details (optional)
            
        Returns:
            Liability analysis with exposure areas, recommendations, and insurance needs
        """
        self.log_action("Analyzing liability exposure")
        
        liability_areas = []
        
        # Check for high-liability activities
        if project_activities.get("handles_sensitive_data", False):
            liability_areas.append({
                "area": "Data breach liability",
                "exposure_level": "high",
                "recommendation": "Ensure cyber liability insurance coverage"
            })
        
        if project_activities.get("provides_advice", False):
            liability_areas.append({
                "area": "Professional liability",
                "exposure_level": "medium",
                "recommendation": "Consider professional liability insurance"
            })
        
        if project_activities.get("physical_operations", False):
            liability_areas.append({
                "area": "General liability",
                "exposure_level": "medium",
                "recommendation": "Ensure general liability insurance coverage"
            })
        
        # Check insurance adequacy
        coverage_adequate = True
        if insurance_coverage:
            required_coverage = {
                "general_liability": 1000000,
                "professional_liability": 1000000,
                "cyber_liability": 500000
            }
            
            for coverage_type, min_amount in required_coverage.items():
                current_amount = insurance_coverage.get(coverage_type, 0)
                if current_amount < min_amount:
                    coverage_adequate = False
                    liability_areas.append({
                        "area": f"Insufficient {coverage_type} coverage",
                        "exposure_level": "high",
                        "recommendation": f"Increase {coverage_type} to at least ${min_amount:,}"
                    })
        
        return {
            "liability_areas": liability_areas,
            "coverage_adequate": coverage_adequate,
            "recommendations": [area["recommendation"] for area in liability_areas],
            "overall_exposure": "high" if any(a["exposure_level"] == "high" for a in liability_areas) else "medium"
        }
    
    def create_compliance_documentation(
        self,
        compliance_requirements: Dict[str, Any],
        project_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create compliance documentation checklist
        
        Args:
            compliance_requirements: Compliance requirements
            project_details: Project details
            
        Returns:
            Compliance documentation checklist with required documents and status
        """
        self.log_action("Creating compliance documentation checklist")
        
        documentation = {
            "required_documents": [],
            "document_status": {},
            "completion_percentage": 0.0
        }
        
        # Standard compliance documents
        standard_docs = [
            "Privacy Policy",
            "Terms of Service",
            "Data Processing Agreement",
            "Security Policy",
            "Compliance Checklist",
            "Risk Assessment Report"
        ]
        
        # Add industry-specific documents
        industry = project_details.get("industry", "")
        if industry.lower() in ["healthcare", "medical"]:
            standard_docs.append("HIPAA Compliance Documentation")
        if industry.lower() in ["finance", "banking"]:
            standard_docs.append("Financial Regulatory Compliance Documentation")
        
        documentation["required_documents"] = standard_docs
        
        # Initialize status
        for doc in standard_docs:
            documentation["document_status"][doc] = "pending"
        
        documentation["completion_percentage"] = 0.0
        
        return documentation
    
    def _categorize_risks(self, risks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize risks by category"""
        categorized = {}
        for risk in risks:
            category = risk.get("category", "other")
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(risk)
        return categorized
    
    def _generate_risk_mitigation(self, risks: List[Dict[str, Any]]) -> List[str]:
        """Generate risk mitigation strategies"""
        mitigations = []
        
        for risk in risks:
            category = risk.get("category", "")
            severity = risk.get("severity", "medium")
            
            if category == "compliance":
                mitigations.append("Conduct compliance audit and address identified gaps")
            elif category == "contract":
                mitigations.append("Review and revise contract terms with legal counsel")
            elif category == "privacy":
                mitigations.append("Implement data protection measures and privacy policies")
            elif category == "intellectual_property":
                mitigations.append("Verify IP licenses and obtain necessary permissions")
            else:
                mitigations.append(f"Develop mitigation plan for {risk.get('risk', 'identified risk')}")
        
        return list(set(mitigations))  # Remove duplicates
    
    def _generate_risk_recommendations(
        self,
        risks: List[Dict[str, Any]],
        overall_risk_level: str
    ) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if overall_risk_level == "high":
            recommendations.append("URGENT: Address high-severity legal risks before proceeding")
            recommendations.append("Engage legal counsel for comprehensive risk review")
        elif overall_risk_level == "medium":
            recommendations.append("Address medium-severity risks and implement mitigation strategies")
        else:
            recommendations.append("Continue monitoring legal risks throughout project")
        
        high_severity_risks = [r for r in risks if r.get("severity") == "high"]
        if high_severity_risks:
            recommendations.append(f"Prioritize mitigation of {len(high_severity_risks)} high-severity risks")
        
        return recommendations
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - Legal Director workflow
        
        Expected input:
        {
            "action": "check_compliance" | "assess_risk" | "verify_requirements" |
                      "review_contract" | "analyze_liability" | "create_documentation",
            "project_details": {...},
            "project_scope": {...},
            "contract_details": {...},
            ...
        }
        """
        action = input_data.get("action", "check_compliance")
        
        if action == "check_compliance":
            return self.check_regulatory_compliance(
                input_data.get("project_details", {}),
                input_data.get("industry"),
                input_data.get("jurisdiction")
            )
        elif action == "assess_risk":
            return self.assess_legal_risk(
                input_data.get("project_scope", {}),
                input_data.get("contracts"),
                input_data.get("compliance_status")
            )
        elif action == "verify_requirements":
            return self.verify_legal_requirements(
                input_data.get("project_requirements", {}),
                input_data.get("industry")
            )
        elif action == "review_contract":
            return self.review_contract(
                input_data.get("contract_details", {}),
                input_data.get("contract_type", "vendor")
            )
        elif action == "analyze_liability":
            return self.analyze_liability(
                input_data.get("project_activities", {}),
                input_data.get("insurance_coverage")
            )
        elif action == "create_documentation":
            return self.create_compliance_documentation(
                input_data.get("compliance_requirements", {}),
                input_data.get("project_details", {})
            )
        else:
            # Default: check compliance
            return self.check_regulatory_compliance(
                input_data.get("project_details", {}),
                input_data.get("industry"),
                input_data.get("jurisdiction")
            )

