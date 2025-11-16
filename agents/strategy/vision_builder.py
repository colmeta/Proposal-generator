"""
Vision Builder Agent
Develop vision/mission from vague inputs, clarify goals and objectives, create compelling narratives
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json


class VisionBuilderAgent(BaseAgent):
    """
    Vision Builder Agent
    Transforms vague ideas into clear, compelling vision and mission statements
    """
    
    def __init__(self):
        super().__init__(
            name="Vision Builder",
            role="Develop vision and mission from vague inputs",
            task_type="strategy"
        )
    
    def develop_vision(
        self,
        vague_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Develop a clear vision from vague input
        
        Args:
            vague_input: Vague or unclear vision/idea description
            context: Additional context (industry, goals, etc.)
        
        Returns:
            Clear vision statement with mission, values, and objectives
        """
        self.log_action("Developing vision from vague input")
        
        context_str = json.dumps(context, indent=2) if context else "None provided"
        
        prompt = f"""As a Vision Builder, transform this vague input into a clear, compelling vision.

Vague Input:
{vague_input}

Context:
{context_str}

Create a comprehensive vision that includes:
1. Clear vision statement (aspirational, future-focused)
2. Mission statement (purpose and approach)
3. Core values (principles that guide actions)
4. Key objectives (measurable goals)
5. Compelling narrative (story that inspires)

Return JSON:
{{
    "vision_statement": "clear vision statement",
    "mission_statement": "mission statement",
    "core_values": ["value 1", "value 2"],
    "key_objectives": ["objective 1", "objective 2"],
    "narrative": "compelling narrative story",
    "clarity_score": 0-10,
    "inspiration_score": 0-10
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
                vision = json.loads(json_match.group())
                self.log_action("Vision developed", {"clarity": vision.get("clarity_score")})
                return vision
        except Exception as e:
            self.logger.warning(f"Vision development LLM call failed: {e}")
        
        # Fallback vision
        return {
            "vision_statement": vague_input,
            "mission_statement": f"To achieve {vague_input}",
            "core_values": ["Excellence", "Innovation", "Integrity"],
            "key_objectives": ["Define clear goals", "Execute effectively"],
            "narrative": f"Our vision is to {vague_input}",
            "clarity_score": 7.0,
            "inspiration_score": 7.0
        }
    
    def clarify_goals(
        self,
        unclear_goals: List[str],
        vision: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Clarify and refine unclear goals
        
        Args:
            unclear_goals: List of unclear or vague goals
            vision: Vision context to align goals with
        
        Returns:
            Clarified goals with SMART criteria
        """
        self.log_action("Clarifying goals")
        
        vision_str = json.dumps(vision, indent=2) if vision else "None provided"
        
        prompt = f"""As a Vision Builder, clarify and refine these unclear goals.

Unclear Goals:
{json.dumps(unclear_goals, indent=2)}

Vision Context:
{vision_str}

For each goal, create:
1. Clear, specific goal statement
2. SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
3. Success metrics
4. Alignment with vision
5. Actionable steps

Return JSON:
{{
    "clarified_goals": [
        {{
            "original": "original vague goal",
            "clarified": "clear goal statement",
            "smart_criteria": {{
                "specific": "specific description",
                "measurable": "how to measure",
                "achievable": "feasibility assessment",
                "relevant": "relevance to vision",
                "time_bound": "timeline"
            }},
            "success_metrics": ["metric 1"],
            "actionable_steps": ["step 1", "step 2"]
        }}
    ],
    "overall_clarity_improvement": "description"
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
                clarified = json.loads(json_match.group())
                self.log_action("Goals clarified", {"count": len(clarified.get("clarified_goals", []))})
                return clarified
        except Exception as e:
            self.logger.warning(f"Goal clarification LLM call failed: {e}")
        
        # Fallback: basic clarification
        clarified_goals = []
        for goal in unclear_goals:
            clarified_goals.append({
                "original": goal,
                "clarified": f"Clearly define and achieve: {goal}",
                "smart_criteria": {
                    "specific": goal,
                    "measurable": "TBD",
                    "achievable": "Yes",
                    "relevant": "Yes",
                    "time_bound": "TBD"
                },
                "success_metrics": ["Goal achieved"],
                "actionable_steps": ["Define specifics", "Execute plan"]
            })
        
        return {
            "clarified_goals": clarified_goals,
            "overall_clarity_improvement": "Goals have been clarified"
        }
    
    def create_narrative(
        self,
        vision: Dict[str, Any],
        target_audience: str = "stakeholders"
    ) -> Dict[str, Any]:
        """
        Create compelling narrative from vision
        
        Args:
            vision: Vision and mission statements
            target_audience: Target audience for the narrative
        
        Returns:
            Compelling narrative with different formats
        """
        self.log_action("Creating compelling narrative")
        
        prompt = f"""As a Vision Builder, create a compelling narrative from this vision.

Vision:
{json.dumps(vision, indent=2)}

Target Audience: {target_audience}

Create narratives in different formats:
1. Elevator pitch (30 seconds)
2. Full narrative (2-3 minutes)
3. Written story (for documents)
4. Key talking points
5. Emotional hooks

Return JSON:
{{
    "elevator_pitch": "30-second pitch",
    "full_narrative": "2-3 minute narrative",
    "written_story": "written narrative for documents",
    "talking_points": ["point 1", "point 2"],
    "emotional_hooks": ["hook 1", "hook 2"],
    "narrative_strength": 0-10
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
                narrative = json.loads(json_match.group())
                self.log_action("Narrative created", {"strength": narrative.get("narrative_strength")})
                return narrative
        except Exception as e:
            self.logger.warning(f"Narrative creation LLM call failed: {e}")
        
        # Fallback narrative
        vision_stmt = vision.get("vision_statement", "Our vision")
        mission_stmt = vision.get("mission_statement", "Our mission")
        
        return {
            "elevator_pitch": f"{vision_stmt}. {mission_stmt}.",
            "full_narrative": f"Our vision is {vision_stmt}. We are committed to {mission_stmt}.",
            "written_story": f"Vision: {vision_stmt}\n\nMission: {mission_stmt}",
            "talking_points": [vision_stmt, mission_stmt],
            "emotional_hooks": ["Transformative impact", "Clear purpose"],
            "narrative_strength": 7.5
        }
    
    def transform_idea_to_vision(
        self,
        idea: str,
        industry: Optional[str] = None,
        goals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Transform a raw idea into a complete vision
        
        Args:
            idea: Raw idea or concept
            industry: Industry context
            goals: Related goals
        
        Returns:
            Complete vision package
        """
        self.log_action("Transforming idea to vision")
        
        # First develop the vision
        context = {
            "industry": industry,
            "goals": goals
        }
        vision = self.develop_vision(idea, context)
        
        # Then create narrative
        narrative = self.create_narrative(vision)
        
        # Combine into complete package
        return {
            "vision": vision,
            "narrative": narrative,
            "transformation_complete": True
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - route to appropriate method"""
        action = input_data.get("action", "develop_vision")
        
        if action == "develop_vision":
            return self.develop_vision(
                input_data.get("vague_input", ""),
                input_data.get("context")
            )
        elif action == "clarify_goals":
            return self.clarify_goals(
                input_data.get("unclear_goals", []),
                input_data.get("vision")
            )
        elif action == "create_narrative":
            return self.create_narrative(
                input_data.get("vision", {}),
                input_data.get("target_audience", "stakeholders")
            )
        elif action == "transform_idea":
            return self.transform_idea_to_vision(
                input_data.get("idea", ""),
                input_data.get("industry"),
                input_data.get("goals")
            )
        else:
            # Default to vision development
            return self.develop_vision(
                input_data.get("vague_input", ""),
                input_data.get("context")
            )

