"""
Success Analyzer Agent
Studies winning proposals from public sources and extracts success patterns
"""

import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
from services.web_scraper import web_scraper


class SuccessAnalyzerAgent(BaseAgent):
    """
    Success Analyzer Agent - Studies winning proposals and extracts patterns
    """
    
    def __init__(self):
        super().__init__(
            name="Success Analyzer Agent",
            role="Analyze winning proposals and extract success patterns",
            task_type="research"
        )
        self.patterns_dir = Path("data/success_patterns")
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_file = self.patterns_dir / "patterns.json"
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load existing success patterns"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load patterns: {e}")
        
        return {
            "patterns": [],
            "common_elements": [],
            "winning_strategies": [],
            "statistics": {}
        }
    
    def analyze_winning_proposal(
        self,
        proposal_content: str,
        funder_name: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a winning proposal and extract patterns
        
        Args:
            proposal_content: Content of the winning proposal
            funder_name: Name of the funder (optional)
            source: Source of the proposal (optional)
        
        Returns:
            Dict with extracted patterns and insights
        """
        self.log_action(f"Analyzing winning proposal from {funder_name or 'unknown funder'}")
        
        # Use LLM to analyze the proposal
        analysis = self._analyze_with_llm(proposal_content, funder_name)
        
        # Extract patterns
        patterns = self._extract_patterns(analysis)
        
        # Update pattern database
        self._update_patterns(patterns, funder_name, source)
        
        return {
            "analysis": analysis,
            "patterns": patterns,
            "funder": funder_name,
            "source": source
        }
    
    def _analyze_with_llm(
        self,
        proposal_content: str,
        funder_name: Optional[str]
    ) -> Dict[str, Any]:
        """Use LLM to analyze proposal content"""
        content_preview = proposal_content[:10000]  # Limit content length
        
        prompt = f"""Analyze this winning funding proposal and identify what made it successful.

Funder: {funder_name or "Unknown"}

Proposal Content:
{content_preview}

Analyze and return a JSON object with:
{{
    "strengths": ["strength1", "strength2", ...],
    "key_elements": ["element1", "element2", ...],
    "writing_style": "description of writing style",
    "structure": "description of proposal structure",
    "persuasion_techniques": ["technique1", "technique2", ...],
    "data_usage": "how data/evidence was used",
    "differentiation": "how it stood out",
    "alignment": "how it aligned with funder priorities",
    "winning_factors": ["factor1", "factor2", ...],
    "recommendations": ["recommendation1", "recommendation2", ...]
}}

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=3000
            )
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse LLM response: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error analyzing proposal: {e}")
            return {}
    
    def _extract_patterns(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patterns from analysis"""
        return {
            "winning_factors": analysis.get("winning_factors", []),
            "common_elements": analysis.get("key_elements", []),
            "persuasion_techniques": analysis.get("persuasion_techniques", []),
            "structure_patterns": analysis.get("structure", ""),
            "writing_style": analysis.get("writing_style", ""),
            "data_usage_patterns": analysis.get("data_usage", ""),
            "differentiation_strategies": analysis.get("differentiation", "")
        }
    
    def _update_patterns(
        self,
        new_patterns: Dict[str, Any],
        funder_name: Optional[str],
        source: Optional[str]
    ):
        """Update pattern database with new patterns"""
        # Add to patterns list
        pattern_entry = {
            "patterns": new_patterns,
            "funder": funder_name,
            "source": source,
            "timestamp": str(Path().cwd())  # Simple timestamp placeholder
        }
        
        self.patterns["patterns"].append(pattern_entry)
        
        # Update common elements (aggregate)
        all_elements = []
        for entry in self.patterns["patterns"]:
            all_elements.extend(entry["patterns"].get("common_elements", []))
        
        # Count frequency
        from collections import Counter
        element_counts = Counter(all_elements)
        self.patterns["common_elements"] = [
            {"element": elem, "frequency": count}
            for elem, count in element_counts.most_common(20)
        ]
        
        # Update winning strategies
        all_factors = []
        for entry in self.patterns["patterns"]:
            all_factors.extend(entry["patterns"].get("winning_factors", []))
        
        factor_counts = Counter(all_factors)
        self.patterns["winning_strategies"] = [
            {"strategy": factor, "frequency": count}
            for factor, count in factor_counts.most_common(15)
        ]
        
        # Update statistics
        self.patterns["statistics"] = {
            "total_proposals_analyzed": len(self.patterns["patterns"]),
            "unique_funders": len(set(
                entry.get("funder") for entry in self.patterns["patterns"]
                if entry.get("funder")
            )),
            "top_elements": self.patterns["common_elements"][:5],
            "top_strategies": self.patterns["winning_strategies"][:5]
        }
        
        # Save patterns
        self._save_patterns()
    
    def _save_patterns(self):
        """Save patterns to file"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save patterns: {e}")
    
    def get_success_patterns(self) -> Dict[str, Any]:
        """Get all success patterns"""
        return self.patterns
    
    def get_recommendations(self, funder_name: Optional[str] = None) -> List[str]:
        """Get recommendations based on success patterns"""
        recommendations = []
        
        # Get top strategies
        for strategy in self.patterns.get("winning_strategies", [])[:5]:
            recommendations.append(
                f"Use: {strategy['strategy']} (appears in {strategy['frequency']} winning proposals)"
            )
        
        # Get top elements
        for element in self.patterns.get("common_elements", [])[:5]:
            recommendations.append(
                f"Include: {element['element']} (found in {element['frequency']} winning proposals)"
            )
        
        return recommendations
    
    def research_public_winners(
        self,
        funder_name: str,
        search_terms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Research publicly available winning proposals
        
        Args:
            funder_name: Name of the funder
            search_terms: Optional search terms
        
        Returns:
            Dict with research results
        """
        self.log_action(f"Researching public winners for {funder_name}")
        
        if not search_terms:
            search_terms = [
                f"{funder_name} grant winners",
                f"{funder_name} funded projects",
                f"{funder_name} successful proposals"
            ]
        
        # Use LLM to find sources
        prompt = f"""Find public sources where we can learn about winning proposals from {funder_name}.

Search terms: {', '.join(search_terms)}

Provide a list of:
1. Websites that publish winning proposals
2. Public databases with funded projects
3. News articles about grant winners
4. Case studies or success stories

Return as JSON:
{{
    "sources": [
        {{
            "name": "source name",
            "url": "url",
            "description": "what information is available"
        }}
    ],
    "search_strategies": ["strategy1", "strategy2", ...]
}}

Return ONLY valid JSON.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.GEMINI,
                temperature=0.5,
                max_tokens=2000
            )
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                sources_data = json.loads(json_match.group())
            else:
                sources_data = json.loads(response)
            
            return {
                "funder": funder_name,
                "sources": sources_data.get("sources", []),
                "search_strategies": sources_data.get("search_strategies", []),
                "research_complete": True
            }
        
        except Exception as e:
            self.logger.error(f"Error researching public winners: {e}")
            return {
                "funder": funder_name,
                "error": str(e),
                "research_complete": False
            }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - analyze proposal or research winners"""
        if "proposal_content" in input_data:
            # Analyze a proposal
            return {
                "status": "success",
                "result": self.analyze_winning_proposal(
                    proposal_content=input_data["proposal_content"],
                    funder_name=input_data.get("funder_name"),
                    source=input_data.get("source")
                )
            }
        elif "funder_name" in input_data:
            # Research public winners
            return {
                "status": "success",
                "result": self.research_public_winners(
                    funder_name=input_data["funder_name"],
                    search_terms=input_data.get("search_terms")
                )
            }
        elif "get_patterns" in input_data:
            # Get success patterns
            return {
                "status": "success",
                "patterns": self.get_success_patterns(),
                "recommendations": self.get_recommendations(
                    input_data.get("funder_name")
                )
            }
        else:
            raise ValueError("Invalid input: must provide proposal_content, funder_name, or get_patterns")

