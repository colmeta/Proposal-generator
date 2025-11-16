"""
Competitive Intelligence Agent
Analyzes competitors, market positioning, and identifies competitive advantages
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json


class CompetitiveIntelligenceAgent(BaseAgent):
    """
    Competitive Intelligence Agent
    Performs competitor analysis, market positioning, SWOT analysis, and identifies differentiation opportunities
    """
    
    def __init__(self, knowledge_base=None):
        """
        Initialize Competitive Intelligence Agent
        
        Args:
            knowledge_base: Optional knowledge base service for retrieving competitor data
        """
        super().__init__(
            name="Competitive Intelligence Agent",
            role="Competitor analysis and market positioning expert",
            task_type="analysis"
        )
        self.knowledge_base = knowledge_base
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process competitive intelligence request
        
        Args:
            input_data: Should contain:
                - project_name: Name of the project
                - funder_name: Name of the funder
                - industry: Industry sector
                - competitors: Optional list of competitor names
                - market_context: Optional market context information
        
        Returns:
            Competitive intelligence analysis including:
                - competitors: List of identified competitors
                - market_positioning: Market positioning analysis
                - competitive_advantages: Identified competitive advantages
                - swot_analysis: SWOT analysis
                - differentiation_opportunities: Opportunities for differentiation
        """
        self.log_action("Starting competitive intelligence analysis", input_data)
        
        # Validate input
        required_fields = ["project_name", "funder_name"]
        self.validate_input(input_data, required_fields)
        
        project_name = input_data.get("project_name")
        funder_name = input_data.get("funder_name")
        industry = input_data.get("industry", "general")
        competitors = input_data.get("competitors", [])
        market_context = input_data.get("market_context", "")
        
        # Retrieve relevant knowledge from knowledge base if available
        knowledge_context = ""
        if self.knowledge_base:
            try:
                search_results = self.knowledge_base.search(
                    query=f"{funder_name} competitors {industry}",
                    n_results=5
                )
                if search_results:
                    knowledge_context = "\n".join([
                        f"- {result.get('content', '')}" 
                        for result in search_results
                    ])
            except Exception as e:
                self.logger.warning(f"Knowledge base search failed: {e}")
        
        # Identify competitors if not provided
        if not competitors:
            competitors = self._identify_competitors(
                project_name, funder_name, industry, knowledge_context
            )
        
        # Perform competitive analysis
        market_positioning = self._analyze_market_positioning(
            project_name, competitors, industry, market_context
        )
        
        competitive_advantages = self._identify_competitive_advantages(
            project_name, competitors, funder_name
        )
        
        swot_analysis = self._perform_swot_analysis(
            project_name, competitors, industry
        )
        
        differentiation_opportunities = self._identify_differentiation_opportunities(
            project_name, competitors, funder_name, market_positioning
        )
        
        result = {
            "competitors": competitors,
            "market_positioning": market_positioning,
            "competitive_advantages": competitive_advantages,
            "swot_analysis": swot_analysis,
            "differentiation_opportunities": differentiation_opportunities,
            "summary": self._generate_summary(
                competitive_advantages, swot_analysis, differentiation_opportunities
            )
        }
        
        self.log_action("Competitive intelligence analysis completed", {
            "competitors_count": len(competitors)
        })
        
        return result
    
    def _identify_competitors(
        self, 
        project_name: str, 
        funder_name: str, 
        industry: str,
        knowledge_context: str = ""
    ) -> List[Dict[str, Any]]:
        """Identify potential competitors"""
        prompt = f"""As a competitive intelligence expert, identify potential competitors for the following project:

Project Name: {project_name}
Funder: {funder_name}
Industry: {industry}

{f"Additional Context:\n{knowledge_context}" if knowledge_context else ""}

Identify 5-10 potential competitors that might also be applying for funding from {funder_name} or operating in the same space.

For each competitor, provide:
1. Organization/Company name
2. Brief description of their work
3. Why they are a competitor (similar focus, target market, or approach)

Return your response as a JSON array with the following structure:
[
  {{
    "name": "Competitor Name",
    "description": "Brief description",
    "competitive_reason": "Why they compete"
  }}
]

Only return the JSON array, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                competitors = json.loads(json_str)
                return competitors if isinstance(competitors, list) else []
        except Exception as e:
            self.logger.error(f"Error identifying competitors: {e}")
        
        return []
    
    def _analyze_market_positioning(
        self,
        project_name: str,
        competitors: List[Dict[str, Any]],
        industry: str,
        market_context: str = ""
    ) -> Dict[str, Any]:
        """Analyze market positioning relative to competitors"""
        competitors_str = "\n".join([
            f"- {comp.get('name', 'Unknown')}: {comp.get('description', '')}"
            for comp in competitors
        ])
        
        prompt = f"""As a market positioning expert, analyze the market positioning for:

Project: {project_name}
Industry: {industry}

Competitors:
{competitors_str}

{f"Market Context:\n{market_context}" if market_context else ""}

Analyze the market positioning and provide:
1. Current market position (leader, challenger, follower, niche)
2. Market share estimate (if applicable)
3. Positioning strategy
4. Target market segments
5. Value proposition positioning

Return your response as a JSON object:
{{
  "position": "leader|challenger|follower|niche",
  "market_share_estimate": "description",
  "positioning_strategy": "description",
  "target_segments": ["segment1", "segment2"],
  "value_proposition": "description"
}}

Only return the JSON object, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1500
            )
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error analyzing market positioning: {e}")
        
        return {
            "position": "unknown",
            "market_share_estimate": "Unable to determine",
            "positioning_strategy": "Analysis pending",
            "target_segments": [],
            "value_proposition": "Analysis pending"
        }
    
    def _identify_competitive_advantages(
        self,
        project_name: str,
        competitors: List[Dict[str, Any]],
        funder_name: str
    ) -> Dict[str, Any]:
        """Identify competitive advantages"""
        competitors_str = "\n".join([
            f"- {comp.get('name', 'Unknown')}: {comp.get('description', '')}"
            for comp in competitors
        ])
        
        prompt = f"""As a competitive analysis expert, identify competitive advantages for:

Project: {project_name}
Funder: {funder_name}

Competitors:
{competitors_str}

Identify:
1. Unique strengths that differentiate this project
2. Competitive advantages over each major competitor
3. Advantages that align with {funder_name}'s priorities
4. Sustainable competitive advantages

Return your response as a JSON object:
{{
  "unique_strengths": ["strength1", "strength2"],
  "advantages_by_competitor": {{
    "competitor_name": ["advantage1", "advantage2"]
  }},
  "funder_aligned_advantages": ["advantage1", "advantage2"],
  "sustainable_advantages": ["advantage1", "advantage2"]
}}

Only return the JSON object, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error identifying competitive advantages: {e}")
        
        return {
            "unique_strengths": [],
            "advantages_by_competitor": {},
            "funder_aligned_advantages": [],
            "sustainable_advantages": []
        }
    
    def _perform_swot_analysis(
        self,
        project_name: str,
        competitors: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """Perform SWOT analysis"""
        competitors_str = "\n".join([
            f"- {comp.get('name', 'Unknown')}"
            for comp in competitors[:5]  # Limit to top 5
        ])
        
        prompt = f"""As a strategic analysis expert, perform a comprehensive SWOT analysis for:

Project: {project_name}
Industry: {industry}
Key Competitors: {competitors_str if competitors_str else "None identified"}

Provide a SWOT analysis with:
- Strengths: Internal positive attributes
- Weaknesses: Internal areas for improvement
- Opportunities: External favorable conditions
- Threats: External challenges and risks

Return your response as a JSON object:
{{
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "opportunities": ["opportunity1", "opportunity2"],
  "threats": ["threat1", "threat2"]
}}

Only return the JSON object, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error performing SWOT analysis: {e}")
        
        return {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
    
    def _identify_differentiation_opportunities(
        self,
        project_name: str,
        competitors: List[Dict[str, Any]],
        funder_name: str,
        market_positioning: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify opportunities for differentiation"""
        competitors_str = "\n".join([
            f"- {comp.get('name', 'Unknown')}: {comp.get('description', '')}"
            for comp in competitors
        ])
        
        prompt = f"""As a differentiation strategy expert, identify opportunities for differentiation for:

Project: {project_name}
Funder: {funder_name}

Competitors:
{competitors_str}

Market Positioning: {json.dumps(market_positioning, indent=2)}

Identify specific opportunities to differentiate this project from competitors, especially in ways that align with {funder_name}'s priorities.

For each opportunity, provide:
1. Differentiation strategy
2. Why it matters to the funder
3. Implementation feasibility
4. Expected impact

Return your response as a JSON array:
[
  {{
    "strategy": "Differentiation strategy",
    "funder_alignment": "Why it matters to funder",
    "feasibility": "high|medium|low",
    "expected_impact": "description"
  }}
]

Only return the JSON array, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.8,
                max_tokens=2000
            )
            
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                opportunities = json.loads(json_str)
                return opportunities if isinstance(opportunities, list) else []
        except Exception as e:
            self.logger.error(f"Error identifying differentiation opportunities: {e}")
        
        return []
    
    def _generate_summary(
        self,
        competitive_advantages: Dict[str, Any],
        swot_analysis: Dict[str, Any],
        differentiation_opportunities: List[Dict[str, Any]]
    ) -> str:
        """Generate executive summary of competitive intelligence"""
        prompt = f"""Generate a concise executive summary (2-3 paragraphs) of the competitive intelligence analysis:

Competitive Advantages:
{json.dumps(competitive_advantages, indent=2)}

SWOT Analysis:
{json.dumps(swot_analysis, indent=2)}

Differentiation Opportunities:
{json.dumps(differentiation_opportunities, indent=2)}

Provide a clear, actionable summary that highlights key findings and recommendations."""
        
        try:
            return self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "Summary generation failed."

