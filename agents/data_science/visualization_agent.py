"""
Data Science & Visualization Agent
Creates executive-level data visualizations and presentations
Better than Visual Capitalist - designed for presidents and decision-makers
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging
import base64
from io import BytesIO

logger = logging.getLogger(__name__)


class DataVisualizationAgent(BaseAgent):
    """
    Data Science & Visualization Agent
    Creates world-class data visualizations and presentations
    """
    
    def __init__(self):
        super().__init__(
            name="Data Science & Visualization Agent",
            role="Create executive-level data visualizations and presentations that win",
            task_type="data_science"
        )
    
    def create_executive_presentation(
        self,
        proposal_data: Dict[str, Any],
        opportunity_type: str = "funding",  # "funding", "contract", "compliance"
        presentation_style: str = "executive"  # "executive", "presidential", "board"
    ) -> Dict[str, Any]:
        """
        Create executive-level presentation with world-class visualizations
        
        Better than Visual Capitalist:
        - Data-driven storytelling
        - Executive-ready format
        - Compelling visualizations
        - Win-focused messaging
        """
        self.log_action(f"Creating {presentation_style} presentation for {opportunity_type}")
        
        # Extract key data points
        data_points = self._extract_key_data_points(proposal_data, opportunity_type)
        
        # Create visualizations
        visualizations = self._create_visualizations(data_points, opportunity_type)
        
        # Create presentation structure
        presentation = self._create_presentation_structure(
            proposal_data=proposal_data,
            visualizations=visualizations,
            opportunity_type=opportunity_type,
            style=presentation_style
        )
        
        # Generate executive narrative
        narrative = self._generate_executive_narrative(
            proposal_data=proposal_data,
            data_points=data_points,
            opportunity_type=opportunity_type
        )
        
        # Create data-driven insights
        insights = self._generate_data_insights(data_points, opportunity_type)
        
        return {
            "presentation": presentation,
            "visualizations": visualizations,
            "narrative": narrative,
            "insights": insights,
            "executive_summary": self._create_executive_summary(data_points, opportunity_type),
            "data_story": self._create_data_story(data_points, opportunity_type),
            "winning_arguments": self._identify_winning_arguments(data_points, opportunity_type)
        }
    
    def _extract_key_data_points(
        self,
        proposal_data: Dict[str, Any],
        opportunity_type: str
    ) -> Dict[str, Any]:
        """Extract key data points for visualization"""
        
        data_points = {
            "metrics": {},
            "comparisons": {},
            "trends": {},
            "impact": {},
            "financial": {},
            "performance": {}
        }
        
        # Extract from proposal data
        if "budget" in proposal_data:
            data_points["financial"] = proposal_data["budget"]
        
        if "projects" in proposal_data:
            data_points["performance"]["projects"] = proposal_data["projects"]
        
        if "team" in proposal_data:
            data_points["performance"]["team_size"] = len(proposal_data.get("team", []))
        
        # Use LLM to identify key metrics
        prompt = f"""Extract key data points and metrics from this {opportunity_type} proposal for executive presentation:

{json.dumps(proposal_data, indent=2)[:5000]}

Identify:
1. Key performance metrics
2. Financial data points
3. Impact metrics
4. Comparative advantages
5. Growth trends
6. Success indicators

Return JSON:
{{
    "key_metrics": {{"metric_name": "value"}},
    "financial_highlights": {{"item": "value"}},
    "impact_metrics": {{"metric": "value"}},
    "comparative_advantages": ["advantage1", "advantage2"],
    "growth_indicators": ["indicator1", "indicator2"],
    "success_factors": ["factor1", "factor2"]
}}

Return ONLY valid JSON.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=2000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                data_points.update(extracted)
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
        
        return data_points
    
    def _create_visualizations(
        self,
        data_points: Dict[str, Any],
        opportunity_type: str
    ) -> List[Dict[str, Any]]:
        """Create world-class visualizations"""
        
        visualizations = []
        
        # 1. Impact Dashboard
        if data_points.get("impact_metrics"):
            visualizations.append({
                "type": "impact_dashboard",
                "title": "Impact at a Glance",
                "description": "Comprehensive impact visualization",
                "data": data_points["impact_metrics"],
                "chart_type": "dashboard",
                "priority": "high"
            })
        
        # 2. Financial Overview
        if data_points.get("financial_highlights"):
            visualizations.append({
                "type": "financial_overview",
                "title": "Financial Overview",
                "description": "Budget breakdown and financial projections",
                "data": data_points["financial_highlights"],
                "chart_type": "stacked_bar",
                "priority": "high"
            })
        
        # 3. Performance Trends
        if data_points.get("growth_indicators"):
            visualizations.append({
                "type": "performance_trends",
                "title": "Performance Trends",
                "description": "Growth and performance over time",
                "data": data_points["growth_indicators"],
                "chart_type": "line_chart",
                "priority": "medium"
            })
        
        # 4. Comparative Analysis
        if data_points.get("comparative_advantages"):
            visualizations.append({
                "type": "comparative_analysis",
                "title": "Competitive Advantages",
                "description": "Why we stand out",
                "data": data_points["comparative_advantages"],
                "chart_type": "radar_chart",
                "priority": "high"
            })
        
        # 5. Success Metrics
        if data_points.get("key_metrics"):
            visualizations.append({
                "type": "success_metrics",
                "title": "Key Success Metrics",
                "description": "Critical performance indicators",
                "data": data_points["key_metrics"],
                "chart_type": "kpi_dashboard",
                "priority": "critical"
            })
        
        # Generate visualization specifications using LLM
        enhanced_viz = self._enhance_visualizations_with_llm(visualizations, opportunity_type)
        
        return enhanced_viz
    
    def _enhance_visualizations_with_llm(
        self,
        visualizations: List[Dict],
        opportunity_type: str
    ) -> List[Dict]:
        """Enhance visualizations with AI recommendations"""
        
        prompt = f"""As a world-class data visualization expert (better than Visual Capitalist), enhance these visualizations for {opportunity_type} proposals:

{json.dumps(visualizations, indent=2)}

Provide recommendations for:
1. Best chart types for each data
2. Color schemes (executive/presidential style)
3. Layout and design
4. Data storytelling approach
5. Visual hierarchy

Return JSON:
{{
    "enhanced_visualizations": [
        {{
            "type": "...",
            "recommended_chart": "...",
            "color_scheme": "...",
            "design_notes": "...",
            "storytelling_angle": "...",
            "executive_appeal": "..."
        }}
    ],
    "presentation_flow": ["viz1", "viz2", ...],
    "key_messages": ["message1", "message2"]
}}

Return ONLY valid JSON.
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
                enhanced = json.loads(json_match.group())
                
                # Merge enhancements
                for i, viz in enumerate(visualizations):
                    if i < len(enhanced.get("enhanced_visualizations", [])):
                        viz.update(enhanced["enhanced_visualizations"][i])
                
                return visualizations
        except Exception as e:
            logger.error(f"Visualization enhancement failed: {e}")
        
        return visualizations
    
    def _create_presentation_structure(
        self,
        proposal_data: Dict[str, Any],
        visualizations: List[Dict],
        opportunity_type: str,
        style: str
    ) -> Dict[str, Any]:
        """Create executive presentation structure"""
        
        structure = {
            "title": f"{opportunity_type.title()} Proposal - Executive Presentation",
            "style": style,
            "slides": []
        }
        
        # Slide 1: Title & Executive Summary
        structure["slides"].append({
            "slide_number": 1,
            "title": "Executive Summary",
            "type": "title",
            "content": {
                "headline": self._create_headline(proposal_data, opportunity_type),
                "key_message": self._create_key_message(proposal_data, opportunity_type),
                "visualization": "hero_visualization"
            }
        })
        
        # Slide 2: The Opportunity
        structure["slides"].append({
            "slide_number": 2,
            "title": "The Opportunity",
            "type": "opportunity",
            "content": {
                "description": proposal_data.get("problem_statement", ""),
                "visualization": visualizations[0] if visualizations else None
            }
        })
        
        # Slide 3: Our Solution
        structure["slides"].append({
            "slide_number": 3,
            "title": "Our Solution",
            "type": "solution",
            "content": {
                "description": proposal_data.get("solution", ""),
                "visualization": visualizations[1] if len(visualizations) > 1 else None
            }
        })
        
        # Slide 4: Impact & Results
        structure["slides"].append({
            "slide_number": 4,
            "title": "Impact & Results",
            "type": "impact",
            "content": {
                "metrics": proposal_data.get("impact", {}),
                "visualization": next((v for v in visualizations if v["type"] == "impact_dashboard"), None)
            }
        })
        
        # Slide 5: Financial Overview
        structure["slides"].append({
            "slide_number": 5,
            "title": "Financial Overview",
            "type": "financial",
            "content": {
                "budget": proposal_data.get("budget", {}),
                "visualization": next((v for v in visualizations if v["type"] == "financial_overview"), None)
            }
        })
        
        # Slide 6: Why We Win
        structure["slides"].append({
            "slide_number": 6,
            "title": "Why We Win",
            "type": "competitive",
            "content": {
                "advantages": proposal_data.get("advantages", []),
                "visualization": next((v for v in visualizations if v["type"] == "comparative_analysis"), None)
            }
        })
        
        # Slide 7: Call to Action
        structure["slides"].append({
            "slide_number": 7,
            "title": "Next Steps",
            "type": "cta",
            "content": {
                "action_items": self._create_action_items(opportunity_type),
                "timeline": proposal_data.get("timeline", {})
            }
        })
        
        return structure
    
    def _create_headline(self, proposal_data: Dict[str, Any], opportunity_type: str) -> str:
        """Create compelling headline"""
        # Use LLM to create executive headline
        prompt = f"""Create a compelling executive headline for this {opportunity_type} proposal:

{json.dumps(proposal_data, indent=2)[:2000]}

Headline should be:
- Powerful and memorable
- Data-driven
- Executive-level
- Win-focused

Return ONLY the headline, no other text.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.7,
                max_tokens=100
            )
            return response.strip()
        except:
            return f"Transforming {opportunity_type} Through Data-Driven Excellence"
    
    def _create_key_message(self, proposal_data: Dict[str, Any], opportunity_type: str) -> str:
        """Create key message"""
        prompt = f"""Create a powerful key message (one sentence) for this {opportunity_type} proposal:

{json.dumps(proposal_data, indent=2)[:2000]}

Message should be:
- Clear and compelling
- Data-backed
- Executive-ready

Return ONLY the message, no other text.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.6,
                max_tokens=150
            )
            return response.strip()
        except:
            return "Delivering measurable impact through proven excellence"
    
    def _generate_executive_narrative(
        self,
        proposal_data: Dict[str, Any],
        data_points: Dict[str, Any],
        opportunity_type: str
    ) -> str:
        """Generate executive narrative"""
        
        prompt = f"""Create an executive narrative (2-3 paragraphs) for this {opportunity_type} proposal. Style: Presidential/Board-level.

DATA POINTS:
{json.dumps(data_points, indent=2)}

PROPOSAL DATA:
{json.dumps(proposal_data, indent=2)[:3000]}

Narrative should:
- Tell a compelling data-driven story
- Be executive-level (presidential quality)
- Highlight key metrics naturally
- Build a winning case
- Be memorable and impactful

Return ONLY the narrative, no other text.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.5,
                max_tokens=500
            )
            return response.strip()
        except:
            return "Our proposal represents a strategic opportunity to deliver exceptional results..."
    
    def _generate_data_insights(
        self,
        data_points: Dict[str, Any],
        opportunity_type: str
    ) -> List[str]:
        """Generate data-driven insights"""
        
        prompt = f"""Generate 5-7 data-driven insights from this {opportunity_type} proposal data:

{json.dumps(data_points, indent=2)}

Insights should:
- Be backed by data
- Be executive-level
- Support winning argument
- Be memorable

Return JSON array:
["insight1", "insight2", ...]

Return ONLY valid JSON array.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=500
            )
            
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return [
            "Data-driven approach ensures measurable outcomes",
            "Proven track record demonstrates capability",
            "Strategic alignment maximizes impact"
        ]
    
    def _create_executive_summary(
        self,
        data_points: Dict[str, Any],
        opportunity_type: str
    ) -> str:
        """Create executive summary"""
        # Use LLM to create executive summary
        return f"Executive summary for {opportunity_type} based on key data points"
    
    def _create_data_story(
        self,
        data_points: Dict[str, Any],
        opportunity_type: str
    ) -> str:
        """Create data-driven story"""
        # Use LLM to create compelling data story
        return f"Data-driven narrative for {opportunity_type}"
    
    def _identify_winning_arguments(
        self,
        data_points: Dict[str, Any],
        opportunity_type: str
    ) -> List[str]:
        """Identify winning arguments from data"""
        # Use LLM to identify winning arguments
        return [
            "Proven track record",
            "Data-driven approach",
            "Measurable impact"
        ]
    
    def _create_action_items(self, opportunity_type: str) -> List[str]:
        """Create action items"""
        return [
            "Review and approve proposal",
            "Schedule follow-up meeting",
            "Proceed with next steps"
        ]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - create presentation"""
        proposal_data = input_data.get("proposal_data", {})
        opportunity_type = input_data.get("opportunity_type", "funding")
        presentation_style = input_data.get("presentation_style", "executive")
        
        return self.create_executive_presentation(
            proposal_data=proposal_data,
            opportunity_type=opportunity_type,
            presentation_style=presentation_style
        )

