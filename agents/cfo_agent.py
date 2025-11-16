"""
CFO Agent - Financial Oversight and Approval Authority
Provides financial oversight, budget approval, ROI calculations,
financial risk assessment, and cost-benefit analysis.
"""

from typing import Dict, Any, List, Optional, Tuple
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)


class CFOAgent(BaseAgent):
    """
    CFO Agent - Financial oversight and approval authority.
    Reviews financial work, approves budgets, calculates ROI,
    assesses financial risks, and performs cost-benefit analysis.
    """
    
    def __init__(self):
        super().__init__(
            name="CFO Agent",
            role="Financial oversight, budget approval, and risk assessment",
            task_type="analysis"
        )
        self.approval_threshold = 7.0  # Minimum financial viability score (out of 10)
    
    def review_budget(
        self,
        budget: Dict[str, Any],
        project_requirements: Dict[str, Any],
        financial_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Review and approve/reject budget
        
        Args:
            budget: Budget from Finance Director
            project_requirements: Project requirements
            financial_constraints: Financial constraints (max budget, etc.)
            
        Returns:
            Budget review with approval status, feedback, and recommendations
        """
        self.log_action("Reviewing budget")
        
        total_budget = budget.get("total_budget", 0)
        categories = budget.get("categories", [])
        
        # Check against constraints
        max_budget = financial_constraints.get("max_budget") if financial_constraints else None
        budget_within_constraints = True
        if max_budget and total_budget > max_budget:
            budget_within_constraints = False
        
        # Analyze budget structure
        issues = []
        strengths = []
        
        if total_budget <= 0:
            issues.append("Budget total is zero or negative")
        
        if not categories:
            issues.append("No budget categories defined")
        else:
            # Check for contingency
            contingency = budget.get("contingency_amount", 0)
            contingency_pct = budget.get("contingency_percentage", 0)
            if contingency_pct < 5:
                issues.append(f"Contingency too low ({contingency_pct}%) - recommend at least 10%")
            elif contingency_pct >= 10:
                strengths.append(f"Appropriate contingency buffer ({contingency_pct}%)")
            
            # Check category distribution
            personnel_pct = sum(
                cat.get("amount", 0) for cat in categories 
                if "personnel" in cat.get("category", "").lower()
            ) / total_budget * 100 if total_budget > 0 else 0
            
            if personnel_pct > 70:
                issues.append(f"Personnel costs very high ({personnel_pct:.1f}%) - consider optimization")
            elif personnel_pct < 30:
                issues.append(f"Personnel costs low ({personnel_pct:.1f}%) - verify adequacy")
        
        if max_budget and budget_within_constraints:
            strengths.append(f"Budget within constraints (${total_budget:,.2f} <= ${max_budget:,.2f})")
        elif max_budget and not budget_within_constraints:
            issues.append(
                f"Budget exceeds constraints by ${total_budget - max_budget:,.2f} "
                f"(${total_budget:,.2f} > ${max_budget:,.2f})"
            )
        
        # Calculate review score
        score = 8.0  # Start with good score
        score -= len(issues) * 1.0
        score += len(strengths) * 0.5
        score = max(0.0, min(10.0, score))
        
        approved = score >= self.approval_threshold and budget_within_constraints and len(issues) == 0
        
        return {
            "approved": approved,
            "score": round(score, 2),
            "total_budget": total_budget,
            "within_constraints": budget_within_constraints,
            "issues": issues,
            "strengths": strengths,
            "recommendations": self._generate_budget_recommendations(issues, budget),
            "feedback": self._generate_budget_feedback(approved, score, issues, strengths)
        }
    
    def calculate_roi(
        self,
        investment: float,
        returns: Dict[str, Any],
        time_period: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate Return on Investment (ROI)
        
        Args:
            investment: Total investment amount
            returns: Returns data (can include multiple scenarios)
            time_period: Time period in months (optional)
            
        Returns:
            ROI analysis with multiple metrics and scenarios
        """
        self.log_action("Calculating ROI")
        
        if investment <= 0:
            return {
                "error": "Investment must be positive",
                "roi_percentage": 0,
                "net_return": 0
            }
        
        # Handle different return formats
        if isinstance(returns, dict):
            # Multiple scenarios
            roi_results = {}
            for scenario, return_data in returns.items():
                if isinstance(return_data, (int, float)):
                    total_return = return_data
                elif isinstance(return_data, dict):
                    total_return = return_data.get("total_return", return_data.get("revenue", 0))
                else:
                    total_return = 0
                
                net_return = total_return - investment
                roi_pct = (net_return / investment * 100) if investment > 0 else 0
                
                roi_results[scenario] = {
                    "total_return": total_return,
                    "investment": investment,
                    "net_return": net_return,
                    "roi_percentage": round(roi_pct, 2),
                    "payback_period_months": self._calculate_payback_period(investment, return_data, time_period)
                }
            
            # Calculate average/realistic ROI
            realistic = roi_results.get("realistic", roi_results.get(list(roi_results.keys())[0]))
            
            return {
                "investment": investment,
                "scenarios": roi_results,
                "roi_percentage": realistic["roi_percentage"],
                "net_return": realistic["net_return"],
                "payback_period_months": realistic["payback_period_months"],
                "time_period_months": time_period
            }
        else:
            # Single return value
            total_return = float(returns) if isinstance(returns, (int, float)) else 0
            net_return = total_return - investment
            roi_pct = (net_return / investment * 100) if investment > 0 else 0
            
            return {
                "investment": investment,
                "total_return": total_return,
                "net_return": net_return,
                "roi_percentage": round(roi_pct, 2),
                "payback_period_months": self._calculate_payback_period(investment, returns, time_period)
            }
    
    def assess_financial_risk(
        self,
        budget: Dict[str, Any],
        financial_model: Dict[str, Any],
        revenue_projections: Dict[str, Any],
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess financial risks
        
        Args:
            budget: Project budget
            financial_model: Financial model
            revenue_projections: Revenue projections
            market_conditions: Market conditions and risks
            
        Returns:
            Financial risk assessment with risk factors, severity, and mitigation
        """
        self.log_action("Assessing financial risks")
        
        risks = []
        total_budget = budget.get("total_budget", 0)
        
        # Budget risks
        if total_budget == 0:
            risks.append({
                "risk": "Zero budget",
                "category": "budget",
                "severity": "high",
                "probability": "high",
                "impact": "Project cannot proceed"
            })
        
        # Revenue risk
        scenarios = revenue_projections.get("scenarios", {})
        conservative = scenarios.get("conservative", {})
        realistic = scenarios.get("realistic", {})
        
        if conservative.get("annual_revenue", 0) < total_budget:
            risks.append({
                "risk": "Revenue shortfall in conservative scenario",
                "category": "revenue",
                "severity": "high",
                "probability": "medium",
                "impact": "Project may not be financially viable"
            })
        
        # Break-even risk
        break_even_month = financial_model.get("key_metrics", {}).get("break_even_month")
        timeline_months = financial_model.get("timeline_months", 12)
        
        if break_even_month and break_even_month > timeline_months:
            risks.append({
                "risk": f"Break-even beyond project timeline (month {break_even_month} vs {timeline_months} months)",
                "category": "timeline",
                "severity": "medium",
                "probability": "high",
                "impact": "Project may not achieve financial sustainability"
            })
        
        # Market risks
        if market_conditions:
            market_volatility = market_conditions.get("volatility", "low")
            if market_volatility in ["high", "very_high"]:
                risks.append({
                    "risk": "High market volatility",
                    "category": "market",
                    "severity": "medium",
                    "probability": "medium",
                    "impact": "Revenue projections may be unreliable"
                })
        
        # Contingency risk
        contingency_pct = budget.get("contingency_percentage", 0)
        if contingency_pct < 5:
            risks.append({
                "risk": "Insufficient contingency buffer",
                "category": "budget",
                "severity": "medium",
                "probability": "medium",
                "impact": "Budget overruns may not be covered"
            })
        
        # Calculate overall risk score
        risk_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        total_risk_score = sum(
            risk_scores.get(risk.get("severity", "low"), 1) 
            for risk in risks
        )
        max_possible_score = len(risks) * 4 if risks else 1
        risk_score = (total_risk_score / max_possible_score * 10) if max_possible_score > 0 else 0
        
        # Categorize overall risk level
        if risk_score >= 7.5:
            overall_risk_level = "high"
        elif risk_score >= 5.0:
            overall_risk_level = "medium"
        else:
            overall_risk_level = "low"
        
        return {
            "overall_risk_level": overall_risk_level,
            "risk_score": round(risk_score, 2),
            "risks": risks,
            "risk_by_category": self._categorize_risks(risks),
            "mitigation_strategies": self._generate_risk_mitigation(risks),
            "recommendations": self._generate_risk_recommendations(risks, overall_risk_level)
        }
    
    def perform_cost_benefit_analysis(
        self,
        costs: Dict[str, Any],
        benefits: Dict[str, Any],
        time_horizon: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform cost-benefit analysis
        
        Args:
            costs: Cost data (budget, ongoing costs, etc.)
            benefits: Benefit data (revenue, value, etc.)
            time_horizon: Analysis time horizon in months
            
        Returns:
            Cost-benefit analysis with NPV, BCR, and recommendations
        """
        self.log_action("Performing cost-benefit analysis")
        
        # Extract costs
        total_costs = costs.get("total_budget", costs.get("total_cost", 0))
        ongoing_costs = costs.get("ongoing_monthly_cost", 0)
        
        # Extract benefits
        if isinstance(benefits, dict):
            total_benefits = benefits.get("total_revenue", benefits.get("total_value", 0))
            monthly_benefits = benefits.get("monthly_revenue", benefits.get("monthly_value", 0))
        else:
            total_benefits = float(benefits) if isinstance(benefits, (int, float)) else 0
            monthly_benefits = 0
        
        time_horizon = time_horizon or 12  # Default 12 months
        
        # Calculate net benefit
        total_net_benefit = total_benefits - total_costs
        
        # Calculate Benefit-Cost Ratio (BCR)
        bcr = (total_benefits / total_costs) if total_costs > 0 else 0
        
        # Calculate simple NPV (assuming no discounting for simplicity)
        # In a real scenario, you'd apply discount rates
        npv = total_net_benefit
        
        # Calculate payback period
        if monthly_benefits > ongoing_costs:
            monthly_net_benefit = monthly_benefits - ongoing_costs
            payback_months = total_costs / monthly_net_benefit if monthly_net_benefit > 0 else None
        else:
            payback_months = None
        
        # Determine recommendation
        if bcr > 1.5 and npv > 0:
            recommendation = "STRONGLY RECOMMENDED - High benefit-cost ratio and positive NPV"
        elif bcr > 1.0 and npv > 0:
            recommendation = "RECOMMENDED - Positive benefit-cost ratio and NPV"
        elif bcr > 1.0:
            recommendation = "CONDITIONALLY RECOMMENDED - Positive BCR but negative NPV"
        else:
            recommendation = "NOT RECOMMENDED - Costs exceed benefits"
        
        return {
            "total_costs": total_costs,
            "total_benefits": total_benefits,
            "net_benefit": total_net_benefit,
            "benefit_cost_ratio": round(bcr, 2),
            "npv": round(npv, 2),
            "payback_period_months": int(payback_months) if payback_months else None,
            "time_horizon_months": time_horizon,
            "recommendation": recommendation,
            "key_metrics": {
                "bcr": round(bcr, 2),
                "npv": round(npv, 2),
                "roi_percentage": ((total_net_benefit / total_costs) * 100) if total_costs > 0 else 0
            }
        }
    
    def approve_financial_plan(
        self,
        budget: Dict[str, Any],
        financial_model: Dict[str, Any],
        revenue_projections: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        cost_benefit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Final approval of financial plan
        
        Args:
            budget: Budget review result
            financial_model: Financial model
            revenue_projections: Revenue projections
            risk_assessment: Risk assessment
            cost_benefit: Cost-benefit analysis
            
        Returns:
            Final approval decision with comprehensive feedback
        """
        self.log_action("Making final financial approval decision")
        
        # Collect approval factors
        budget_approved = budget.get("approved", False)
        risk_level = risk_assessment.get("overall_risk_level", "medium")
        bcr = cost_benefit.get("benefit_cost_ratio", 0)
        npv = cost_benefit.get("npv", 0)
        
        # Calculate overall approval score
        score = 5.0  # Start neutral
        
        if budget_approved:
            score += 2.0
        
        if risk_level == "low":
            score += 2.0
        elif risk_level == "medium":
            score += 1.0
        # high risk: no addition
        
        if bcr > 1.5:
            score += 2.0
        elif bcr > 1.0:
            score += 1.0
        
        if npv > 0:
            score += 1.0
        
        score = min(10.0, max(0.0, score))
        
        # Determine approval
        approved = (
            budget_approved and
            risk_level in ["low", "medium"] and
            bcr > 1.0 and
            score >= self.approval_threshold
        )
        
        # Collect issues
        issues = []
        if not budget_approved:
            issues.extend(budget.get("issues", []))
        
        if risk_level == "high":
            issues.append("High financial risk level")
        
        if bcr <= 1.0:
            issues.append(f"Benefit-cost ratio too low ({bcr:.2f})")
        
        if npv < 0:
            issues.append(f"Negative NPV ({npv:,.2f})")
        
        return {
            "approved": approved,
            "approval_score": round(score, 2),
            "budget_approved": budget_approved,
            "risk_level": risk_level,
            "benefit_cost_ratio": bcr,
            "npv": npv,
            "issues": issues,
            "feedback": self._generate_approval_feedback(approved, score, issues),
            "conditions": self._generate_approval_conditions(approved, issues) if not approved else []
        }
    
    def _calculate_payback_period(
        self,
        investment: float,
        returns: Any,
        time_period: Optional[int]
    ) -> Optional[int]:
        """Calculate payback period in months"""
        if time_period and time_period > 0:
            if isinstance(returns, dict):
                monthly_return = returns.get("monthly_revenue", returns.get("monthly_return", 0))
            elif isinstance(returns, (int, float)):
                monthly_return = float(returns) / time_period
            else:
                return None
            
            if monthly_return > 0:
                return int(np.ceil(investment / monthly_return))
        
        return None
    
    def _categorize_risks(self, risks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize risks by category"""
        categorized = {}
        for risk in risks:
            category = risk.get("category", "other")
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(risk)
        return categorized
    
    def _generate_budget_recommendations(
        self,
        issues: List[str],
        budget: Dict[str, Any]
    ) -> List[str]:
        """Generate budget recommendations"""
        recommendations = []
        
        for issue in issues:
            if "contingency" in issue.lower():
                recommendations.append("Increase contingency to at least 10% of total budget")
            elif "personnel" in issue.lower():
                recommendations.append("Review personnel cost allocation and optimize if possible")
            elif "exceeds constraints" in issue.lower():
                recommendations.append("Reduce budget or negotiate higher funding limit")
            else:
                recommendations.append(f"Address: {issue}")
        
        return recommendations
    
    def _generate_budget_feedback(
        self,
        approved: bool,
        score: float,
        issues: List[str],
        strengths: List[str]
    ) -> str:
        """Generate budget review feedback"""
        if approved:
            feedback = f"Budget APPROVED. Score: {score}/10. "
            if strengths:
                feedback += f"Strengths: {', '.join(strengths[:2])}."
        else:
            feedback = f"Budget NOT APPROVED. Score: {score}/10. "
            if issues:
                feedback += f"Issues: {', '.join(issues[:3])}."
        
        return feedback
    
    def _generate_risk_mitigation(self, risks: List[Dict[str, Any]]) -> List[str]:
        """Generate risk mitigation strategies"""
        mitigations = []
        
        for risk in risks:
            category = risk.get("category", "")
            severity = risk.get("severity", "medium")
            
            if category == "budget":
                mitigations.append("Increase contingency buffer and monitor budget closely")
            elif category == "revenue":
                mitigations.append("Develop conservative revenue scenarios and contingency plans")
            elif category == "timeline":
                mitigations.append("Extend timeline or accelerate revenue generation")
            elif category == "market":
                mitigations.append("Monitor market conditions and adjust projections accordingly")
            else:
                mitigations.append(f"Develop mitigation plan for {risk.get('risk', 'identified risk')}")
        
        return list(set(mitigations))  # Remove duplicates
    
    def _generate_risk_recommendations(
        self,
        risks: List[Dict[str, Any]],
        overall_risk_level: str
    ) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if overall_risk_level == "high":
            recommendations.append("URGENT: Address high-severity risks before proceeding")
            recommendations.append("Consider reducing project scope or increasing contingency")
        elif overall_risk_level == "medium":
            recommendations.append("Monitor and mitigate medium-severity risks")
            recommendations.append("Develop contingency plans for key risk areas")
        else:
            recommendations.append("Continue monitoring risks throughout project")
        
        high_severity_risks = [r for r in risks if r.get("severity") == "high"]
        if high_severity_risks:
            recommendations.append(f"Prioritize mitigation of {len(high_severity_risks)} high-severity risks")
        
        return recommendations
    
    def _generate_approval_feedback(
        self,
        approved: bool,
        score: float,
        issues: List[str]
    ) -> str:
        """Generate final approval feedback"""
        if approved:
            return (
                f"FINANCIAL PLAN APPROVED. Overall score: {score}/10. "
                "The financial plan meets approval criteria and is ready for execution."
            )
        else:
            return (
                f"FINANCIAL PLAN NOT APPROVED. Score: {score}/10. "
                f"Found {len(issues)} issues that must be addressed before approval. "
                "See conditions for required actions."
            )
    
    def _generate_approval_conditions(
        self,
        approved: bool,
        issues: List[str]
    ) -> List[str]:
        """Generate conditions for approval"""
        if approved:
            return []
        
        conditions = []
        for issue in issues:
            if "budget" in issue.lower():
                conditions.append("Revise budget to address identified issues")
            elif "risk" in issue.lower():
                conditions.append("Develop and implement risk mitigation strategies")
            elif "bcr" in issue.lower() or "benefit" in issue.lower():
                conditions.append("Improve benefit-cost ratio through cost optimization or benefit enhancement")
            elif "npv" in issue.lower():
                conditions.append("Improve financial projections to achieve positive NPV")
            else:
                conditions.append(f"Address: {issue}")
        
        return conditions
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - CFO workflow
        
        Expected input:
        {
            "action": "review_budget" | "calculate_roi" | "assess_risk" |
                      "cost_benefit_analysis" | "approve_financial_plan",
            "budget": {...},
            ...
        }
        """
        action = input_data.get("action", "review_budget")
        
        if action == "review_budget":
            return self.review_budget(
                input_data.get("budget", {}),
                input_data.get("project_requirements", {}),
                input_data.get("financial_constraints")
            )
        elif action == "calculate_roi":
            return self.calculate_roi(
                input_data.get("investment", 0),
                input_data.get("returns", {}),
                input_data.get("time_period")
            )
        elif action == "assess_risk":
            return self.assess_financial_risk(
                input_data.get("budget", {}),
                input_data.get("financial_model", {}),
                input_data.get("revenue_projections", {}),
                input_data.get("market_conditions")
            )
        elif action == "cost_benefit_analysis":
            return self.perform_cost_benefit_analysis(
                input_data.get("costs", {}),
                input_data.get("benefits", {}),
                input_data.get("time_horizon")
            )
        elif action == "approve_financial_plan":
            return self.approve_financial_plan(
                input_data.get("budget", {}),
                input_data.get("financial_model", {}),
                input_data.get("revenue_projections", {}),
                input_data.get("risk_assessment", {}),
                input_data.get("cost_benefit", {})
            )
        else:
            # Default: review budget
            return self.review_budget(
                input_data.get("budget", {}),
                input_data.get("project_requirements", {}),
                input_data.get("financial_constraints")
            )

