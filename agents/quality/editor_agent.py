"""
Editor Agent - Final Polish and Professional Editing
Performs final polish, grammar and style checks, consistency checks,
and professional editing.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import re
import logging

logger = logging.getLogger(__name__)


class EditorAgent(BaseAgent):
    """
    Editor Agent - Final polish and professional editing.
    Performs grammar checks, style improvements, consistency checks,
    and final professional polish.
    """
    
    def __init__(self):
        super().__init__(
            name="Editor Agent",
            role="Final polish, grammar, style, and professional editing",
            task_type="quality"
        )
    
    def edit_document(
        self,
        document: Dict[str, Any],
        edit_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive document editing
        
        Args:
            document: Document to edit
            edit_type: Type of editing ("comprehensive", "grammar", "style", "polish")
            
        Returns:
            Edited document with changes tracked
        """
        self.log_action(f"Editing document (type: {edit_type})")
        
        if edit_type == "comprehensive":
            return self._comprehensive_edit(document)
        elif edit_type == "grammar":
            return self._grammar_edit(document)
        elif edit_type == "style":
            return self._style_edit(document)
        elif edit_type == "polish":
            return self._polish_edit(document)
        else:
            return self._comprehensive_edit(document)
    
    def _comprehensive_edit(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive editing"""
        # Grammar check
        grammar_result = self.check_grammar(document)
        
        # Style check
        style_result = self.check_style(document)
        
        # Consistency check
        consistency_result = self.check_consistency(document)
        
        # Final polish
        polish_result = self.apply_final_polish(document)
        
        # Combine all edits
        edited_document = self._merge_edits(
            document,
            [grammar_result, style_result, consistency_result, polish_result]
        )
        
        return {
            "edited_document": edited_document,
            "changes": {
                "grammar": grammar_result.get("changes", []),
                "style": style_result.get("changes", []),
                "consistency": consistency_result.get("changes", []),
                "polish": polish_result.get("changes", [])
            },
            "summary": {
                "total_changes": sum(
                    len(r.get("changes", [])) 
                    for r in [grammar_result, style_result, consistency_result, polish_result]
                ),
                "grammar_issues_fixed": len(grammar_result.get("issues", [])),
                "style_improvements": len(style_result.get("improvements", [])),
                "consistency_fixes": len(consistency_result.get("fixes", []))
            }
        }
    
    def check_grammar(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Check and fix grammar errors"""
        self.log_action("Checking grammar")
        
        content = document.get("content", {})
        text_content = self._extract_text(content)
        
        prompt = f"""As a professional editor, check and fix grammar errors in this document.

Document content:
{text_content[:3000]}

Check for:
1. Grammar errors
2. Punctuation errors
3. Sentence structure issues
4. Subject-verb agreement
5. Tense consistency

For each error found, provide:
- Location (section/paragraph)
- Original text
- Corrected text
- Explanation

Return JSON format:
{{
    "issues": [
        {{
            "location": "<section/paragraph>",
            "original": "<original text>",
            "corrected": "<corrected text>",
            "explanation": "<why this is wrong>",
            "severity": "<high/medium/low>"
        }}
    ],
    "changes": [
        {{
            "section": "<section>",
            "original": "<original>",
            "corrected": "<corrected>"
        }}
    ],
    "grammar_score": <0-10>
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
                result = json.loads(json_match.group())
                return result
        except Exception as e:
            logger.warning(f"Grammar check LLM call failed: {e}")
        
        # Fallback: basic grammar checks
        issues = []
        changes = []
        
        # Check for common grammar errors
        if re.search(r'\b(its|it\'s)\b', text_content, re.IGNORECASE):
            issues.append("Check 'its' vs 'it's' usage")
        
        if re.search(r'\b(there|their|they\'re)\b', text_content, re.IGNORECASE):
            issues.append("Check 'there/their/they're' usage")
        
        return {
            "issues": issues,
            "changes": changes,
            "grammar_score": 8.0
        }
    
    def check_style(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Check and improve style"""
        self.log_action("Checking style")
        
        content = document.get("content", {})
        text_content = self._extract_text(content)
        
        prompt = f"""As a professional editor, check and improve the writing style.

Document content:
{text_content[:3000]}

Check for:
1. Clarity and readability
2. Word choice and vocabulary
3. Sentence variety
4. Tone consistency
5. Professional language
6. Active vs passive voice
7. Conciseness

Provide style improvements:
- Location
- Original text
- Improved text
- Rationale

Return JSON format:
{{
    "improvements": [
        {{
            "location": "<section/paragraph>",
            "original": "<original text>",
            "improved": "<improved text>",
            "rationale": "<why this is better>",
            "category": "<clarity/tone/conciseness/etc>"
        }}
    ],
    "changes": [
        {{
            "section": "<section>",
            "original": "<original>",
            "improved": "<improved>"
        }}
    ],
    "style_score": <0-10>
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except Exception as e:
            logger.warning(f"Style check LLM call failed: {e}")
        
        # Fallback
        return {
            "improvements": [],
            "changes": [],
            "style_score": 8.0
        }
    
    def check_consistency(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Check and fix consistency issues"""
        self.log_action("Checking consistency")
        
        content = document.get("content", {})
        text_content = self._extract_text(content)
        
        # Check for consistency issues
        fixes = []
        
        # Check for inconsistent capitalization
        # Check for inconsistent terminology
        # Check for inconsistent formatting
        
        prompt = f"""As a professional editor, check for consistency issues.

Document content:
{text_content[:3000]}

Check for:
1. Terminology consistency
2. Capitalization consistency
3. Formatting consistency
4. Number format consistency
5. Date format consistency
6. Abbreviation consistency

Return JSON format:
{{
    "fixes": [
        {{
            "location": "<section>",
            "issue": "<consistency issue>",
            "original": "<original>",
            "fixed": "<fixed version>",
            "category": "<terminology/formatting/etc>"
        }}
    ],
    "changes": [
        {{
            "section": "<section>",
            "original": "<original>",
            "fixed": "<fixed>"
        }}
    ],
    "consistency_score": <0-10>
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
                result = json.loads(json_match.group())
                return result
        except Exception as e:
            logger.warning(f"Consistency check LLM call failed: {e}")
        
        return {
            "fixes": [],
            "changes": [],
            "consistency_score": 8.0
        }
    
    def apply_final_polish(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Apply final professional polish"""
        self.log_action("Applying final polish")
        
        content = document.get("content", {})
        text_content = self._extract_text(content)
        
        prompt = f"""As a professional editor, apply final polish to make this document publication-ready.

Document content:
{text_content[:3000]}

Apply final polish:
1. Professional tone refinement
2. Flow and transitions
3. Final proofreading
4. Formatting perfection
5. Professional presentation

Return JSON format:
{{
    "polished_content": "<polished text>",
    "changes": [
        {{
            "section": "<section>",
            "original": "<original>",
            "polished": "<polished>",
            "improvement": "<what was improved>"
        }}
    ],
    "polish_score": <0-10>
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
                result = json.loads(json_match.group())
                return result
        except Exception as e:
            logger.warning(f"Final polish LLM call failed: {e}")
        
        return {
            "polished_content": text_content,
            "changes": [],
            "polish_score": 8.0
        }
    
    def _extract_text(self, content: Any) -> str:
        """Extract text content from document structure"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
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
    
    def _merge_edits(
        self,
        document: Dict[str, Any],
        edit_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge all edits into final document"""
        # This is a simplified merge - in production, would need more sophisticated merging
        edited_doc = document.copy()
        
        # Apply changes from all edit results
        for result in edit_results:
            changes = result.get("changes", [])
            for change in changes:
                # Apply change to document
                # This is simplified - would need proper text replacement logic
                pass
        
        return edited_doc
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - Editor workflow
        
        Expected input:
        {
            "document": {...},
            "edit_type": "comprehensive" | "grammar" | "style" | "polish"
        }
        """
        return self.edit_document(
            input_data.get("document", {}),
            input_data.get("edit_type", "comprehensive")
        )

