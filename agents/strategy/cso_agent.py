"""
Chief Strategy Officer Agent
Project orchestration, strategic decisions, high-level planning, strategic alignment
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json


class CSOAgent(BaseAgent):
    """
    Chief Strategy Officer Agent
    Handles project orchestration, strategic decisions, high-level planning, and strategic alignment
    """
    
    def __init__(self):
        super().__init__(
            name="Chief Strategy Officer",
            role="Project orchestration and strategic decision-making",
            task_type="strategy"
        )
    
    def orchestrate_project(
        self,
        project_requirements: Dict[str, Any],
        available_resources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrate project execution with strategic oversight
        
        Args:
            project_requirements: Project requirements and objectives
            available_resources: Available team, budget, and resources
        
        Returns:
            Project orchestration plan with phases, milestones, and resource allocation
        """
        self.log_action("Orchestrating project execution")
        
        prompt = f"""As a Chief Strategy Officer, create a comprehensive project orchestration plan.

Project Requirements:
{json.dumps(project_requirements, indent=2)}

Available Resources:
{json.dumps(available_resources, indent=2)}

Create a strategic orchestration plan that includes:
1. Project phases and milestones
2. Resource allocation across phases
3. Strategic priorities and sequencing
4. Risk mitigation strategies
5. Success metrics and KPIs
6. Timeline with critical path

Return as JSON with structure:
{{
    "phases": [
        {{
            "name": "phase name",
            "objectives": ["objective 1", "objective 2"],
            "resources": {{"budget": 0, "team": []}},
            "timeline": "duration",
            "dependencies": ["phase names"],
            "risks": ["risk description"],
            "success_criteria": ["criteria"]
        }}
    ],
    "strategic_priorities": ["priority 1", "priority 2"],
    "overall_timeline": "total duration",
    "critical_path": ["phase sequence"],
    "risk_mitigation": {{"risk": "mitigation strategy"}}
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=4000
            )
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                self.log_action("Project orchestration plan created", {"phases": len(plan.get("phases", []))})
                return plan
        except Exception as e:
            self.logger.warning(f"Orchestration LLM call failed: {e}")
        
        # Fallback plan
        return {
            "phases": [
                {
                    "name": "Planning",
                    "objectives": ["Define scope", "Allocate resources"],
                    "resources": available_resources,
                    "timeline": "2 weeks",
                    "dependencies": [],
                    "risks": [],
                    "success_criteria": ["Scope defined", "Resources allocated"]
                }
            ],
            "strategic_priorities": ["Quality", "Timeline", "Budget"],
            "overall_timeline": "TBD",
            "critical_path": ["Planning"],
            "risk_mitigation": {}
        }
    
    def make_strategic_decision(
        self,
        decision_context: Dict[str, Any],
        options: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Make strategic decisions based on context and options
        
        Args:
            decision_context: Context for the decision (goals, constraints, etc.)
            options: Available options to choose from
        
        Returns:
            Decision with rationale and strategic alignment
        """
        self.log_action("Making strategic decision")
        
        prompt = f"""As a Chief Strategy Officer, make a strategic decision.

Decision Context:
{json.dumps(decision_context, indent=2)}

Available Options:
{json.dumps(options, indent=2)}

Evaluate each option based on:
1. Strategic alignment with goals
2. Resource requirements
3. Risk assessment
4. Long-term impact
5. Feasibility

Return JSON:
{{
    "selected_option": "option name or index",
    "rationale": "why this option",
    "strategic_alignment_score": 0-10,
    "risk_level": "low/medium/high",
    "expected_impact": "description",
    "alternatives_considered": ["option 1", "option 2"],
    "recommendations": ["recommendation 1"]
}}
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
                decision = json.loads(json_match.group())
                self.log_action("Strategic decision made", {"option": decision.get("selected_option")})
                return decision
        except Exception as e:
            self.logger.warning(f"Strategic decision LLM call failed: {e}")
        
        # Fallback: select first option
        return {
            "selected_option": options[0].get("name", "Option 1") if options else "Default",
            "rationale": "Default selection",
            "strategic_alignment_score": 7.0,
            "risk_level": "medium",
            "expected_impact": "Moderate impact",
            "alternatives_considered": [opt.get("name", "Option") for opt in options],
            "recommendations": []
        }
    
    def create_strategic_plan(
        self,
        vision: Dict[str, Any],
        objectives: List[str],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create high-level strategic plan
        
        Args:
            vision: Vision and mission statement
            objectives: Strategic objectives
            constraints: Budget, timeline, resource constraints
        
        Returns:
            Strategic plan with goals, strategies, and tactics
        """
        self.log_action("Creating strategic plan")
        
        prompt = f"""As a Chief Strategy Officer, create a high-level strategic plan.

Vision:
{json.dumps(vision, indent=2)}

Objectives:
{json.dumps(objectives, indent=2)}

Constraints:
{json.dumps(constraints, indent=2)}

Create a strategic plan with:
1. Strategic goals aligned with vision
2. High-level strategies to achieve goals
3. Key tactics and initiatives
4. Success metrics
5. Timeline and milestones

Return JSON:
{{
    "strategic_goals": [
        {{
            "goal": "goal description",
            "strategies": ["strategy 1", "strategy 2"],
            "tactics": ["tactic 1", "tactic 2"],
            "success_metrics": ["metric 1"],
            "timeline": "duration"
        }}
    ],
    "overall_timeline": "total duration",
    "key_milestones": ["milestone 1", "milestone 2"],
    "resource_requirements": {{"budget": 0, "team": []}}
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
                plan = json.loads(json_match.group())
                self.log_action("Strategic plan created", {"goals": len(plan.get("strategic_goals", []))})
                return plan
        except Exception as e:
            self.logger.warning(f"Strategic plan LLM call failed: {e}")
        
        # Fallback plan
        return {
            "strategic_goals": [
                {
                    "goal": "Achieve project objectives",
                    "strategies": ["Execute efficiently", "Maintain quality"],
                    "tactics": ["Follow best practices", "Monitor progress"],
                    "success_metrics": ["On-time delivery", "Quality standards met"],
                    "timeline": "As per constraints"
                }
            ],
            "overall_timeline": constraints.get("timeline", "TBD"),
            "key_milestones": ["Planning", "Execution", "Delivery"],
            "resource_requirements": constraints
        }
    
    def ensure_strategic_alignment(
        self,
        current_work: Dict[str, Any],
        strategic_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ensure current work aligns with strategic goals
        
        Args:
            current_work: Current work product or plan
            strategic_goals: Strategic goals and objectives
        
        Returns:
            Alignment assessment with recommendations
        """
        self.log_action("Assessing strategic alignment")
        
        prompt = f"""As a Chief Strategy Officer, assess strategic alignment.

Current Work:
{json.dumps(current_work, indent=2)}

Strategic Goals:
{json.dumps(strategic_goals, indent=2)}

Evaluate:
1. How well current work aligns with strategic goals
2. Gaps or misalignments
3. Recommendations for better alignment
4. Strategic value of current work

Return JSON:
{{
    "alignment_score": 0-10,
    "alignment_status": "aligned/partial/misaligned",
    "strengths": ["strength 1"],
    "gaps": ["gap 1"],
    "recommendations": ["recommendation 1"],
    "strategic_value": "high/medium/low"
}}
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
                assessment = json.loads(json_match.group())
                self.log_action("Strategic alignment assessed", {"score": assessment.get("alignment_score")})
                return assessment
        except Exception as e:
            self.logger.warning(f"Alignment assessment LLM call failed: {e}")
        
        # Fallback assessment
        return {
            "alignment_score": 7.5,
            "alignment_status": "partial",
            "strengths": ["Work addresses key objectives"],
            "gaps": ["May need refinement"],
            "recommendations": ["Review and refine for better alignment"],
            "strategic_value": "medium"
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - route to appropriate method"""
        action = input_data.get("action", "orchestrate")
        
        if action == "orchestrate":
            return self.orchestrate_project(
                input_data.get("project_requirements", {}),
                input_data.get("available_resources", {})
            )
        elif action == "decide":
            return self.make_strategic_decision(
                input_data.get("decision_context", {}),
                input_data.get("options", [])
            )
        elif action == "plan":
            return self.create_strategic_plan(
                input_data.get("vision", {}),
                input_data.get("objectives", []),
                input_data.get("constraints", {})
            )
        elif action == "align":
            return self.ensure_strategic_alignment(
                input_data.get("current_work", {}),
                input_data.get("strategic_goals", {})
            )
        else:
            # Default to orchestration
            return self.orchestrate_project(
                input_data.get("project_requirements", {}),
                input_data.get("available_resources", {})
            )

