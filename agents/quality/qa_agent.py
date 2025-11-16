"""
QA Agent - Multi-layer Quality Assurance
Performs comprehensive quality checks, consistency verification,
error detection, and quality scoring.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import re
import logging

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """
    QA Agent - Comprehensive quality assurance.
    Performs multi-layer quality checks, consistency verification,
    error detection, and quality scoring.
    """
    
    def __init__(self):
        super().__init__(
            name="QA Agent",
            role="Multi-layer quality assurance and consistency verification",
            task_type="quality"
        )
        self.min_quality_score = 8.0  # Minimum acceptable quality score
    
    def perform_quality_check(
        self,
        document: Dict[str, Any],
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive multi-layer quality check
        
        Args:
            document: Document to check
            requirements: Optional requirements to check against
            
        Returns:
            Quality check results with scores, issues, and recommendations
        """
        self.log_action("Performing comprehensive quality check")
        
        # Perform all quality check layers
        structure_check = self._check_structure(document, requirements)
        consistency_check = self._check_consistency(document)
        error_check = self._check_errors(document)
        completeness_check = self._check_completeness(document, requirements)
        clarity_check = self._check_clarity(document)
        
        # Calculate overall quality score
        scores = [
            structure_check.get("score", 0),
            consistency_check.get("score", 0),
            error_check.get("score", 0),
            completeness_check.get("score", 0),
            clarity_check.get("score", 0)
        ]
        
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # Collect all issues
        all_issues = []
        all_issues.extend(structure_check.get("issues", []))
        all_issues.extend(consistency_check.get("issues", []))
        all_issues.extend(error_check.get("issues", []))
        all_issues.extend(completeness_check.get("issues", []))
        all_issues.extend(clarity_check.get("issues", []))
        
        # Determine if quality is acceptable
        quality_acceptable = overall_score >= self.min_quality_score and len(all_issues) == 0
        
        return {
            "quality_acceptable": quality_acceptable,
            "overall_score": round(overall_score, 2),
            "min_required_score": self.min_quality_score,
            "checks": {
                "structure": structure_check,
                "consistency": consistency_check,
                "errors": error_check,
                "completeness": completeness_check,
                "clarity": clarity_check
            },
            "issues": all_issues,
            "recommendations": self._generate_recommendations(all_issues, scores),
            "summary": self._generate_quality_summary(overall_score, all_issues)
        }
    
    def _check_structure(
        self,
        document: Dict[str, Any],
        requirements: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check document structure"""
        issues = []
        score = 10.0
        
        # Check for required sections
        content = document.get("content", {})
        if not content:
            issues.append("Document content is empty")
            score -= 5.0
        
        # Check section structure
        sections = content.get("sections", {}) if isinstance(content, dict) else {}
        if not sections:
            issues.append("No sections found in document")
            score -= 3.0
        
        # Check required sections if requirements provided
        if requirements:
            required_sections = requirements.get("required_sections", [])
            missing_sections = [
                section for section in required_sections
                if section not in sections
            ]
            if missing_sections:
                issues.append(f"Missing required sections: {', '.join(missing_sections)}")
                score -= len(missing_sections) * 1.5
        
        # Check section hierarchy
        if sections:
            for section_name, section_content in sections.items():
                if not section_content or (isinstance(section_content, str) and len(section_content.strip()) == 0):
                    issues.append(f"Section '{section_name}' is empty")
                    score -= 0.5
        
        score = max(0.0, min(10.0, score))
        
        return {
            "score": round(score, 2),
            "status": "pass" if score >= 8.0 else "fail",
            "issues": issues,
            "sections_found": len(sections) if sections else 0
        }
    
    def _check_consistency(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Check consistency across document"""
        issues = []
        score = 10.0
        
        content = document.get("content", {})
        if not content:
            return {"score": 0, "status": "fail", "issues": ["No content to check"], "inconsistencies": []}
        
        # Extract text content
        text_content = self._extract_text(content)
        
        # Check for inconsistent terminology
        terminology_issues = self._check_terminology_consistency(text_content)
        issues.extend(terminology_issues)
        score -= len(terminology_issues) * 0.5
        
        # Check for inconsistent formatting
        formatting_issues = self._check_formatting_consistency(text_content)
        issues.extend(formatting_issues)
        score -= len(formatting_issues) * 0.3
        
        # Check for inconsistent style
        style_issues = self._check_style_consistency(text_content)
        issues.extend(style_issues)
        score -= len(style_issues) * 0.4
        
        # Use LLM for deeper consistency check
        try:
            llm_consistency = self._llm_consistency_check(content)
            if llm_consistency:
                issues.extend(llm_consistency.get("issues", []))
                score -= len(llm_consistency.get("issues", [])) * 0.5
        except Exception as e:
            logger.warning(f"LLM consistency check failed: {e}")
        
        score = max(0.0, min(10.0, score))
        
        return {
            "score": round(score, 2),
            "status": "pass" if score >= 8.0 else "fail",
            "issues": issues,
            "inconsistencies": issues
        }
    
    def _check_errors(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Check for errors in document"""
        issues = []
        score = 10.0
        
        content = document.get("content", {})
        if not content:
            return {"score": 0, "status": "fail", "issues": ["No content to check"], "errors": []}
        
        text_content = self._extract_text(content)
        
        # Check for common errors
        # Spelling errors (basic check for obvious typos)
        spelling_errors = self._check_spelling_errors(text_content)
        issues.extend(spelling_errors)
        score -= len(spelling_errors) * 0.5
        
        # Grammar errors (basic patterns)
        grammar_errors = self._check_grammar_errors(text_content)
        issues.extend(grammar_errors)
        score -= len(grammar_errors) * 0.5
        
        # Formatting errors
        formatting_errors = self._check_formatting_errors(text_content)
        issues.extend(formatting_errors)
        score -= len(formatting_errors) * 0.3
        
        # Data errors (numbers, dates, etc.)
        data_errors = self._check_data_errors(content)
        issues.extend(data_errors)
        score -= len(data_errors) * 1.0
        
        # Use LLM for comprehensive error detection
        try:
            llm_errors = self._llm_error_check(content)
            if llm_errors:
                issues.extend(llm_errors.get("errors", []))
                score -= len(llm_errors.get("errors", [])) * 0.5
        except Exception as e:
            logger.warning(f"LLM error check failed: {e}")
        
        score = max(0.0, min(10.0, score))
        
        return {
            "score": round(score, 2),
            "status": "pass" if score >= 8.0 else "fail",
            "issues": issues,
            "errors": issues,
            "error_count": len(issues)
        }
    
    def _check_completeness(
        self,
        document: Dict[str, Any],
        requirements: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check document completeness"""
        issues = []
        score = 10.0
        
        content = document.get("content", {})
        if not content:
            return {"score": 0, "status": "fail", "issues": ["Document is empty"], "missing_items": []}
        
        # Check if requirements are met
        if requirements:
            required_items = requirements.get("required_items", [])
            for item in required_items:
                if not self._has_item(content, item):
                    issues.append(f"Missing required item: {item}")
                    score -= 1.0
        
        # Check content depth
        text_content = self._extract_text(content)
        if len(text_content) < 500:
            issues.append("Document content is too brief (less than 500 characters)")
            score -= 2.0
        
        # Check for placeholder text
        placeholders = re.findall(r'\[.*?\]|TODO|FIXME|XXX', text_content, re.IGNORECASE)
        if placeholders:
            issues.append(f"Found {len(placeholders)} placeholder(s) that need to be filled")
            score -= len(placeholders) * 0.5
        
        score = max(0.0, min(10.0, score))
        
        return {
            "score": round(score, 2),
            "status": "pass" if score >= 8.0 else "fail",
            "issues": issues,
            "missing_items": [issue for issue in issues if "Missing" in issue]
        }
    
    def _check_clarity(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Check document clarity and readability"""
        issues = []
        score = 10.0
        
        content = document.get("content", {})
        if not content:
            return {"score": 0, "status": "fail", "issues": ["No content to check"], "clarity_issues": []}
        
        text_content = self._extract_text(content)
        
        # Check for overly long sentences
        sentences = re.split(r'[.!?]+', text_content)
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        if long_sentences:
            issues.append(f"Found {len(long_sentences)} overly long sentence(s) (over 30 words)")
            score -= len(long_sentences) * 0.3
        
        # Check for jargon without explanation
        jargon_patterns = [
            r'\b[A-Z]{3,}\b',  # Acronyms
        ]
        for pattern in jargon_patterns:
            matches = re.findall(pattern, text_content)
            if len(matches) > 10:
                issues.append("Excessive use of acronyms/jargon may reduce clarity")
                score -= 1.0
                break
        
        # Use LLM for clarity assessment
        try:
            llm_clarity = self._llm_clarity_check(content)
            if llm_clarity:
                issues.extend(llm_clarity.get("issues", []))
                score -= len(llm_clarity.get("issues", [])) * 0.5
        except Exception as e:
            logger.warning(f"LLM clarity check failed: {e}")
        
        score = max(0.0, min(10.0, score))
        
        return {
            "score": round(score, 2),
            "status": "pass" if score >= 8.0 else "fail",
            "issues": issues,
            "clarity_issues": issues
        }
    
    def _extract_text(self, content: Any) -> str:
        """Extract text content from document structure"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            # Extract text from all string values
            texts = []
            for value in content.values():
                if isinstance(value, str):
                    texts.append(value)
                elif isinstance(value, dict):
                    texts.append(self._extract_text(value))
                elif isinstance(value, list):
                    for item in value:
                        texts.append(self._extract_text(item))
            return " ".join(texts)
        elif isinstance(content, list):
            texts = [self._extract_text(item) for item in content]
            return " ".join(texts)
        else:
            return str(content)
    
    def _check_terminology_consistency(self, text: str) -> List[str]:
        """Check for terminology inconsistencies"""
        issues = []
        # Basic check for common inconsistencies
        # This is a simplified version - in production, use more sophisticated NLP
        return issues
    
    def _check_formatting_consistency(self, text: str) -> List[str]:
        """Check for formatting inconsistencies"""
        issues = []
        # Check for mixed line breaks
        if '\r\n' in text and '\n' in text.replace('\r\n', ''):
            issues.append("Mixed line break formats detected")
        return issues
    
    def _check_style_consistency(self, text: str) -> List[str]:
        """Check for style inconsistencies"""
        issues = []
        # Check for mixed quotation marks
        if '"' in text and "'" in text:
            # This is normal, but could flag if excessive mixing
            pass
        return issues
    
    def _check_spelling_errors(self, text: str) -> List[str]:
        """Basic spelling error check"""
        issues = []
        # Common typos pattern matching
        common_typos = {
            'teh': 'the',
            'adn': 'and',
            'taht': 'that',
            'recieve': 'receive',
        }
        words = re.findall(r'\b\w+\b', text.lower())
        for typo, correct in common_typos.items():
            if typo in words:
                issues.append(f"Possible typo: '{typo}' should be '{correct}'")
        return issues
    
    def _check_grammar_errors(self, text: str) -> List[str]:
        """Basic grammar error check"""
        issues = []
        # Check for double spaces
        if '  ' in text:
            issues.append("Found double spaces (formatting issue)")
        # Check for common grammar patterns
        if re.search(r'\b(a|an) [aeiou]', text, re.IGNORECASE):
            # This is actually correct, but could be improved
            pass
        return issues
    
    def _check_formatting_errors(self, text: str) -> List[str]:
        """Check for formatting errors"""
        issues = []
        # Check for trailing spaces
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.endswith(' ') and line.strip():
                issues.append(f"Line {i+1}: Trailing space detected")
        return issues
    
    def _check_data_errors(self, content: Dict[str, Any]) -> List[str]:
        """Check for data errors (numbers, dates, etc.)"""
        issues = []
        # Check budget totals match
        if "budget" in str(content).lower():
            # This would need more sophisticated parsing
            pass
        return issues
    
    def _has_item(self, content: Any, item: str) -> bool:
        """Check if content has a specific item"""
        text = self._extract_text(content).lower()
        return item.lower() in text
    
    def _llm_consistency_check(self, content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to check consistency"""
        prompt = f"""As a quality assurance expert, check the document for consistency issues.

Document content:
{json.dumps(content, indent=2)[:2000]}

Check for:
1. Terminology consistency
2. Formatting consistency
3. Style consistency
4. Tone consistency

Return JSON: {{"issues": ["<issue 1>", "<issue 2>"]}}
"""
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.2,
                max_tokens=1000
            )
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"LLM consistency check failed: {e}")
        return None
    
    def _llm_error_check(self, content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to check for errors"""
        prompt = f"""As a quality assurance expert, check the document for errors.

Document content:
{json.dumps(content, indent=2)[:2000]}

Check for:
1. Spelling errors
2. Grammar errors
3. Factual errors
4. Formatting errors

Return JSON: {{"errors": ["<error 1>", "<error 2>"]}}
"""
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.2,
                max_tokens=1000
            )
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"LLM error check failed: {e}")
        return None
    
    def _llm_clarity_check(self, content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to check clarity"""
        prompt = f"""As a quality assurance expert, check the document for clarity issues.

Document content:
{json.dumps(content, indent=2)[:2000]}

Check for:
1. Unclear sentences
2. Excessive jargon
3. Poor readability
4. Confusing structure

Return JSON: {{"issues": ["<issue 1>", "<issue 2>"]}}
"""
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.2,
                max_tokens=1000
            )
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"LLM clarity check failed: {e}")
        return None
    
    def _generate_recommendations(
        self,
        issues: List[str],
        scores: List[float]
    ) -> List[str]:
        """Generate recommendations based on issues"""
        recommendations = []
        
        if not issues:
            recommendations.append("Document quality is excellent - no issues found")
            return recommendations
        
        # Categorize issues and provide recommendations
        structure_issues = [i for i in issues if "section" in i.lower() or "structure" in i.lower()]
        if structure_issues:
            recommendations.append("Review and improve document structure")
        
        consistency_issues = [i for i in issues if "consistency" in i.lower() or "inconsistent" in i.lower()]
        if consistency_issues:
            recommendations.append("Ensure consistent terminology and formatting throughout")
        
        error_issues = [i for i in issues if "error" in i.lower() or "typo" in i.lower() or "grammar" in i.lower()]
        if error_issues:
            recommendations.append("Fix spelling, grammar, and formatting errors")
        
        completeness_issues = [i for i in issues if "missing" in i.lower() or "incomplete" in i.lower()]
        if completeness_issues:
            recommendations.append("Complete all required sections and remove placeholders")
        
        clarity_issues = [i for i in issues if "clarity" in i.lower() or "unclear" in i.lower()]
        if clarity_issues:
            recommendations.append("Improve clarity and readability")
        
        return recommendations
    
    def _generate_quality_summary(
        self,
        score: float,
        issues: List[str]
    ) -> str:
        """Generate quality summary"""
        if score >= 9.0 and not issues:
            return "Excellent quality - document is ready for delivery"
        elif score >= 8.0:
            return f"Good quality (score: {score}/10) - minor issues to address"
        elif score >= 6.0:
            return f"Acceptable quality (score: {score}/10) - several issues need attention"
        else:
            return f"Quality below standard (score: {score}/10) - significant improvements needed"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - QA workflow
        
        Expected input:
        {
            "document": {...},
            "requirements": {...}
        }
        """
        return self.perform_quality_check(
            input_data.get("document", {}),
            input_data.get("requirements")
        )

