"""
Government Specialist Agent
RFP analysis, procurement compliance, government-specific requirements, public sector expertise
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json


class GovernmentSpecialistAgent(BaseAgent):
    """
    Government Specialist Agent
    Specializes in RFP analysis, procurement compliance, and government-specific requirements
    """
    
    def __init__(self):
        super().__init__(
            name="Government Specialist",
            role="RFP analysis and government procurement compliance",
            task_type="compliance"
        )
    
    def analyze_rfp(
        self,
        rfp_document: Dict[str, Any],
        rfp_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze RFP document for requirements and compliance needs
        
        Args:
            rfp_document: Structured RFP data
            rfp_text: Raw RFP text if available
        
        Returns:
            RFP analysis with requirements, compliance needs, and recommendations
        """
        self.log_action("Analyzing RFP document")
        
        rfp_content = rfp_text or json.dumps(rfp_document, indent=2)
        
        prompt = f"""As a Government Specialist, analyze this RFP (Request for Proposal) document.

RFP Content:
{rfp_content}

Analyze and extract:
1. All requirements (mandatory and optional)
2. Compliance requirements (regulations, standards, certifications)
3. Evaluation criteria and scoring
4. Submission requirements and deadlines
5. Budget constraints and payment terms
6. Technical specifications
7. Risk factors and challenges
8. Competitive positioning opportunities

Return JSON:
{{
    "mandatory_requirements": ["requirement 1", "requirement 2"],
    "optional_requirements": ["requirement 1"],
    "compliance_requirements": [
        {{
            "requirement": "requirement description",
            "type": "certification/regulation/standard",
            "details": "specific details"
        }}
    ],
    "evaluation_criteria": [
        {{
            "criterion": "criterion name",
            "weight": "percentage or description",
            "description": "what is evaluated"
        }}
    ],
    "submission_requirements": {{
        "deadline": "deadline date",
        "format": "format requirements",
        "sections": ["section 1", "section 2"],
        "page_limits": "limits if any"
    }},
    "budget_info": {{
        "budget_range": "range if specified",
        "payment_terms": "terms description",
        "budget_constraints": ["constraint 1"]
    }},
    "technical_specifications": ["spec 1", "spec 2"],
    "risk_factors": ["risk 1", "risk 2"],
    "opportunities": ["opportunity 1", "opportunity 2"],
    "compliance_score": 0-10,
    "win_probability_factors": ["factor 1"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.2,
                max_tokens=4000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                self.log_action("RFP analyzed", {
                    "mandatory_reqs": len(analysis.get("mandatory_requirements", [])),
                    "compliance_score": analysis.get("compliance_score")
                })
                return analysis
        except Exception as e:
            self.logger.warning(f"RFP analysis LLM call failed: {e}")
        
        # Fallback analysis
        return {
            "mandatory_requirements": ["Meet all specified requirements", "Comply with regulations"],
            "optional_requirements": [],
            "compliance_requirements": [
                {
                    "requirement": "General compliance",
                    "type": "regulation",
                    "details": "Must comply with applicable regulations"
                }
            ],
            "evaluation_criteria": [
                {
                    "criterion": "Technical approach",
                    "weight": "High",
                    "description": "Quality of technical solution"
                },
                {
                    "criterion": "Cost",
                    "weight": "Medium",
                    "description": "Cost-effectiveness"
                }
            ],
            "submission_requirements": {
                "deadline": "TBD",
                "format": "As specified in RFP",
                "sections": ["Executive Summary", "Technical Approach", "Budget"],
                "page_limits": "As specified"
            },
            "budget_info": {
                "budget_range": "Not specified",
                "payment_terms": "As per contract",
                "budget_constraints": []
            },
            "technical_specifications": ["Meet technical requirements"],
            "risk_factors": ["Compliance risks", "Timeline risks"],
            "opportunities": ["Strong technical approach", "Competitive pricing"],
            "compliance_score": 7.0,
            "win_probability_factors": ["Technical expertise", "Compliance"]
        }
    
    def ensure_procurement_compliance(
        self,
        proposal: Dict[str, Any],
        rfp_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ensure proposal meets procurement compliance requirements
        
        Args:
            proposal: Proposal document/data
            rfp_requirements: RFP requirements and compliance needs
        
        Returns:
            Compliance assessment with gaps and recommendations
        """
        self.log_action("Ensuring procurement compliance")
        
        prompt = f"""As a Government Specialist, verify procurement compliance.

Proposal:
{json.dumps(proposal, indent=2)}

RFP Requirements:
{json.dumps(rfp_requirements, indent=2)}

Check compliance with:
1. All mandatory requirements addressed
2. Format and submission requirements met
3. Certifications and qualifications included
4. Budget and pricing compliance
5. Technical specifications met
6. Legal and regulatory compliance
7. Documentation completeness

Return JSON:
{{
    "compliance_status": "compliant/partial/non-compliant",
    "compliance_score": 0-10,
    "mandatory_requirements_met": {{
        "met": ["requirement 1"],
        "missing": ["requirement 2"],
        "partial": ["requirement 3"]
    }},
    "format_compliance": {{
        "compliant": true/false,
        "issues": ["issue 1"]
    }},
    "certifications": {{
        "required": ["cert 1"],
        "provided": ["cert 1"],
        "missing": ["cert 2"]
    }},
    "gaps": ["gap 1", "gap 2"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "risk_assessment": "risk level and description"
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
                self.log_action("Compliance assessed", {
                    "status": compliance.get("compliance_status"),
                    "score": compliance.get("compliance_score")
                })
                return compliance
        except Exception as e:
            self.logger.warning(f"Compliance check LLM call failed: {e}")
        
        # Fallback assessment
        return {
            "compliance_status": "partial",
            "compliance_score": 7.5,
            "mandatory_requirements_met": {
                "met": [],
                "missing": [],
                "partial": []
            },
            "format_compliance": {
                "compliant": True,
                "issues": []
            },
            "certifications": {
                "required": [],
                "provided": [],
                "missing": []
            },
            "gaps": [],
            "recommendations": ["Review all requirements", "Ensure complete documentation"],
            "risk_assessment": "Moderate - requires review"
        }
    
    def identify_government_requirements(
        self,
        project_type: str,
        jurisdiction: str = "federal"
    ) -> Dict[str, Any]:
        """
        Identify government-specific requirements for project type
        
        Args:
            project_type: Type of project (IT, construction, services, etc.)
            jurisdiction: Government level (federal, state, local)
        
        Returns:
            Government requirements checklist
        """
        self.log_action("Identifying government requirements")
        
        prompt = f"""As a Government Specialist, identify all government-specific requirements.

Project Type: {project_type}
Jurisdiction: {jurisdiction}

Identify requirements for:
1. Certifications and qualifications
2. Regulatory compliance
3. Security and clearance requirements
4. Reporting and documentation
5. Contract terms and conditions
6. Insurance and bonding
7. Small business preferences
8. Environmental and sustainability
9. Accessibility requirements
10. Data security and privacy

Return JSON:
{{
    "certifications": [
        {{
            "certification": "cert name",
            "required": true/false,
            "description": "description"
        }}
    ],
    "regulatory_compliance": ["regulation 1", "regulation 2"],
    "security_requirements": ["requirement 1"],
    "reporting_requirements": ["report type 1"],
    "contract_terms": ["term 1", "term 2"],
    "insurance_bonding": {{
        "insurance": "requirements",
        "bonding": "requirements"
    }},
    "small_business_preferences": "description",
    "environmental": ["requirement 1"],
    "accessibility": ["requirement 1"],
    "data_security": ["requirement 1"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                requirements = json.loads(json_match.group())
                self.log_action("Government requirements identified", {
                    "certifications": len(requirements.get("certifications", []))
                })
                return requirements
        except Exception as e:
            self.logger.warning(f"Requirements identification LLM call failed: {e}")
        
        # Fallback requirements
        return {
            "certifications": [
                {
                    "certification": "General business license",
                    "required": True,
                    "description": "Valid business license"
                }
            ],
            "regulatory_compliance": ["Applicable federal regulations"],
            "security_requirements": ["Data security standards"],
            "reporting_requirements": ["Progress reports", "Financial reports"],
            "contract_terms": ["Standard government contract terms"],
            "insurance_bonding": {
                "insurance": "General liability insurance",
                "bonding": "Performance bond if required"
            },
            "small_business_preferences": "Small business set-asides may apply",
            "environmental": ["Environmental compliance"],
            "accessibility": ["Section 508 compliance if applicable"],
            "data_security": ["FISMA compliance if handling federal data"]
        }
    
    def provide_public_sector_expertise(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provide public sector expertise and guidance
        
        Args:
            question: Question about public sector procurement or compliance
            context: Additional context
        
        Returns:
            Expert guidance and recommendations
        """
        self.log_action("Providing public sector expertise")
        
        context_str = json.dumps(context, indent=2) if context else "None"
        
        prompt = f"""As a Government Specialist with deep public sector expertise, answer this question.

Question: {question}

Context:
{context_str}

Provide comprehensive guidance including:
1. Direct answer to the question
2. Relevant regulations or policies
3. Best practices
4. Common pitfalls to avoid
5. Actionable recommendations

Return JSON:
{{
    "answer": "comprehensive answer",
    "regulations": ["regulation 1", "regulation 2"],
    "best_practices": ["practice 1", "practice 2"],
    "pitfalls": ["pitfall 1", "pitfall 2"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "additional_resources": ["resource 1"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=2500
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                guidance = json.loads(json_match.group())
                self.log_action("Expert guidance provided")
                return guidance
        except Exception as e:
            self.logger.warning(f"Expertise guidance LLM call failed: {e}")
        
        # Fallback guidance
        return {
            "answer": "Consult with procurement specialists and review applicable regulations",
            "regulations": ["Applicable federal/state regulations"],
            "best_practices": ["Follow RFP requirements exactly", "Maintain compliance documentation"],
            "pitfalls": ["Missing deadlines", "Incomplete documentation"],
            "recommendations": ["Engage early", "Seek clarification if needed"],
            "additional_resources": ["Government procurement websites", "Regulatory agencies"]
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - route to appropriate method"""
        action = input_data.get("action", "analyze_rfp")
        
        if action == "analyze_rfp":
            return self.analyze_rfp(
                input_data.get("rfp_document", {}),
                input_data.get("rfp_text")
            )
        elif action == "ensure_compliance":
            return self.ensure_procurement_compliance(
                input_data.get("proposal", {}),
                input_data.get("rfp_requirements", {})
            )
        elif action == "identify_requirements":
            return self.identify_government_requirements(
                input_data.get("project_type", ""),
                input_data.get("jurisdiction", "federal")
            )
        elif action == "expertise":
            return self.provide_public_sector_expertise(
                input_data.get("question", ""),
                input_data.get("context")
            )
        else:
            # Default to RFP analysis
            return self.analyze_rfp(
                input_data.get("rfp_document", {}),
                input_data.get("rfp_text")
            )

