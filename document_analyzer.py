"""
Document analysis and gap identification system
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import FUNDER_REQUIREMENTS, DOCUMENT_TYPES


@dataclass
class Gap:
    """Represents a gap in a document"""
    section: str
    issue: str
    severity: str  # "critical", "important", "minor"
    recommendation: str


class DocumentAnalyzer:
    """Analyzes documents and identifies gaps"""
    
    def __init__(self, funder_type: str, document_type: str):
        self.funder_type = funder_type
        self.document_type = document_type
        self.funder_reqs = FUNDER_REQUIREMENTS.get(funder_type, {})
        self.doc_template = DOCUMENT_TYPES.get(document_type, {})
    
    def analyze_text(self, text: str) -> List[Gap]:
        """Analyze document text and identify gaps"""
        gaps = []
        text_lower = text.lower()
        
        # Check for required sections
        required_sections = self.doc_template.get("sections", [])
        for section in required_sections:
            section_keywords = self._get_section_keywords(section)
            if not any(keyword in text_lower for keyword in section_keywords):
                gaps.append(Gap(
                    section=section,
                    issue=f"Missing or insufficient {section} section",
                    severity="critical" if section in ["Problem Statement", "Solution", "Budget"] else "important",
                    recommendation=f"Add a comprehensive {section} section that addresses the funder's requirements"
                ))
        
        # Check for funder-specific requirements
        key_requirements = self.funder_reqs.get("key_requirements", [])
        for req in key_requirements:
            req_keywords = self._get_requirement_keywords(req)
            if not any(keyword in text_lower for keyword in req_keywords):
                gaps.append(Gap(
                    section="General",
                    issue=f"Missing {req}",
                    severity="critical" if req in ["Budget", "Timeline", "Impact metrics"] else "important",
                    recommendation=f"Include detailed information about {req} as required by {self.funder_reqs.get('name', 'the funder')}"
                ))
        
        # Check for data and evidence
        if not self._has_data_evidence(text):
            gaps.append(Gap(
                section="Evidence",
                issue="Lacks quantitative data and evidence",
                severity="critical",
                recommendation="Include statistics, research citations, and quantitative evidence to support claims"
            ))
        
        # Check for budget details
        if "budget" in text_lower and not self._has_detailed_budget(text):
            gaps.append(Gap(
                section="Budget",
                issue="Budget lacks sufficient detail",
                severity="critical",
                recommendation="Provide line-item budget breakdown with justification for each expense"
            ))
        
        # Check for impact metrics
        if not self._has_impact_metrics(text):
            gaps.append(Gap(
                section="Impact",
                issue="Missing measurable impact metrics",
                severity="critical",
                recommendation="Include specific, measurable, time-bound impact indicators and KPIs"
            ))
        
        return gaps
    
    def _get_section_keywords(self, section: str) -> List[str]:
        """Get keywords to identify a section"""
        keyword_map = {
            "Executive Summary": ["executive summary", "overview", "summary"],
            "Problem Statement": ["problem", "challenge", "issue", "need"],
            "Solution/Approach": ["solution", "approach", "methodology", "intervention"],
            "Budget": ["budget", "cost", "funding", "financial", "expense"],
            "Timeline": ["timeline", "schedule", "milestone", "phase", "duration"],
            "Impact and Outcomes": ["impact", "outcome", "result", "effect", "benefit"],
            "Sustainability Plan": ["sustainability", "sustainable", "long-term", "continuity"],
            "Partnerships": ["partnership", "collaboration", "partner", "stakeholder"],
            "Risk Assessment": ["risk", "challenge", "mitigation", "contingency"],
            "Monitoring and Evaluation": ["monitoring", "evaluation", "m&e", "assessment", "tracking"]
        }
        return keyword_map.get(section, [section.lower()])
    
    def _get_requirement_keywords(self, requirement: str) -> List[str]:
        """Get keywords to identify a requirement"""
        keyword_map = {
            "Clear problem statement with data": ["problem", "challenge", "data", "statistic"],
            "Evidence-based solution": ["evidence", "research", "study", "data", "proven"],
            "Measurable impact metrics": ["metric", "indicator", "kpi", "measure", "target"],
            "Budget breakdown": ["budget", "cost", "breakdown", "item", "expense"],
            "Timeline with milestones": ["timeline", "milestone", "schedule", "phase"],
            "Economic analysis": ["economic", "cost-benefit", "roi", "financial analysis"],
            "Risk assessment": ["risk", "assessment", "mitigation", "contingency"],
            "Environmental impact assessment": ["environmental", "impact assessment", "sustainability"],
            "Gender and social inclusion": ["gender", "inclusion", "equity", "diversity"],
            "Public health impact": ["public health", "health impact", "health outcome"],
            "Health system integration": ["health system", "integration", "healthcare"],
            "Business case alignment": ["business case", "roi", "value", "alignment"]
        }
        return keyword_map.get(requirement, requirement.lower().split())
    
    def _has_data_evidence(self, text: str) -> bool:
        """Check if text contains data and evidence"""
        # Look for numbers, percentages, statistics
        has_numbers = bool(re.search(r'\d+%|\d+\.\d+%|\d+,\d+|\d+\.\d+', text))
        # Look for citations or references
        has_citations = bool(re.search(r'\([A-Z][a-z]+ et al\.|\([A-Z][a-z]+, \d{4}\)|\[.*?\]', text))
        return has_numbers or has_citations
    
    def _has_detailed_budget(self, text: str) -> bool:
        """Check if budget has sufficient detail"""
        budget_section = re.search(r'budget.*?(?=\n\n|\n[A-Z]|$)', text, re.IGNORECASE | re.DOTALL)
        if not budget_section:
            return False
        budget_text = budget_section.group(0)
        # Check for multiple line items or categories
        has_line_items = len(re.findall(r'\$|USD|€|£|\d+,\d+|\d+\.\d+', budget_text)) >= 3
        has_categories = bool(re.search(r'personnel|staff|equipment|travel|overhead|administrative', budget_text, re.IGNORECASE))
        return has_line_items and has_categories
    
    def _has_impact_metrics(self, text: str) -> bool:
        """Check if text has measurable impact metrics"""
        metric_keywords = ["metric", "indicator", "kpi", "target", "goal", "outcome", "measure"]
        has_metrics = any(keyword in text.lower() for keyword in metric_keywords)
        has_numbers = bool(re.search(r'\d+%|\d+ people|\d+ communities|\d+ beneficiaries', text, re.IGNORECASE))
        return has_metrics and has_numbers
    
    def generate_gap_report(self, gaps: List[Gap]) -> str:
        """Generate a human-readable gap report"""
        if not gaps:
            return "✓ Your document appears comprehensive and meets the funder's requirements."
        
        report = "Document Gap Analysis Report\n"
        report += "=" * 50 + "\n\n"
        
        critical = [g for g in gaps if g.severity == "critical"]
        important = [g for g in gaps if g.severity == "important"]
        minor = [g for g in gaps if g.severity == "minor"]
        
        if critical:
            report += "🔴 CRITICAL GAPS (Must Address):\n"
            report += "-" * 50 + "\n"
            for gap in critical:
                report += f"\n• {gap.section}: {gap.issue}\n"
                report += f"  Recommendation: {gap.recommendation}\n"
            report += "\n"
        
        if important:
            report += "🟡 IMPORTANT GAPS (Should Address):\n"
            report += "-" * 50 + "\n"
            for gap in important:
                report += f"\n• {gap.section}: {gap.issue}\n"
                report += f"  Recommendation: {gap.recommendation}\n"
            report += "\n"
        
        if minor:
            report += "🟢 MINOR GAPS (Consider Addressing):\n"
            report += "-" * 50 + "\n"
            for gap in minor:
                report += f"\n• {gap.section}: {gap.issue}\n"
                report += f"  Recommendation: {gap.recommendation}\n"
        
        return report

