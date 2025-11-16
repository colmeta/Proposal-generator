"""
Persuasion Optimizer Agent
Maximizes win probability through messaging optimization,
A/B testing suggestions, and persuasion techniques.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class PersuasionOptimizerAgent(BaseAgent):
    """
    Persuasion Optimizer Agent - Maximizes win probability.
    Optimizes messaging, suggests A/B tests, and applies persuasion techniques.
    """
    
    def __init__(self):
        super().__init__(
            name="Persuasion Optimizer",
            role="Maximize win probability through optimized messaging and persuasion",
            task_type="strategy"
        )
    
    def optimize_messaging(
        self,
        proposal: Dict[str, Any],
        target_audience: Dict[str, Any],
        competitive_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize messaging for maximum persuasion
        
        Args:
            proposal: Proposal document
            target_audience: Target audience information
            competitive_context: Competitive context and positioning
            
        Returns:
            Optimized messaging with recommendations and improvements
        """
        self.log_action("Optimizing messaging for maximum persuasion")
        
        prompt = f"""As a persuasion expert, optimize the proposal messaging to maximize win probability.

Proposal:
{json.dumps(proposal.get("content", {}), indent=2)[:3000]}

Target Audience:
{json.dumps(target_audience, indent=2)}

Competitive Context:
{json.dumps(competitive_context or {}, indent=2)}

Optimize for:
1. Emotional appeal and connection
2. Clear value proposition
3. Compelling call-to-action
4. Trust and credibility signals
5. Differentiation from competitors
6. Addressing audience pain points

Return JSON format:
{{
    "optimized_messaging": {{
        "headline": "<optimized headline>",
        "value_proposition": "<optimized value prop>",
        "key_messages": ["<message 1>", "<message 2>"],
        "emotional_appeals": ["<appeal 1>", "<appeal 2>"],
        "trust_signals": ["<signal 1>", "<signal 2>"],
        "call_to_action": "<optimized CTA>"
    }},
    "improvements": [
        {{
            "section": "<section name>",
            "current": "<current text>",
            "optimized": "<optimized text>",
            "rationale": "<why this improves persuasion>"
        }}
    ],
    "persuasion_techniques_applied": ["<technique 1>", "<technique 2>"],
    "win_probability_impact": "<estimated impact on win probability>",
    "recommendations": ["<recommendation 1>", "<recommendation 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.6,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                optimization = json.loads(json_match.group())
                return optimization
        except Exception as e:
            logger.warning(f"Messaging optimization LLM call failed: {e}")
        
        # Fallback optimization
        return {
            "optimized_messaging": {
                "headline": proposal.get("content", {}).get("title", "Proposal"),
                "value_proposition": "Delivering exceptional value",
                "key_messages": [],
                "emotional_appeals": [],
                "trust_signals": [],
                "call_to_action": "Approve this proposal"
            },
            "improvements": [],
            "persuasion_techniques_applied": [],
            "win_probability_impact": "Moderate",
            "recommendations": ["Review messaging for clarity and impact"]
        }
    
    def suggest_ab_tests(
        self,
        proposal: Dict[str, Any],
        key_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Suggest A/B tests for key proposal elements
        
        Args:
            proposal: Proposal document
            key_sections: Key sections to test (optional)
            
        Returns:
            A/B test suggestions with variants and metrics
        """
        self.log_action("Generating A/B test suggestions")
        
        prompt = f"""As a persuasion expert, suggest A/B tests to optimize proposal effectiveness.

Proposal sections:
{json.dumps(proposal.get("content", {}), indent=2)[:2000]}

Key sections to test: {key_sections or "All sections"}

Suggest A/B tests for:
1. Headlines and titles
2. Value propositions
3. Call-to-action statements
4. Opening paragraphs
5. Key messaging points

For each test, provide:
- Test name
- Element to test
- Variant A (current)
- Variant B (alternative)
- Expected impact
- Success metric

Return JSON format:
{{
    "ab_tests": [
        {{
            "test_name": "<test name>",
            "element": "<element to test>",
            "variant_a": "<current version>",
            "variant_b": "<alternative version>",
            "rationale": "<why test this>",
            "expected_impact": "<high/medium/low>",
            "success_metric": "<metric to measure>"
        }}
    ],
    "testing_priority": ["<test 1>", "<test 2>"],
    "recommendations": ["<recommendation 1>", "<recommendation 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.7,
                max_tokens=2500
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                tests = json.loads(json_match.group())
                return tests
        except Exception as e:
            logger.warning(f"A/B test suggestion LLM call failed: {e}")
        
        # Fallback suggestions
        return {
            "ab_tests": [
                {
                    "test_name": "Headline Test",
                    "element": "Proposal headline",
                    "variant_a": "Current headline",
                    "variant_b": "Alternative headline",
                    "rationale": "Headlines significantly impact first impressions",
                    "expected_impact": "high",
                    "success_metric": "Engagement and approval rate"
                }
            ],
            "testing_priority": ["Headline", "Value Proposition"],
            "recommendations": ["Test key messaging elements before final submission"]
        }
    
    def apply_persuasion_techniques(
        self,
        proposal: Dict[str, Any],
        techniques: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Apply persuasion techniques to proposal
        
        Args:
            proposal: Proposal document
            techniques: Specific techniques to apply (optional)
            
        Returns:
            Proposal with applied persuasion techniques and explanations
        """
        self.log_action("Applying persuasion techniques")
        
        available_techniques = techniques or [
            "social_proof",
            "scarcity",
            "authority",
            "reciprocity",
            "commitment",
            "liking",
            "storytelling",
            "emotional_appeal"
        ]
        
        prompt = f"""As a persuasion expert, apply proven persuasion techniques to this proposal.

Proposal:
{json.dumps(proposal.get("content", {}), indent=2)[:3000]}

Techniques to apply: {', '.join(available_techniques)}

For each technique, provide:
1. Where to apply it
2. How to apply it
3. Specific text suggestions
4. Expected impact

Return JSON format:
{{
    "applied_techniques": [
        {{
            "technique": "<technique name>",
            "description": "<what this technique does>",
            "application": "<where/how to apply>",
            "suggested_text": "<specific text suggestion>",
            "expected_impact": "<high/medium/low>",
            "rationale": "<why this works>"
        }}
    ],
    "improved_proposal": {{
        "sections": {{
            "<section>": "<improved text>"
        }}
    }},
    "persuasion_score": <0-10>,
    "recommendations": ["<recommendation 1>", "<recommendation 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.6,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except Exception as e:
            logger.warning(f"Persuasion techniques LLM call failed: {e}")
        
        # Fallback
        return {
            "applied_techniques": [
                {
                    "technique": "social_proof",
                    "description": "Showcase past successes and testimonials",
                    "application": "Add success stories section",
                    "suggested_text": "Previous successful projects...",
                    "expected_impact": "high",
                    "rationale": "Builds trust and credibility"
                }
            ],
            "improved_proposal": {},
            "persuasion_score": 7.0,
            "recommendations": ["Apply social proof and authority signals"]
        }
    
    def maximize_win_probability(
        self,
        proposal: Dict[str, Any],
        requirements: Dict[str, Any],
        competitive_context: Dict[str, Any],
        target_audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive win probability maximization
        
        Args:
            proposal: Proposal document
            requirements: Funder requirements
            competitive_context: Competitive context
            target_audience: Target audience
            
        Returns:
            Comprehensive optimization with win probability assessment
        """
        self.log_action("Maximizing win probability")
        
        # Optimize messaging
        messaging_optimization = self.optimize_messaging(
            proposal, target_audience, competitive_context
        )
        
        # Apply persuasion techniques
        persuasion_applied = self.apply_persuasion_techniques(proposal)
        
        # Suggest A/B tests
        ab_tests = self.suggest_ab_tests(proposal)
        
        # Assess win probability
        win_probability = self._assess_win_probability(
            proposal, requirements, competitive_context, messaging_optimization
        )
        
        return {
            "win_probability": win_probability,
            "messaging_optimization": messaging_optimization,
            "persuasion_techniques": persuasion_applied,
            "ab_test_suggestions": ab_tests,
            "optimization_summary": self._generate_optimization_summary(
                win_probability, messaging_optimization, persuasion_applied
            ),
            "next_steps": self._generate_next_steps(win_probability, ab_tests)
        }
    
    def _assess_win_probability(
        self,
        proposal: Dict[str, Any],
        requirements: Dict[str, Any],
        competitive_context: Dict[str, Any],
        optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess win probability after optimization"""
        prompt = f"""As a proposal expert, assess the win probability of this optimized proposal.

Proposal:
{json.dumps(proposal.get("content", {}), indent=2)[:2000]}

Requirements:
{json.dumps(requirements, indent=2)}

Competitive Context:
{json.dumps(competitive_context, indent=2)}

Optimization Applied:
{json.dumps(optimization, indent=2)}

Assess win probability (0-100%) and provide:
1. Overall probability
2. Key strengths
3. Remaining weaknesses
4. Improvement suggestions

Return JSON:
{{
    "probability_percent": <0-100>,
    "probability_level": "<very_high/high/medium/low>",
    "key_strengths": ["<strength 1>", "<strength 2>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=1500
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Win probability assessment failed: {e}")
        
        # Fallback assessment
        return {
            "probability_percent": 70,
            "probability_level": "medium",
            "key_strengths": ["Clear value proposition"],
            "weaknesses": ["Could improve differentiation"],
            "improvement_suggestions": ["Strengthen competitive positioning"]
        }
    
    def _generate_optimization_summary(
        self,
        win_probability: Dict[str, Any],
        messaging: Dict[str, Any],
        persuasion: Dict[str, Any]
    ) -> str:
        """Generate optimization summary"""
        prob = win_probability.get("probability_percent", 0)
        level = win_probability.get("probability_level", "medium")
        
        summary = f"Win probability: {prob}% ({level})\n"
        summary += f"Applied {len(persuasion.get('applied_techniques', []))} persuasion techniques\n"
        summary += f"Generated {len(messaging.get('improvements', []))} messaging improvements"
        
        return summary
    
    def _generate_next_steps(
        self,
        win_probability: Dict[str, Any],
        ab_tests: Dict[str, Any]
    ) -> List[str]:
        """Generate next steps"""
        steps = []
        
        prob = win_probability.get("probability_percent", 0)
        if prob < 70:
            steps.append("Continue optimizing messaging and value proposition")
        
        if ab_tests.get("ab_tests"):
            steps.append(f"Consider running {len(ab_tests['ab_tests'])} A/B tests before final submission")
        
        weaknesses = win_probability.get("weaknesses", [])
        if weaknesses:
            steps.append(f"Address {len(weaknesses)} identified weaknesses")
        
        return steps
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - Persuasion optimization workflow
        
        Expected input:
        {
            "action": "optimize_messaging" | "suggest_ab_tests" | 
                      "apply_persuasion_techniques" | "maximize_win_probability",
            "proposal": {...},
            ...
        }
        """
        action = input_data.get("action", "maximize_win_probability")
        
        if action == "optimize_messaging":
            return self.optimize_messaging(
                input_data.get("proposal", {}),
                input_data.get("target_audience", {}),
                input_data.get("competitive_context")
            )
        elif action == "suggest_ab_tests":
            return self.suggest_ab_tests(
                input_data.get("proposal", {}),
                input_data.get("key_sections")
            )
        elif action == "apply_persuasion_techniques":
            return self.apply_persuasion_techniques(
                input_data.get("proposal", {}),
                input_data.get("techniques")
            )
        elif action == "maximize_win_probability":
            return self.maximize_win_probability(
                input_data.get("proposal", {}),
                input_data.get("requirements", {}),
                input_data.get("competitive_context", {}),
                input_data.get("target_audience", {})
            )
        else:
            # Default: maximize win probability
            return self.maximize_win_probability(
                input_data.get("proposal", {}),
                input_data.get("requirements", {}),
                input_data.get("competitive_context", {}),
                input_data.get("target_audience", {})
            )

