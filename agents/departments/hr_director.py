"""
HR Director Agent
Handles team presentation and credentials, organizational capacity assessment,
skills gap analysis, team structure optimization, credentials verification, and capacity planning.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class HRDirectorAgent(BaseAgent):
    """
    HR Director Agent - Team and organizational capacity specialist.
    Presents teams, verifies credentials, assesses capacity, analyzes skills gaps,
    optimizes team structure, and plans capacity.
    """
    
    def __init__(self):
        super().__init__(
            name="HR Director",
            role="Team presentation, credentials verification, and capacity planning",
            task_type="analysis"
        )
    
    def present_team(
        self,
        team_members: List[Dict[str, Any]],
        project_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Present team with credentials and capabilities
        
        Args:
            team_members: List of team members with their information
            project_requirements: Project requirements (optional)
            
        Returns:
            Team presentation with credentials, capabilities, and alignment
        """
        self.log_action("Presenting team")
        
        prompt = f"""As an HR Director, create a professional team presentation for this proposal.

Team Members:
{json.dumps(team_members, indent=2)}

Project Requirements (if available):
{json.dumps(project_requirements or {}, indent=2)}

Create a comprehensive team presentation including:
1. Team member profiles with key credentials
2. Relevant experience and expertise
3. Role assignments
4. Team strengths and capabilities
5. Alignment with project requirements

Return JSON format:
{{
    "team_presentation": {{
        "total_members": <number>,
        "team_strengths": ["<strength 1>", "<strength 2>"],
        "key_credentials": ["<credential 1>", "<credential 2>"],
        "relevant_experience": "<summary>"
    }},
    "member_profiles": [
        {{
            "name": "<name>",
            "role": "<role>",
            "credentials": ["<credential 1>"],
            "experience": "<years>",
            "key_skills": ["<skill 1>", "<skill 2>"],
            "contribution": "<how they contribute>"
        }}
    ],
    "team_alignment": {{
        "alignment_score": <0-10>,
        "strengths": ["<strength 1>"],
        "gaps": ["<gap 1>"]
    }}
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
                presentation = json.loads(json_match.group())
                return presentation
        except Exception as e:
            logger.warning(f"Team presentation LLM call failed: {e}")
        
        # Fallback: basic team presentation
        return {
            "team_presentation": {
                "total_members": len(team_members),
                "team_strengths": ["Experienced team", "Diverse skill set"],
                "key_credentials": [],
                "relevant_experience": "Team has relevant experience for the project"
            },
            "member_profiles": [
                {
                    "name": member.get("name", "Unknown"),
                    "role": member.get("role", "Team Member"),
                    "credentials": member.get("credentials", []),
                    "experience": member.get("experience_years", 0),
                    "key_skills": member.get("skills", []),
                    "contribution": "Contributes to project success"
                }
                for member in team_members
            ],
            "team_alignment": {
                "alignment_score": 7.0,
                "strengths": ["Team composition is appropriate"],
                "gaps": []
            }
        }
    
    def verify_credentials(
        self,
        team_members: List[Dict[str, Any]],
        required_credentials: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verify team member credentials
        
        Args:
            team_members: List of team members
            required_credentials: Required credentials for the project (optional)
            
        Returns:
            Credentials verification with status, gaps, and recommendations
        """
        self.log_action("Verifying credentials")
        
        verification = {
            "all_verified": True,
            "verification_status": {},
            "missing_credentials": [],
            "recommendations": []
        }
        
        # Verify each team member's credentials
        for member in team_members:
            member_name = member.get("name", "Unknown")
            member_credentials = member.get("credentials", [])
            
            member_status = {
                "verified": True,
                "credentials": member_credentials,
                "missing": []
            }
            
            # Check if member has required credentials
            if required_credentials:
                for req_cred in required_credentials:
                    if req_cred not in member_credentials:
                        member_status["verified"] = False
                        member_status["missing"].append(req_cred)
                        verification["all_verified"] = False
                        verification["missing_credentials"].append({
                            "member": member_name,
                            "credential": req_cred
                        })
            
            verification["verification_status"][member_name] = member_status
        
        # Generate recommendations
        if not verification["all_verified"]:
            verification["recommendations"].append(
                f"Address {len(verification['missing_credentials'])} missing credentials"
            )
            for missing in verification["missing_credentials"][:5]:
                verification["recommendations"].append(
                    f"- {missing['member']} needs {missing['credential']}"
                )
        else:
            verification["recommendations"].append("All required credentials are verified")
        
        return verification
    
    def assess_organizational_capacity(
        self,
        current_organization: Dict[str, Any],
        project_demand: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess organizational capacity
        
        Args:
            current_organization: Current organizational structure and capacity
            project_demand: Project resource and skill demands
            
        Returns:
            Capacity assessment with utilization, gaps, and recommendations
        """
        self.log_action("Assessing organizational capacity")
        
        assessment = {
            "capacity_adequate": True,
            "current_capacity": {},
            "project_demand": {},
            "capacity_gaps": {},
            "utilization": {},
            "recommendations": []
        }
        
        # Assess team size capacity
        current_team_size = current_organization.get("team_size", 0)
        required_team_size = project_demand.get("team_size", 0)
        
        assessment["current_capacity"]["team_size"] = current_team_size
        assessment["project_demand"]["team_size"] = required_team_size
        
        if current_team_size < required_team_size:
            assessment["capacity_adequate"] = False
            gap = required_team_size - current_team_size
            assessment["capacity_gaps"]["team_size"] = gap
            assessment["recommendations"].append(f"Need {gap} additional team members")
        else:
            utilization = (required_team_size / current_team_size * 100) if current_team_size > 0 else 0
            assessment["utilization"]["team_size"] = round(utilization, 2)
        
        # Assess skill capacity
        current_skills = set(current_organization.get("available_skills", []))
        required_skills = set(project_demand.get("required_skills", []))
        
        assessment["current_capacity"]["skills"] = list(current_skills)
        assessment["project_demand"]["skills"] = list(required_skills)
        
        missing_skills = required_skills - current_skills
        if missing_skills:
            assessment["capacity_adequate"] = False
            assessment["capacity_gaps"]["skills"] = list(missing_skills)
            assessment["recommendations"].append(
                f"Need to acquire or hire for skills: {', '.join(list(missing_skills)[:5])}"
            )
        
        # Assess experience level
        current_experience = current_organization.get("average_experience_years", 0)
        required_experience = project_demand.get("required_experience_years", 0)
        
        if current_experience < required_experience:
            assessment["capacity_adequate"] = False
            assessment["capacity_gaps"]["experience"] = required_experience - current_experience
            assessment["recommendations"].append(
                f"Team needs {required_experience - current_experience} more years of average experience"
            )
        
        if assessment["capacity_adequate"]:
            assessment["recommendations"].append("Organizational capacity is adequate for project")
        
        return assessment
    
    def analyze_skills_gap(
        self,
        current_skills: List[str],
        required_skills: List[str],
        team_members: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze skills gap
        
        Args:
            current_skills: Current team skills
            required_skills: Required skills for the project
            team_members: Optional team member details
            
        Returns:
            Skills gap analysis with gaps, recommendations, and development plans
        """
        self.log_action("Analyzing skills gap")
        
        current_skills_set = set(current_skills)
        required_skills_set = set(required_skills)
        
        gap_analysis = {
            "current_skills": list(current_skills_set),
            "required_skills": list(required_skills_set),
            "skills_gap": list(required_skills_set - current_skills_set),
            "excess_skills": list(current_skills_set - required_skills_set),
            "coverage_percentage": 0.0,
            "recommendations": []
        }
        
        # Calculate coverage
        if required_skills_set:
            coverage = len(current_skills_set & required_skills_set) / len(required_skills_set) * 100
            gap_analysis["coverage_percentage"] = round(coverage, 2)
        
        # Generate recommendations
        if gap_analysis["skills_gap"]:
            gap_analysis["recommendations"].append(
                f"Address {len(gap_analysis['skills_gap'])} skills gaps"
            )
            
            # Prioritize critical skills
            critical_skills = gap_analysis["skills_gap"][:5]
            for skill in critical_skills:
                gap_analysis["recommendations"].append(
                    f"- Acquire {skill} through hiring, training, or consulting"
                )
        else:
            gap_analysis["recommendations"].append("No skills gaps identified - team is well-equipped")
        
        # Development plan
        if gap_analysis["skills_gap"]:
            gap_analysis["development_plan"] = {
                "training_needed": gap_analysis["skills_gap"],
                "hiring_needed": gap_analysis["skills_gap"],
                "consulting_options": gap_analysis["skills_gap"]
            }
        else:
            gap_analysis["development_plan"] = {
                "training_needed": [],
                "hiring_needed": [],
                "consulting_options": []
            }
        
        return gap_analysis
    
    def optimize_team_structure(
        self,
        current_structure: Dict[str, Any],
        project_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize team structure
        
        Args:
            current_structure: Current team structure
            project_requirements: Project requirements
            
        Returns:
            Optimized team structure with recommendations
        """
        self.log_action("Optimizing team structure")
        
        prompt = f"""As an HR Director, optimize the team structure for this project.

Current Team Structure:
{json.dumps(current_structure, indent=2)}

Project Requirements:
{json.dumps(project_requirements, indent=2)}

Optimize for:
1. Efficiency and productivity
2. Clear roles and responsibilities
3. Effective communication
4. Skill utilization
5. Scalability

Return JSON format:
{{
    "optimized_structure": {{
        "hierarchy": "<flat|hierarchical|matrix>",
        "teams": [
            {{
                "team_name": "<name>",
                "members": <number>,
                "responsibilities": ["<responsibility 1>"]
            }}
        ],
        "reporting_structure": "<description>"
    }},
    "improvements": ["<improvement 1>", "<improvement 2>"],
    "recommendations": ["<recommendation 1>", "<recommendation 2>"]
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
                optimization = json.loads(json_match.group())
                return optimization
        except Exception as e:
            logger.warning(f"Team structure optimization LLM call failed: {e}")
        
        # Fallback: return current structure
        return {
            "optimized_structure": current_structure,
            "improvements": [],
            "recommendations": ["Review team structure for optimization opportunities"]
        }
    
    def plan_capacity(
        self,
        project_roadmap: Dict[str, Any],
        current_capacity: Dict[str, Any],
        growth_projections: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Plan organizational capacity
        
        Args:
            project_roadmap: Project roadmap and phases
            current_capacity: Current organizational capacity
            growth_projections: Growth projections (optional)
            
        Returns:
            Capacity plan with hiring needs, timeline, and recommendations
        """
        self.log_action("Planning capacity")
        
        capacity_plan = {
            "current_capacity": current_capacity,
            "projected_needs": {},
            "hiring_plan": [],
            "timeline": {},
            "recommendations": []
        }
        
        # Analyze project phases
        phases = project_roadmap.get("phases", [])
        current_team_size = current_capacity.get("team_size", 0)
        
        # Project capacity needs by phase
        peak_team_size = 0
        for phase in phases:
            phase_team_size = phase.get("required_team_size", 0)
            peak_team_size = max(peak_team_size, phase_team_size)
        
        capacity_plan["projected_needs"]["peak_team_size"] = peak_team_size
        
        # Calculate hiring needs
        if peak_team_size > current_team_size:
            hiring_needed = peak_team_size - current_team_size
            capacity_plan["hiring_plan"].append({
                "action": "Hire additional team members",
                "quantity": hiring_needed,
                "timeline": "Before project start",
                "priority": "high"
            })
            capacity_plan["recommendations"].append(
                f"Hire {hiring_needed} team members before project start"
            )
        
        # Consider growth projections
        if growth_projections:
            future_team_size = growth_projections.get("projected_team_size", current_team_size)
            if future_team_size > peak_team_size:
                capacity_plan["hiring_plan"].append({
                    "action": "Plan for growth",
                    "quantity": future_team_size - peak_team_size,
                    "timeline": "During project execution",
                    "priority": "medium"
                })
        
        # Timeline
        capacity_plan["timeline"] = {
            "immediate": "Address current capacity gaps",
            "short_term": "Hire for project start",
            "long_term": "Plan for growth and scalability"
        }
        
        if not capacity_plan["hiring_plan"]:
            capacity_plan["recommendations"].append("Current capacity is adequate for project needs")
        
        return capacity_plan
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - HR Director workflow
        
        Expected input:
        {
            "action": "present_team" | "verify_credentials" | "assess_capacity" |
                      "analyze_skills_gap" | "optimize_structure" | "plan_capacity",
            "team_members": [...],
            "project_requirements": {...},
            ...
        }
        """
        action = input_data.get("action", "present_team")
        
        if action == "present_team":
            return self.present_team(
                input_data.get("team_members", []),
                input_data.get("project_requirements")
            )
        elif action == "verify_credentials":
            return self.verify_credentials(
                input_data.get("team_members", []),
                input_data.get("required_credentials")
            )
        elif action == "assess_capacity":
            return self.assess_organizational_capacity(
                input_data.get("current_organization", {}),
                input_data.get("project_demand", {})
            )
        elif action == "analyze_skills_gap":
            return self.analyze_skills_gap(
                input_data.get("current_skills", []),
                input_data.get("required_skills", []),
                input_data.get("team_members")
            )
        elif action == "optimize_structure":
            return self.optimize_team_structure(
                input_data.get("current_structure", {}),
                input_data.get("project_requirements", {})
            )
        elif action == "plan_capacity":
            return self.plan_capacity(
                input_data.get("project_roadmap", {}),
                input_data.get("current_capacity", {}),
                input_data.get("growth_projections")
            )
        else:
            # Default: present team
            return self.present_team(
                input_data.get("team_members", []),
                input_data.get("project_requirements")
            )

