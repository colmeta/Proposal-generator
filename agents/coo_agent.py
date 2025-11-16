"""
COO Agent - Operations Oversight and Validation
Provides operations oversight, process efficiency analysis, resource management,
timeline validation, and operational feasibility assessment.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class COOAgent(BaseAgent):
    """
    COO Agent - Operations oversight and validation authority.
    Reviews operations work, validates timelines, assesses process efficiency,
    manages resources, and evaluates operational feasibility.
    """
    
    def __init__(self):
        super().__init__(
            name="COO Agent",
            role="Operations oversight, process efficiency, and resource management",
            task_type="analysis"
        )
        self.approval_threshold = 7.0  # Minimum operational viability score (out of 10)
    
    def review_operations_plan(
        self,
        operations_plan: Dict[str, Any],
        project_requirements: Dict[str, Any],
        resource_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Review and validate operations plan
        
        Args:
            operations_plan: Operations plan from Operations Director
            project_requirements: Project requirements
            resource_constraints: Resource constraints (team size, budget, etc.)
            
        Returns:
            Operations review with approval status, feedback, and recommendations
        """
        self.log_action("Reviewing operations plan")
        
        # Extract key information
        processes = operations_plan.get("processes", [])
        workflows = operations_plan.get("workflows", [])
        resource_allocation = operations_plan.get("resource_allocation", {})
        timeline = operations_plan.get("timeline", {})
        
        # Analyze operations plan
        issues = []
        strengths = []
        
        # Check process completeness
        if not processes:
            issues.append("No processes defined in operations plan")
        else:
            strengths.append(f"Defined {len(processes)} operational processes")
        
        # Check workflow efficiency
        if not workflows:
            issues.append("No workflows defined")
        else:
            # Check for bottlenecks
            complex_workflows = [w for w in workflows if w.get("complexity", "low") in ["high", "very_high"]]
            if complex_workflows:
                issues.append(f"{len(complex_workflows)} high-complexity workflows may create bottlenecks")
            else:
                strengths.append("Workflows are appropriately scoped")
        
        # Check resource allocation
        if not resource_allocation:
            issues.append("Resource allocation not specified")
        else:
            # Validate resource adequacy
            required_resources = resource_allocation.get("required", {})
            allocated_resources = resource_allocation.get("allocated", {})
            
            for resource_type, required in required_resources.items():
                allocated = allocated_resources.get(resource_type, 0)
                if allocated < required:
                    issues.append(f"Insufficient {resource_type}: {allocated} allocated vs {required} required")
                elif allocated == required:
                    strengths.append(f"Appropriate {resource_type} allocation")
        
        # Check timeline feasibility
        timeline_duration = timeline.get("duration_months", 0)
        if timeline_duration <= 0:
            issues.append("Invalid or missing timeline duration")
        else:
            # Check against constraints
            max_duration = resource_constraints.get("max_duration_months") if resource_constraints else None
            if max_duration and timeline_duration > max_duration:
                issues.append(f"Timeline exceeds maximum duration ({timeline_duration} > {max_duration} months)")
            else:
                strengths.append(f"Timeline is feasible ({timeline_duration} months)")
        
        # Calculate review score
        score = 8.0  # Start with good score
        score -= len(issues) * 1.0
        score += len(strengths) * 0.5
        score = max(0.0, min(10.0, score))
        
        approved = score >= self.approval_threshold and len(issues) == 0
        
        return {
            "approved": approved,
            "score": round(score, 2),
            "issues": issues,
            "strengths": strengths,
            "recommendations": self._generate_operations_recommendations(issues, operations_plan),
            "feedback": self._generate_operations_feedback(approved, score, issues, strengths)
        }
    
    def analyze_process_efficiency(
        self,
        processes: List[Dict[str, Any]],
        workflows: List[Dict[str, Any]],
        performance_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze process efficiency
        
        Args:
            processes: List of operational processes
            workflows: List of workflows
            performance_metrics: Optional performance metrics
            
        Returns:
            Process efficiency analysis with bottlenecks, optimization opportunities, and recommendations
        """
        self.log_action("Analyzing process efficiency")
        
        efficiency_analysis = {
            "total_processes": len(processes),
            "total_workflows": len(workflows),
            "bottlenecks": [],
            "optimization_opportunities": [],
            "efficiency_score": 0.0
        }
        
        # Identify bottlenecks
        for workflow in workflows:
            complexity = workflow.get("complexity", "medium")
            steps = workflow.get("steps", [])
            
            if complexity in ["high", "very_high"]:
                efficiency_analysis["bottlenecks"].append({
                    "workflow": workflow.get("name", "Unknown"),
                    "issue": f"High complexity ({complexity})",
                    "steps_count": len(steps),
                    "recommendation": "Consider breaking down into smaller, parallel processes"
                })
            
            # Check for sequential dependencies
            sequential_steps = [s for s in steps if s.get("can_parallelize", False) == False]
            if len(sequential_steps) > 5:
                efficiency_analysis["bottlenecks"].append({
                    "workflow": workflow.get("name", "Unknown"),
                    "issue": f"Too many sequential steps ({len(sequential_steps)})",
                    "recommendation": "Identify steps that can be parallelized"
                })
        
        # Identify optimization opportunities
        for process in processes:
            automation_level = process.get("automation_level", "none")
            if automation_level in ["none", "low"]:
                efficiency_analysis["optimization_opportunities"].append({
                    "process": process.get("name", "Unknown"),
                    "opportunity": "Low automation level",
                    "potential_improvement": "Consider automation to reduce manual effort"
                })
        
        # Calculate efficiency score
        base_score = 7.0
        base_score -= len(efficiency_analysis["bottlenecks"]) * 1.0
        base_score += len(efficiency_analysis["optimization_opportunities"]) * 0.3  # Opportunities are positive
        efficiency_analysis["efficiency_score"] = max(0.0, min(10.0, round(base_score, 2)))
        
        # Generate recommendations
        efficiency_analysis["recommendations"] = self._generate_efficiency_recommendations(
            efficiency_analysis["bottlenecks"],
            efficiency_analysis["optimization_opportunities"]
        )
        
        return efficiency_analysis
    
    def validate_timeline(
        self,
        timeline: Dict[str, Any],
        project_scope: Dict[str, Any],
        resource_availability: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate project timeline feasibility
        
        Args:
            timeline: Project timeline
            project_scope: Project scope and deliverables
            resource_availability: Resource availability constraints
            
        Returns:
            Timeline validation with feasibility assessment and recommendations
        """
        self.log_action("Validating timeline")
        
        duration_months = timeline.get("duration_months", 0)
        milestones = timeline.get("milestones", [])
        phases = timeline.get("phases", [])
        
        validation = {
            "feasible": True,
            "duration_months": duration_months,
            "issues": [],
            "strengths": [],
            "recommendations": []
        }
        
        # Check duration
        if duration_months <= 0:
            validation["feasible"] = False
            validation["issues"].append("Invalid or missing timeline duration")
        elif duration_months < 1:
            validation["issues"].append("Timeline seems too short (< 1 month)")
        elif duration_months > 60:
            validation["issues"].append("Timeline seems too long (> 5 years) - may indicate scope issues")
        else:
            validation["strengths"].append(f"Timeline duration is reasonable ({duration_months} months)")
        
        # Check milestones
        if not milestones:
            validation["issues"].append("No milestones defined")
        else:
            validation["strengths"].append(f"Defined {len(milestones)} milestones")
            
            # Check milestone distribution
            if len(milestones) < 3:
                validation["issues"].append("Too few milestones - may lack visibility")
        
        # Check phases
        if not phases:
            validation["issues"].append("No phases defined")
        else:
            validation["strengths"].append(f"Defined {len(phases)} phases")
            
            # Check phase durations
            total_phase_duration = sum(p.get("duration_weeks", 0) for p in phases)
            if total_phase_duration > duration_months * 4.33:  # Approximate weeks in months
                validation["issues"].append("Phase durations exceed total timeline")
        
        # Check resource constraints
        if resource_availability:
            required_team_size = project_scope.get("team_size", 0)
            available_team_size = resource_availability.get("team_size", 0)
            
            if available_team_size < required_team_size:
                validation["feasible"] = False
                validation["issues"].append(
                    f"Insufficient team size: {available_team_size} available vs {required_team_size} required"
                )
        
        # Calculate feasibility score
        score = 8.0
        score -= len(validation["issues"]) * 1.5
        score += len(validation["strengths"]) * 0.5
        validation["feasibility_score"] = max(0.0, min(10.0, round(score, 2)))
        
        if validation["feasibility_score"] < 7.0:
            validation["feasible"] = False
        
        # Generate recommendations
        validation["recommendations"] = self._generate_timeline_recommendations(validation["issues"])
        
        return validation
    
    def assess_operational_feasibility(
        self,
        operations_plan: Dict[str, Any],
        resource_availability: Dict[str, Any],
        timeline: Dict[str, Any],
        process_efficiency: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess overall operational feasibility
        
        Args:
            operations_plan: Operations plan
            resource_availability: Available resources
            timeline: Project timeline
            process_efficiency: Process efficiency analysis
            
        Returns:
            Operational feasibility assessment with recommendation
        """
        self.log_action("Assessing operational feasibility")
        
        feasibility = {
            "feasible": True,
            "feasibility_score": 0.0,
            "factors": [],
            "risks": [],
            "recommendations": []
        }
        
        # Check resource adequacy
        required = operations_plan.get("resource_allocation", {}).get("required", {})
        available = resource_availability
        
        for resource_type, required_amount in required.items():
            available_amount = available.get(resource_type, 0)
            if available_amount >= required_amount:
                feasibility["factors"].append(f"Sufficient {resource_type} available")
            else:
                feasibility["risks"].append(f"Insufficient {resource_type}: {available_amount} < {required_amount}")
                feasibility["feasible"] = False
        
        # Check timeline feasibility
        timeline_validation = self.validate_timeline(timeline, {}, resource_availability)
        if not timeline_validation.get("feasible", False):
            feasibility["risks"].extend(timeline_validation.get("issues", []))
            feasibility["feasible"] = False
        else:
            feasibility["factors"].append("Timeline is feasible")
        
        # Check process efficiency
        efficiency_score = process_efficiency.get("efficiency_score", 0)
        if efficiency_score < 6.0:
            feasibility["risks"].append(f"Low process efficiency score: {efficiency_score}/10")
        else:
            feasibility["factors"].append(f"Good process efficiency: {efficiency_score}/10")
        
        # Calculate overall feasibility score
        score = 5.0  # Start neutral
        score += len(feasibility["factors"]) * 1.0
        score -= len(feasibility["risks"]) * 1.5
        score = max(0.0, min(10.0, score))
        feasibility["feasibility_score"] = round(score, 2)
        
        if feasibility["feasibility_score"] < 7.0:
            feasibility["feasible"] = False
        
        # Generate recommendation
        if feasibility["feasible"]:
            feasibility["recommendation"] = "OPERATIONALLY FEASIBLE - Proceed with operations plan"
        else:
            feasibility["recommendation"] = "NOT OPERATIONALLY FEASIBLE - Address identified risks before proceeding"
        
        feasibility["recommendations"] = self._generate_feasibility_recommendations(feasibility["risks"])
        
        return feasibility
    
    def _generate_operations_recommendations(
        self,
        issues: List[str],
        operations_plan: Dict[str, Any]
    ) -> List[str]:
        """Generate operations recommendations"""
        recommendations = []
        
        for issue in issues:
            if "process" in issue.lower():
                recommendations.append("Define clear operational processes with documented steps")
            elif "workflow" in issue.lower():
                recommendations.append("Review and optimize workflows to reduce complexity")
            elif "resource" in issue.lower():
                recommendations.append("Reassess resource allocation and availability")
            elif "timeline" in issue.lower():
                recommendations.append("Review timeline and adjust scope or resources accordingly")
            else:
                recommendations.append(f"Address: {issue}")
        
        return recommendations
    
    def _generate_operations_feedback(
        self,
        approved: bool,
        score: float,
        issues: List[str],
        strengths: List[str]
    ) -> str:
        """Generate operations review feedback"""
        if approved:
            feedback = f"Operations plan APPROVED. Score: {score}/10. "
            if strengths:
                feedback += f"Strengths: {', '.join(strengths[:2])}."
        else:
            feedback = f"Operations plan NOT APPROVED. Score: {score}/10. "
            if issues:
                feedback += f"Issues: {', '.join(issues[:3])}."
        
        return feedback
    
    def _generate_efficiency_recommendations(
        self,
        bottlenecks: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate efficiency recommendations"""
        recommendations = []
        
        if bottlenecks:
            recommendations.append(f"Address {len(bottlenecks)} identified bottlenecks")
            for bottleneck in bottlenecks[:3]:  # Top 3
                recommendations.append(f"- {bottleneck.get('recommendation', '')}")
        
        if opportunities:
            recommendations.append(f"Consider {len(opportunities)} optimization opportunities")
            for opp in opportunities[:3]:  # Top 3
                recommendations.append(f"- {opp.get('potential_improvement', '')}")
        
        if not bottlenecks and not opportunities:
            recommendations.append("Process efficiency is good - continue monitoring")
        
        return recommendations
    
    def _generate_timeline_recommendations(self, issues: List[str]) -> List[str]:
        """Generate timeline recommendations"""
        recommendations = []
        
        for issue in issues:
            if "duration" in issue.lower():
                recommendations.append("Review and adjust timeline duration based on scope")
            elif "milestone" in issue.lower():
                recommendations.append("Define clear milestones for better project visibility")
            elif "phase" in issue.lower():
                recommendations.append("Review phase definitions and durations")
            elif "resource" in issue.lower():
                recommendations.append("Adjust timeline based on resource availability")
            else:
                recommendations.append(f"Address: {issue}")
        
        return recommendations
    
    def _generate_feasibility_recommendations(self, risks: List[str]) -> List[str]:
        """Generate feasibility recommendations"""
        recommendations = []
        
        for risk in risks:
            if "insufficient" in risk.lower():
                recommendations.append("Secure additional resources or reduce scope")
            elif "timeline" in risk.lower():
                recommendations.append("Extend timeline or increase resource allocation")
            elif "efficiency" in risk.lower():
                recommendations.append("Optimize processes to improve efficiency")
            else:
                recommendations.append(f"Mitigate: {risk}")
        
        return recommendations
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - COO workflow
        
        Expected input:
        {
            "action": "review_operations" | "analyze_efficiency" | "validate_timeline" | "assess_feasibility",
            "operations_plan": {...},
            "processes": [...],
            "workflows": [...],
            "timeline": {...},
            ...
        }
        """
        action = input_data.get("action", "review_operations")
        
        if action == "review_operations":
            return self.review_operations_plan(
                input_data.get("operations_plan", {}),
                input_data.get("project_requirements", {}),
                input_data.get("resource_constraints")
            )
        elif action == "analyze_efficiency":
            return self.analyze_process_efficiency(
                input_data.get("processes", []),
                input_data.get("workflows", []),
                input_data.get("performance_metrics")
            )
        elif action == "validate_timeline":
            return self.validate_timeline(
                input_data.get("timeline", {}),
                input_data.get("project_scope", {}),
                input_data.get("resource_availability")
            )
        elif action == "assess_feasibility":
            return self.assess_operational_feasibility(
                input_data.get("operations_plan", {}),
                input_data.get("resource_availability", {}),
                input_data.get("timeline", {}),
                input_data.get("process_efficiency", {})
            )
        else:
            # Default: review operations
            return self.review_operations_plan(
                input_data.get("operations_plan", {}),
                input_data.get("project_requirements", {}),
                input_data.get("resource_constraints")
            )

