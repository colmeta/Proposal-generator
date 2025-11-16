"""
Marketing Director Agent
Handles brand positioning, messaging development, differentiation analysis,
value proposition development, target audience analysis, and competitive positioning.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class MarketingDirectorAgent(BaseAgent):
    """
    Marketing Director Agent - Marketing strategy and positioning specialist.
    Develops brand positioning, messaging, value propositions, and competitive strategies.
    """
    
    def __init__(self):
        super().__init__(
            name="Marketing Director",
            role="Brand positioning, messaging, and competitive strategy",
            task_type="strategy"
        )
    
    def develop_brand_positioning(
        self,
        project_scope: Dict[str, Any],
        target_audience: Optional[Dict[str, Any]] = None,
        competitive_landscape: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Develop brand positioning strategy
        
        Args:
            project_scope: Project scope and objectives
            target_audience: Target audience information
            competitive_landscape: Competitive analysis data
            
        Returns:
            Brand positioning strategy with positioning statement and key messages
        """
        self.log_action("Developing brand positioning strategy")
        
        prompt = f"""As a Marketing Director, develop a compelling brand positioning strategy.

Project Scope:
{json.dumps(project_scope, indent=2)}

Target Audience:
{json.dumps(target_audience or {}, indent=2)}

Competitive Landscape:
{json.dumps(competitive_landscape or {}, indent=2)}

Create a brand positioning strategy including:
1. Positioning statement (who we are, what we do, why we're different)
2. Brand personality and attributes
3. Key differentiators
4. Unique value proposition
5. Target market segments
6. Positioning map (where we sit vs competitors)

Return JSON format:
{{
    "positioning_statement": "<clear positioning statement>",
    "brand_personality": ["<attribute 1>", "<attribute 2>"],
    "key_differentiators": ["<differentiator 1>", "<differentiator 2>"],
    "unique_value_proposition": "<value proposition>",
    "target_segments": [
        {{
            "segment": "<segment name>",
            "characteristics": "<description>",
            "needs": ["<need 1>", "<need 2>"]
        }}
    ],
    "positioning_map": {{
        "our_position": "<description>",
        "competitive_positioning": "<how we compare>"
    }},
    "key_messages": ["<message 1>", "<message 2>"]
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
                positioning = json.loads(json_match.group())
                return positioning
        except Exception as e:
            logger.warning(f"Brand positioning LLM call failed: {e}")
        
        # Fallback positioning
        return {
            "positioning_statement": "A leading solution provider delivering innovative results",
            "brand_personality": ["Innovative", "Reliable", "Professional"],
            "key_differentiators": ["Expertise", "Quality", "Results"],
            "unique_value_proposition": "Delivering exceptional value through proven expertise",
            "target_segments": [],
            "positioning_map": {
                "our_position": "Premium quality provider",
                "competitive_positioning": "Differentiated through expertise and results"
            },
            "key_messages": ["Quality", "Innovation", "Results"]
        }
    
    def develop_messaging(
        self,
        brand_positioning: Dict[str, Any],
        project_scope: Dict[str, Any],
        audience_segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Develop messaging framework
        
        Args:
            brand_positioning: Brand positioning strategy
            project_scope: Project scope
            audience_segment: Specific audience segment (optional)
            
        Returns:
            Messaging framework with key messages, proof points, and tone
        """
        self.log_action("Developing messaging framework")
        
        prompt = f"""As a Marketing Director, develop a comprehensive messaging framework.

Brand Positioning:
{json.dumps(brand_positioning, indent=2)}

Project Scope:
{json.dumps(project_scope, indent=2)}

Audience Segment: {audience_segment or "General"}

Create messaging including:
1. Core message (primary message)
2. Supporting messages (3-5 key messages)
3. Proof points (evidence supporting messages)
4. Tone and voice guidelines
5. Message hierarchy (most important to least)
6. Call-to-action messages

Return JSON format:
{{
    "core_message": "<primary message>",
    "supporting_messages": [
        {{
            "message": "<message text>",
            "audience": "<target audience>",
            "proof_points": ["<proof 1>", "<proof 2>"]
        }}
    ],
    "tone_and_voice": {{
        "tone": "<tone description>",
        "voice": "<voice description>",
        "guidelines": ["<guideline 1>", "<guideline 2>"]
    }},
    "message_hierarchy": ["<message 1>", "<message 2>"],
    "call_to_actions": ["<CTA 1>", "<CTA 2>"],
    "messaging_pillars": ["<pillar 1>", "<pillar 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.5,
                max_tokens=2500
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                messaging = json.loads(json_match.group())
                return messaging
        except Exception as e:
            logger.warning(f"Messaging development LLM call failed: {e}")
        
        # Fallback messaging
        return {
            "core_message": brand_positioning.get("unique_value_proposition", "Delivering exceptional value"),
            "supporting_messages": [
                {
                    "message": "Proven expertise and track record",
                    "audience": "General",
                    "proof_points": ["Experience", "Results"]
                }
            ],
            "tone_and_voice": {
                "tone": "Professional and confident",
                "voice": "Authoritative yet approachable",
                "guidelines": ["Clear", "Concise", "Compelling"]
            },
            "message_hierarchy": [brand_positioning.get("unique_value_proposition", "Value proposition")],
            "call_to_actions": ["Learn more", "Get started"],
            "messaging_pillars": ["Quality", "Innovation", "Results"]
        }
    
    def analyze_differentiation(
        self,
        project_scope: Dict[str, Any],
        competitive_landscape: Dict[str, Any],
        our_capabilities: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitive differentiation
        
        Args:
            project_scope: Project scope
            competitive_landscape: Competitive analysis
            our_capabilities: Our capabilities and strengths
            
        Returns:
            Differentiation analysis with competitive advantages and gaps
        """
        self.log_action("Analyzing competitive differentiation")
        
        competitors = competitive_landscape.get("competitors", [])
        
        prompt = f"""As a Marketing Director, analyze how we differentiate from competitors.

Project Scope:
{json.dumps(project_scope, indent=2)}

Competitors:
{json.dumps(competitors, indent=2)}

Our Capabilities:
{json.dumps(our_capabilities or {}, indent=2)}

Analyze:
1. Competitive advantages (what we do better)
2. Competitive gaps (where competitors are stronger)
3. Unique differentiators (what only we offer)
4. Positioning opportunities (gaps in market)
5. Competitive threats
6. Differentiation strategy recommendations

Return JSON format:
{{
    "competitive_advantages": [
        {{
            "advantage": "<advantage>",
            "description": "<description>",
            "significance": "<high/medium/low>"
        }}
    ],
    "competitive_gaps": [
        {{
            "gap": "<area where competitors are stronger>",
            "impact": "<high/medium/low>",
            "mitigation": "<how to address>"
        }}
    ],
    "unique_differentiators": ["<differentiator 1>", "<differentiator 2>"],
    "positioning_opportunities": ["<opportunity 1>", "<opportunity 2>"],
    "competitive_threats": ["<threat 1>", "<threat 2>"],
    "differentiation_strategy": "<strategic recommendation>",
    "competitive_score": <0-10 rating of our competitive position>
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
                analysis = json.loads(json_match.group())
                return analysis
        except Exception as e:
            logger.warning(f"Differentiation analysis LLM call failed: {e}")
        
        # Fallback analysis
        return {
            "competitive_advantages": [
                {
                    "advantage": "Expertise and experience",
                    "description": "Deep domain knowledge",
                    "significance": "high"
                }
            ],
            "competitive_gaps": [],
            "unique_differentiators": ["Quality", "Innovation"],
            "positioning_opportunities": ["Market leadership"],
            "competitive_threats": [],
            "differentiation_strategy": "Emphasize unique strengths and value proposition",
            "competitive_score": 7.5
        }
    
    def develop_value_proposition(
        self,
        project_scope: Dict[str, Any],
        target_audience: Dict[str, Any],
        benefits: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Develop value proposition
        
        Args:
            project_scope: Project scope
            target_audience: Target audience information
            benefits: List of project benefits
            
        Returns:
            Value proposition with benefits, proof points, and messaging
        """
        self.log_action("Developing value proposition")
        
        prompt = f"""As a Marketing Director, develop a compelling value proposition.

Project Scope:
{json.dumps(project_scope, indent=2)}

Target Audience:
{json.dumps(target_audience, indent=2)}

Benefits:
{json.dumps(benefits or [], indent=2)}

Create a value proposition including:
1. Value proposition statement (clear, compelling statement)
2. Key benefits (what the audience gains)
3. Proof points (evidence of value)
4. Emotional benefits (how it makes them feel)
5. Functional benefits (what it does)
6. Value proposition for different audience segments

Return JSON format:
{{
    "value_proposition_statement": "<clear value proposition>",
    "key_benefits": [
        {{
            "benefit": "<benefit>",
            "type": "<functional/emotional>",
            "proof_point": "<evidence>"
        }}
    ],
    "emotional_benefits": ["<benefit 1>", "<benefit 2>"],
    "functional_benefits": ["<benefit 1>", "<benefit 2>"],
    "proof_points": ["<proof 1>", "<proof 2>"],
    "segment_value_propositions": {{
        "<segment>": "<value prop for this segment>"
    }},
    "value_drivers": ["<driver 1>", "<driver 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.5,
                max_tokens=2500
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                value_prop = json.loads(json_match.group())
                return value_prop
        except Exception as e:
            logger.warning(f"Value proposition development LLM call failed: {e}")
        
        # Fallback value proposition
        return {
            "value_proposition_statement": "Delivering exceptional value through proven expertise and innovative solutions",
            "key_benefits": [
                {
                    "benefit": "Proven results",
                    "type": "functional",
                    "proof_point": "Track record of success"
                }
            ],
            "emotional_benefits": ["Confidence", "Peace of mind"],
            "functional_benefits": ["Results", "Efficiency"],
            "proof_points": ["Experience", "Results"],
            "segment_value_propositions": {},
            "value_drivers": ["Quality", "Innovation"]
        }
    
    def analyze_target_audience(
        self,
        project_scope: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze target audience
        
        Args:
            project_scope: Project scope
            market_data: Market research data
            
        Returns:
            Target audience analysis with segments, personas, and insights
        """
        self.log_action("Analyzing target audience")
        
        prompt = f"""As a Marketing Director, analyze the target audience for this project.

Project Scope:
{json.dumps(project_scope, indent=2)}

Market Data:
{json.dumps(market_data or {}, indent=2)}

Analyze:
1. Primary target audience segments
2. Audience personas (detailed profiles)
3. Audience needs and pain points
4. Decision-making factors
5. Communication preferences
6. Audience size and characteristics

Return JSON format:
{{
    "primary_segments": [
        {{
            "segment": "<segment name>",
            "size": "<large/medium/small>",
            "characteristics": "<description>",
            "needs": ["<need 1>", "<need 2>"],
            "pain_points": ["<pain 1>", "<pain 2>"]
        }}
    ],
    "personas": [
        {{
            "persona_name": "<name>",
            "role": "<role>",
            "demographics": "<description>",
            "goals": ["<goal 1>", "<goal 2>"],
            "challenges": ["<challenge 1>", "<challenge 2>"],
            "decision_factors": ["<factor 1>", "<factor 2>"]
        }}
    ],
    "audience_insights": ["<insight 1>", "<insight 2>"],
    "communication_preferences": ["<preference 1>", "<preference 2>"],
    "decision_making_process": "<description>"
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.5,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
        except Exception as e:
            logger.warning(f"Target audience analysis LLM call failed: {e}")
        
        # Fallback analysis
        return {
            "primary_segments": [
                {
                    "segment": "Primary stakeholders",
                    "size": "medium",
                    "characteristics": "Decision makers and influencers",
                    "needs": ["Results", "Value"],
                    "pain_points": ["Uncertainty", "Risk"]
                }
            ],
            "personas": [
                {
                    "persona_name": "Decision Maker",
                    "role": "Senior executive",
                    "demographics": "Experienced professional",
                    "goals": ["Success", "Value"],
                    "challenges": ["Resource constraints", "Time pressure"],
                    "decision_factors": ["ROI", "Risk", "Quality"]
                }
            ],
            "audience_insights": ["Value-focused", "Results-oriented"],
            "communication_preferences": ["Clear", "Data-driven"],
            "decision_making_process": "Evidence-based decision making"
        }
    
    def develop_competitive_positioning(
        self,
        brand_positioning: Dict[str, Any],
        differentiation_analysis: Dict[str, Any],
        competitive_landscape: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Develop competitive positioning strategy
        
        Args:
            brand_positioning: Brand positioning
            differentiation_analysis: Differentiation analysis
            competitive_landscape: Competitive landscape data
            
        Returns:
            Competitive positioning strategy with positioning map and recommendations
        """
        self.log_action("Developing competitive positioning strategy")
        
        # Extract key information
        our_position = brand_positioning.get("positioning_statement", "")
        differentiators = differentiation_analysis.get("unique_differentiators", [])
        advantages = differentiation_analysis.get("competitive_advantages", [])
        
        # Build positioning strategy
        positioning_strategy = {
            "positioning_statement": our_position,
            "key_differentiators": differentiators,
            "competitive_advantages": [adv.get("advantage") for adv in advantages],
            "positioning_map": {
                "our_position": our_position,
                "competitive_positioning": "Differentiated through unique strengths",
                "positioning_dimensions": {
                    "quality": "High",
                    "innovation": "High",
                    "value": "High"
                }
            },
            "competitive_strategy": "Differentiation through unique value proposition",
            "key_messages": [
                f"Unique {', '.join(differentiators[:2])}",
                "Proven track record",
                "Exceptional value"
            ],
            "competitive_recommendations": [
                "Emphasize unique differentiators",
                "Highlight competitive advantages",
                "Address competitive gaps proactively"
            ]
        }
        
        # Add strategic recommendations based on analysis
        gaps = differentiation_analysis.get("competitive_gaps", [])
        if gaps:
            positioning_strategy["competitive_recommendations"].append(
                "Develop strategies to address competitive gaps"
            )
        
        threats = differentiation_analysis.get("competitive_threats", [])
        if threats:
            positioning_strategy["competitive_recommendations"].append(
                "Monitor and mitigate competitive threats"
            )
        
        return positioning_strategy
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - Marketing Director workflow
        
        Expected input:
        {
            "action": "develop_brand_positioning" | "develop_messaging" | 
                      "analyze_differentiation" | "develop_value_proposition" |
                      "analyze_target_audience" | "develop_competitive_positioning",
            "project_scope": {...},
            "target_audience": {...},
            ...
        }
        """
        action = input_data.get("action", "develop_brand_positioning")
        
        if action == "develop_brand_positioning":
            return self.develop_brand_positioning(
                input_data.get("project_scope", {}),
                input_data.get("target_audience"),
                input_data.get("competitive_landscape")
            )
        elif action == "develop_messaging":
            return self.develop_messaging(
                input_data.get("brand_positioning", {}),
                input_data.get("project_scope", {}),
                input_data.get("audience_segment")
            )
        elif action == "analyze_differentiation":
            return self.analyze_differentiation(
                input_data.get("project_scope", {}),
                input_data.get("competitive_landscape", {}),
                input_data.get("our_capabilities")
            )
        elif action == "develop_value_proposition":
            return self.develop_value_proposition(
                input_data.get("project_scope", {}),
                input_data.get("target_audience", {}),
                input_data.get("benefits")
            )
        elif action == "analyze_target_audience":
            return self.analyze_target_audience(
                input_data.get("project_scope", {}),
                input_data.get("market_data")
            )
        elif action == "develop_competitive_positioning":
            return self.develop_competitive_positioning(
                input_data.get("brand_positioning", {}),
                input_data.get("differentiation_analysis", {}),
                input_data.get("competitive_landscape", {})
            )
        else:
            # Default: develop brand positioning
            return self.develop_brand_positioning(
                input_data.get("project_scope", {}),
                input_data.get("target_audience"),
                input_data.get("competitive_landscape")
            )

