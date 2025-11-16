"""
Operations Director Agent
Handles process optimization, workflow efficiency analysis, resource allocation,
timeline feasibility, operational capacity assessment, and risk mitigation strategies.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class OperationsDirectorAgent(BaseAgent):
    """
    Operations Director Agent - Process and operations specialist.
    Optimizes processes, analyzes workflow efficiency, allocates resources,
    validates timelines, assesses capacity, and develops risk mitigation strategies.
    """
    
    def __init__(self):
        super().__init__(
            name="Operations Director",
            role="Process optimization, workflow efficiency, and resource allocation",
            task_type="analysis"
        )
    
    def optimize_processes(
        self,
        current_processes: List[Dict[str, Any]],
        project_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize operational processes
        
        Args:
            current_processes: Current process definitions
            project_requirements: Project requirements
            
        Returns:
            Optimized processes with improvements and recommendations
        """
        self.log_action("Optimizing processes")
        
        prompt = f"""As an Operations Director, optimize these operational processes for efficiency.

Current Processes:
{json.dumps(current_processes, indent=2)}

Project Requirements:
{json.dumps(project_requirements, indent=2)}

Optimize for:
1. Efficiency and speed
2. Resource utilization
3. Quality and consistency
4. Scalability
5. Automation opportunities

Return JSON format:
{{
    "optimized_processes": [
        {{
            "process_name": "<name>",
            "current_steps": <number>,
            "optimized_steps": <number>,
            "improvements": ["<improvement 1>", "<improvement 2>"],
            "efficiency_gain": "<percentage>",
            "automation_opportunities": ["<opportunity 1>"]
        }}
    ],
    "overall_efficiency_improvement": "<percentage>",
    "recommendations": ["<recommendation 1>", "<recommendation 2>"]
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
                optimization = json.loads(json_match.group())
                return optimization
        except Exception as e:
            logger.warning(f"Process optimization LLM call failed: {e}")
        
        # Fallback: return current processes with basic optimization
        return {
            "optimized_processes": current_processes,
            "overall_efficiency_improvement": "0%",
            "recommendations": ["Review processes for automation opportunities"]
        }
    
    def analyze_workflow_efficiency(
        self,
        workflows: List[Dict[str, Any]],
        performance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze workflow efficiency
        
        Args:
            workflows: List of workflows to analyze
            performance_data: Optional performance metrics
            
        Returns:
            Workflow efficiency analysis with bottlenecks, improvements, and metrics
        """
        self.log_action("Analyzing workflow efficiency")
        
        analysis = {
            "total_workflows": len(workflows),
            "workflow_analysis": [],
            "bottlenecks": [],
            "efficiency_score": 0.0,
            "recommendations": []
        }
        
        # Analyze each workflow
        for workflow in workflows:
            workflow_name = workflow.get("name", "Unknown")
            steps = workflow.get("steps", [])
            complexity = workflow.get("complexity", "medium")
            
            # Calculate efficiency metrics
            total_steps = len(steps)
            parallelizable_steps = len([s for s in steps if s.get("can_parallelize", False)])
            sequential_steps = total_steps - parallelizable_steps
            
            # Identify bottlenecks
            if sequential_steps > 5:
                analysis["bottlenecks"].append({
                    "workflow": workflow_name,
                    "issue": f"Too many sequential steps ({sequential_steps})",
                    "impact": "Reduces parallelization opportunities"
                })
            
            if complexity in ["high", "very_high"]:
                analysis["bottlenecks"].append({
                    "workflow": workflow_name,
                    "issue": f"High complexity ({complexity})",
                    "impact": "Increases execution time and error risk"
                })
            
            # Calculate workflow efficiency score
            efficiency = 7.0  # Base score
            if parallelizable_steps > sequential_steps:
                efficiency += 1.0
            if complexity == "low":
                efficiency += 1.0
            elif complexity == "very_high":
                efficiency -= 2.0
            
            analysis["workflow_analysis"].append({
                "workflow": workflow_name,
                "total_steps": total_steps,
                "sequential_steps": sequential_steps,
                "parallelizable_steps": parallelizable_steps,
                "complexity": complexity,
                "efficiency_score": max(0.0, min(10.0, round(efficiency, 2)))
            })
        
        # Calculate overall efficiency score
        if analysis["workflow_analysis"]:
            avg_efficiency = sum(
                w["efficiency_score"] for w in analysis["workflow_analysis"]
            ) / len(analysis["workflow_analysis"])
            analysis["efficiency_score"] = round(avg_efficiency, 2)
        
        # Generate recommendations
        if analysis["bottlenecks"]:
            analysis["recommendations"].append(
                f"Address {len(analysis['bottlenecks'])} identified bottlenecks"
            )
            for bottleneck in analysis["bottlenecks"][:3]:
                analysis["recommendations"].append(
                    f"- {bottleneck['workflow']}: {bottleneck['issue']}"
                )
        
        if analysis["efficiency_score"] < 7.0:
            analysis["recommendations"].append(
                "Overall workflow efficiency is below optimal - consider process redesign"
            )
        
        return analysis
    
    def allocate_resources(
        self,
        project_requirements: Dict[str, Any],
        available_resources: Dict[str, Any],
        timeline: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Allocate resources for the project
        
        Args:
            project_requirements: Project requirements and scope
            available_resources: Available resources (team, budget, equipment)
            timeline: Project timeline (optional)
            
        Returns:
            Resource allocation plan with assignments, gaps, and recommendations
        """
        self.log_action("Allocating resources")
        
        allocation = {
            "allocated": {},
            "required": {},
            "gaps": {},
            "utilization": {},
            "recommendations": []
        }
        
        # Determine required resources
        team_size = project_requirements.get("team_size", 0)
        budget = project_requirements.get("budget", 0)
        equipment = project_requirements.get("equipment", [])
        
        allocation["required"] = {
            "team_size": team_size,
            "budget": budget,
            "equipment_count": len(equipment)
        }
        
        # Allocate available resources
        available_team = available_resources.get("team_size", 0)
        available_budget = available_resources.get("budget", 0)
        available_equipment = available_resources.get("equipment", [])
        
        allocation["allocated"] = {
            "team_size": min(available_team, team_size),
            "budget": min(available_budget, budget),
            "equipment_count": min(len(available_equipment), len(equipment))
        }
        
        # Identify gaps
        if available_team < team_size:
            allocation["gaps"]["team_size"] = team_size - available_team
            allocation["recommendations"].append(
                f"Need {team_size - available_team} additional team members"
            )
        
        if available_budget < budget:
            allocation["gaps"]["budget"] = budget - available_budget
            allocation["recommendations"].append(
                f"Budget shortfall: ${budget - available_budget:,.2f}"
            )
        
        if len(available_equipment) < len(equipment):
            allocation["gaps"]["equipment"] = len(equipment) - len(available_equipment)
            allocation["recommendations"].append(
                f"Need {len(equipment) - len(available_equipment)} additional equipment items"
            )
        
        # Calculate utilization
        if available_team > 0:
            allocation["utilization"]["team"] = round(
                (allocation["allocated"]["team_size"] / available_team) * 100, 2
            )
        if available_budget > 0:
            allocation["utilization"]["budget"] = round(
                (allocation["allocated"]["budget"] / available_budget) * 100, 2
            )
        
        return allocation
    
    def assess_timeline_feasibility(
        self,
        timeline: Dict[str, Any],
        project_scope: Dict[str, Any],
        resource_allocation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess timeline feasibility
        
        Args:
            timeline: Project timeline
            project_scope: Project scope and deliverables
            resource_allocation: Resource allocation plan
            
        Returns:
            Timeline feasibility assessment with validation and recommendations
        """
        self.log_action("Assessing timeline feasibility")
        
        feasibility = {
            "feasible": True,
            "duration_months": timeline.get("duration_months", 0),
            "issues": [],
            "strengths": [],
            "recommendation": ""
        }
        
        duration = timeline.get("duration_months", 0)
        milestones = timeline.get("milestones", [])
        phases = timeline.get("phases", [])
        
        # Check duration
        if duration <= 0:
            feasibility["feasible"] = False
            feasibility["issues"].append("Invalid timeline duration")
        elif duration < 1:
            feasibility["issues"].append("Timeline too short (< 1 month)")
        elif duration > 60:
            feasibility["issues"].append("Timeline too long (> 5 years)")
        else:
            feasibility["strengths"].append(f"Timeline duration is reasonable ({duration} months)")
        
        # Check resource adequacy
        gaps = resource_allocation.get("gaps", {})
        if gaps:
            feasibility["feasible"] = False
            for resource, gap in gaps.items():
                feasibility["issues"].append(f"Resource gap: {resource} ({gap})")
        else:
            feasibility["strengths"].append("All required resources are available")
        
        # Check milestone distribution
        if not milestones:
            feasibility["issues"].append("No milestones defined")
        elif len(milestones) < 3:
            feasibility["issues"].append("Too few milestones for visibility")
        else:
            feasibility["strengths"].append(f"Good milestone distribution ({len(milestones)} milestones)")
        
        # Check phase alignment
        if phases:
            total_phase_duration = sum(p.get("duration_weeks", 0) for p in phases)
            timeline_weeks = duration * 4.33  # Approximate
            if total_phase_duration > timeline_weeks:
                feasibility["issues"].append("Phase durations exceed timeline")
            else:
                feasibility["strengths"].append("Phases align with timeline")
        
        # Generate recommendation
        if feasibility["feasible"] and not feasibility["issues"]:
            feasibility["recommendation"] = "Timeline is FEASIBLE - proceed as planned"
        elif feasibility["issues"]:
            feasibility["recommendation"] = "Timeline has ISSUES - address before proceeding"
            feasibility["feasible"] = False
        else:
            feasibility["recommendation"] = "Timeline is CONDITIONALLY FEASIBLE - monitor closely"
        
        return feasibility
    
    def assess_operational_capacity(
        self,
        current_capacity: Dict[str, Any],
        project_demand: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess operational capacity
        
        Args:
            current_capacity: Current operational capacity
            project_demand: Project resource demands
            
        Returns:
            Capacity assessment with utilization, constraints, and recommendations
        """
        self.log_action("Assessing operational capacity")
        
        assessment = {
            "capacity_adequate": True,
            "utilization": {},
            "constraints": [],
            "recommendations": []
        }
        
        # Check team capacity
        current_team = current_capacity.get("team_size", 0)
        required_team = project_demand.get("team_size", 0)
        
        if current_team > 0:
            team_utilization = (required_team / current_team) * 100
            assessment["utilization"]["team"] = round(team_utilization, 2)
            
            if team_utilization > 100:
                assessment["capacity_adequate"] = False
                assessment["constraints"].append(
                    f"Team capacity exceeded: {team_utilization:.1f}% utilization"
                )
                assessment["recommendations"].append("Hire additional team members or reduce scope")
            elif team_utilization > 80:
                assessment["constraints"].append(
                    f"High team utilization: {team_utilization:.1f}% - risk of burnout"
                )
                assessment["recommendations"].append("Consider additional resources or timeline extension")
        
        # Check infrastructure capacity
        current_infrastructure = current_capacity.get("infrastructure_capacity", 0)
        required_infrastructure = project_demand.get("infrastructure_requirements", 0)
        
        if current_infrastructure > 0:
            infra_utilization = (required_infrastructure / current_infrastructure) * 100
            assessment["utilization"]["infrastructure"] = round(infra_utilization, 2)
            
            if infra_utilization > 100:
                assessment["capacity_adequate"] = False
                assessment["constraints"].append("Infrastructure capacity exceeded")
                assessment["recommendations"].append("Scale up infrastructure")
        
        if assessment["capacity_adequate"] and not assessment["constraints"]:
            assessment["recommendations"].append("Capacity is adequate for project demands")
        
        return assessment
    
    def develop_risk_mitigation_strategies(
        self,
        identified_risks: List[Dict[str, Any]],
        operations_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Develop risk mitigation strategies
        
        Args:
            identified_risks: List of identified operational risks
            operations_context: Operations context and constraints
            
        Returns:
            Risk mitigation strategies with action plans and responsibilities
        """
        self.log_action("Developing risk mitigation strategies")
        
        strategies = {
            "mitigation_plans": [],
            "priority_actions": [],
            "monitoring_requirements": []
        }
        
        # Develop mitigation for each risk
        for risk in identified_risks:
            risk_name = risk.get("risk", "Unknown risk")
            severity = risk.get("severity", "medium")
            category = risk.get("category", "operational")
            
            mitigation = {
                "risk": risk_name,
                "severity": severity,
                "category": category,
                "mitigation_strategy": "",
                "actions": [],
                "owner": "Operations Team",
                "timeline": "Ongoing"
            }
            
            # Generate mitigation based on category
            if category == "resource":
                mitigation["mitigation_strategy"] = "Resource contingency planning"
                mitigation["actions"] = [
                    "Identify backup resources",
                    "Cross-train team members",
                    "Establish vendor relationships"
                ]
            elif category == "timeline":
                mitigation["mitigation_strategy"] = "Timeline buffer and monitoring"
                mitigation["actions"] = [
                    "Add 10-15% buffer to timeline",
                    "Implement weekly progress reviews",
                    "Identify critical path dependencies"
                ]
            elif category == "process":
                mitigation["mitigation_strategy"] = "Process standardization and documentation"
                mitigation["actions"] = [
                    "Document all processes",
                    "Create runbooks and playbooks",
                    "Implement quality checkpoints"
                ]
            else:
                mitigation["mitigation_strategy"] = "General risk monitoring and response"
                mitigation["actions"] = [
                    "Monitor risk indicators",
                    "Develop contingency plans",
                    "Regular risk reviews"
                ]
            
            strategies["mitigation_plans"].append(mitigation)
            
            # Add to priority actions if high severity
            if severity in ["high", "critical"]:
                strategies["priority_actions"].extend(mitigation["actions"])
        
        # Add monitoring requirements
        strategies["monitoring_requirements"] = [
            "Weekly risk review meetings",
            "Monthly capacity assessments",
            "Quarterly process efficiency reviews"
        ]
        
        return strategies
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - Operations Director workflow
        
        Expected input:
        {
            "action": "optimize_processes" | "analyze_workflow" | "allocate_resources" |
                      "assess_timeline" | "assess_capacity" | "mitigate_risks",
            "current_processes": [...],
            "workflows": [...],
            "project_requirements": {...},
            ...
        }
        """
        action = input_data.get("action", "optimize_processes")
        
        if action == "optimize_processes":
            return self.optimize_processes(
                input_data.get("current_processes", []),
                input_data.get("project_requirements", {})
            )
        elif action == "analyze_workflow":
            return self.analyze_workflow_efficiency(
                input_data.get("workflows", []),
                input_data.get("performance_data")
            )
        elif action == "allocate_resources":
            return self.allocate_resources(
                input_data.get("project_requirements", {}),
                input_data.get("available_resources", {}),
                input_data.get("timeline")
            )
        elif action == "assess_timeline":
            return self.assess_timeline_feasibility(
                input_data.get("timeline", {}),
                input_data.get("project_scope", {}),
                input_data.get("resource_allocation", {})
            )
        elif action == "assess_capacity":
            return self.assess_operational_capacity(
                input_data.get("current_capacity", {}),
                input_data.get("project_demand", {})
            )
        elif action == "mitigate_risks":
            return self.develop_risk_mitigation_strategies(
                input_data.get("identified_risks", []),
                input_data.get("operations_context", {})
            )
        else:
            # Default: optimize processes
            return self.optimize_processes(
                input_data.get("current_processes", []),
                input_data.get("project_requirements", {})
            )

