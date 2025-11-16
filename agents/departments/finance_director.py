"""
Finance Director Agent
Handles budget creation, financial models, cost analysis, revenue projections,
break-even analysis, and financial feasibility assessment.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)


class FinanceDirectorAgent(BaseAgent):
    """
    Finance Director Agent - Budget and financial analysis specialist.
    Creates budgets, develops financial models, performs cost analysis,
    projects revenue, calculates break-even points, and assesses feasibility.
    """
    
    def __init__(self):
        super().__init__(
            name="Finance Director",
            role="Budget creation, financial modeling, and cost analysis",
            task_type="analysis"
        )
    
    def create_budget(
        self,
        project_requirements: Dict[str, Any],
        cost_estimates: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive budget for proposal
        
        Args:
            project_requirements: Project requirements and scope
            cost_estimates: Optional initial cost estimates
            
        Returns:
            Detailed budget breakdown with categories, amounts, and justifications
        """
        self.log_action("Creating project budget")
        
        prompt = f"""As a Finance Director, create a comprehensive budget for this project proposal.

Project Requirements:
{json.dumps(project_requirements, indent=2)}

Cost Estimates (if provided):
{json.dumps(cost_estimates or {}, indent=2)}

Create a detailed budget with:
1. Personnel costs (salaries, benefits, time allocation)
2. Equipment and materials
3. Travel and accommodation
4. Overhead and indirect costs
5. Contingency (typically 10-15%)
6. Total budget

For each line item, provide:
- Category name
- Amount
- Justification/explanation
- Time period (if applicable)

Return JSON format:
{{
    "total_budget": <number>,
    "categories": [
        {{
            "category": "<name>",
            "amount": <number>,
            "justification": "<explanation>",
            "period": "<time period>"
        }}
    ],
    "contingency_percentage": <number>,
    "contingency_amount": <number>,
    "budget_breakdown": {{
        "personnel": <number>,
        "equipment": <number>,
        "travel": <number>,
        "overhead": <number>,
        "other": <number>
    }},
    "assumptions": ["<assumption 1>", "<assumption 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                budget = json.loads(json_match.group())
                # Validate and calculate totals
                budget = self._validate_budget(budget)
                self.log_action("Budget created", {"total": budget.get("total_budget", 0)})
                return budget
        except Exception as e:
            logger.warning(f"Budget creation LLM call failed: {e}")
        
        # Fallback: create basic budget structure
        return self._create_fallback_budget(project_requirements, cost_estimates)
    
    def develop_financial_model(
        self,
        budget: Dict[str, Any],
        revenue_projections: Optional[Dict[str, Any]] = None,
        timeline: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Develop financial model with projections
        
        Args:
            budget: Project budget
            revenue_projections: Optional revenue projections
            timeline: Project timeline
            
        Returns:
            Financial model with cash flow, projections, and key metrics
        """
        self.log_action("Developing financial model")
        
        total_budget = budget.get("total_budget", 0)
        timeline_months = timeline.get("duration_months", 12) if timeline else 12
        
        # Calculate monthly burn rate
        monthly_burn = total_budget / timeline_months if timeline_months > 0 else total_budget
        
        # Create cash flow projection
        cash_flow = []
        cumulative = 0
        for month in range(timeline_months):
            monthly_cost = monthly_burn
            if revenue_projections:
                monthly_revenue = revenue_projections.get("monthly_revenue", 0)
            else:
                monthly_revenue = 0
            
            net_cash_flow = monthly_revenue - monthly_cost
            cumulative += net_cash_flow
            
            cash_flow.append({
                "month": month + 1,
                "revenue": monthly_revenue,
                "costs": monthly_cost,
                "net_cash_flow": net_cash_flow,
                "cumulative": cumulative
            })
        
        # Calculate key financial metrics
        total_revenue = sum(entry["revenue"] for entry in cash_flow)
        total_costs = sum(entry["costs"] for entry in cash_flow)
        net_profit = total_revenue - total_costs
        roi = ((total_revenue - total_costs) / total_costs * 100) if total_costs > 0 else 0
        
        financial_model = {
            "total_budget": total_budget,
            "timeline_months": timeline_months,
            "monthly_burn_rate": monthly_burn,
            "cash_flow_projection": cash_flow,
            "key_metrics": {
                "total_revenue": total_revenue,
                "total_costs": total_costs,
                "net_profit": net_profit,
                "roi_percentage": roi,
                "break_even_month": self._calculate_break_even_month(cash_flow)
            },
            "assumptions": [
                f"Monthly burn rate: ${monthly_burn:,.2f}",
                f"Project duration: {timeline_months} months"
            ]
        }
        
        if revenue_projections:
            financial_model["assumptions"].append(
                f"Monthly revenue: ${revenue_projections.get('monthly_revenue', 0):,.2f}"
            )
        
        return financial_model
    
    def analyze_costs(
        self,
        budget: Dict[str, Any],
        benchmark_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform detailed cost analysis
        
        Args:
            budget: Project budget
            benchmark_data: Optional industry benchmarks
            
        Returns:
            Cost analysis with breakdown, comparisons, and optimization suggestions
        """
        self.log_action("Analyzing costs")
        
        categories = budget.get("categories", [])
        total = budget.get("total_budget", 0)
        
        # Calculate category percentages
        category_analysis = []
        for category in categories:
            amount = category.get("amount", 0)
            percentage = (amount / total * 100) if total > 0 else 0
            category_analysis.append({
                "category": category.get("category", "Unknown"),
                "amount": amount,
                "percentage": round(percentage, 2),
                "justification": category.get("justification", "")
            })
        
        # Sort by amount (descending)
        category_analysis.sort(key=lambda x: x["amount"], reverse=True)
        
        # Identify high-cost areas
        high_cost_areas = [
            cat for cat in category_analysis 
            if cat["percentage"] > 20  # More than 20% of total
        ]
        
        # Cost optimization suggestions
        optimization_suggestions = []
        if high_cost_areas:
            for area in high_cost_areas:
                optimization_suggestions.append(
                    f"Review {area['category']} costs ({area['percentage']:.1f}% of total) "
                    f"for potential optimization opportunities"
                )
        
        analysis = {
            "total_budget": total,
            "category_breakdown": category_analysis,
            "high_cost_areas": high_cost_areas,
            "cost_distribution": {
                "largest_category": category_analysis[0]["category"] if category_analysis else None,
                "largest_percentage": category_analysis[0]["percentage"] if category_analysis else 0,
                "number_of_categories": len(category_analysis)
            },
            "optimization_suggestions": optimization_suggestions,
            "benchmark_comparison": benchmark_data if benchmark_data else None
        }
        
        return analysis
    
    def project_revenue(
        self,
        project_scope: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Project revenue for the project
        
        Args:
            project_scope: Project scope and deliverables
            market_data: Optional market research data
            
        Returns:
            Revenue projections with assumptions and scenarios
        """
        self.log_action("Projecting revenue")
        
        prompt = f"""As a Finance Director, create revenue projections for this project.

Project Scope:
{json.dumps(project_scope, indent=2)}

Market Data (if available):
{json.dumps(market_data or {}, indent=2)}

Create revenue projections including:
1. Revenue streams (e.g., product sales, services, subscriptions)
2. Monthly/quarterly revenue estimates
3. Growth assumptions
4. Conservative, realistic, and optimistic scenarios
5. Key assumptions and risks

Return JSON format:
{{
    "revenue_streams": [
        {{
            "stream": "<name>",
            "description": "<description>",
            "monthly_revenue": <number>
        }}
    ],
    "total_monthly_revenue": <number>,
    "scenarios": {{
        "conservative": {{
            "monthly_revenue": <number>,
            "annual_revenue": <number>,
            "assumptions": ["<assumption>"]
        }},
        "realistic": {{
            "monthly_revenue": <number>,
            "annual_revenue": <number>,
            "assumptions": ["<assumption>"]
        }},
        "optimistic": {{
            "monthly_revenue": <number>,
            "annual_revenue": <number>,
            "assumptions": ["<assumption>"]
        }}
    }},
    "key_assumptions": ["<assumption 1>", "<assumption 2>"],
    "risks": ["<risk 1>", "<risk 2>"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=2500
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                projections = json.loads(json_match.group())
                return projections
        except Exception as e:
            logger.warning(f"Revenue projection LLM call failed: {e}")
        
        # Fallback: basic revenue projection
        return {
            "revenue_streams": [],
            "total_monthly_revenue": 0,
            "scenarios": {
                "conservative": {"monthly_revenue": 0, "annual_revenue": 0, "assumptions": []},
                "realistic": {"monthly_revenue": 0, "annual_revenue": 0, "assumptions": []},
                "optimistic": {"monthly_revenue": 0, "annual_revenue": 0, "assumptions": []}
            },
            "key_assumptions": ["Revenue projections require market validation"],
            "risks": ["Market demand uncertainty"]
        }
    
    def calculate_break_even(
        self,
        budget: Dict[str, Any],
        revenue_projections: Dict[str, Any],
        timeline: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate break-even point
        
        Args:
            budget: Project budget
            revenue_projections: Revenue projections
            timeline: Project timeline
            
        Returns:
            Break-even analysis with point in time and key metrics
        """
        self.log_action("Calculating break-even point")
        
        total_costs = budget.get("total_budget", 0)
        timeline_months = timeline.get("duration_months", 12) if timeline else 12
        monthly_costs = total_costs / timeline_months if timeline_months > 0 else total_costs
        
        # Get monthly revenue (use realistic scenario if available)
        scenarios = revenue_projections.get("scenarios", {})
        realistic = scenarios.get("realistic", {})
        monthly_revenue = realistic.get("monthly_revenue", 0)
        
        if monthly_revenue <= 0:
            return {
                "break_even_month": None,
                "break_even_achievable": False,
                "total_costs": total_costs,
                "monthly_costs": monthly_costs,
                "monthly_revenue": monthly_revenue,
                "monthly_contribution": monthly_revenue - monthly_costs,
                "message": "Break-even not achievable with current revenue projections"
            }
        
        # Calculate break-even month
        if monthly_revenue >= monthly_costs:
            # Positive contribution margin
            months_to_break_even = total_costs / (monthly_revenue - monthly_costs)
            break_even_month = int(np.ceil(months_to_break_even))
            
            if break_even_month > timeline_months:
                return {
                    "break_even_month": break_even_month,
                    "break_even_achievable": False,
                    "total_costs": total_costs,
                    "monthly_costs": monthly_costs,
                    "monthly_revenue": monthly_revenue,
                    "monthly_contribution": monthly_revenue - monthly_costs,
                    "message": f"Break-even requires {break_even_month} months, but project duration is {timeline_months} months"
                }
            
            return {
                "break_even_month": break_even_month,
                "break_even_achievable": True,
                "total_costs": total_costs,
                "monthly_costs": monthly_costs,
                "monthly_revenue": monthly_revenue,
                "monthly_contribution": monthly_revenue - monthly_costs,
                "contribution_margin_percentage": ((monthly_revenue - monthly_costs) / monthly_revenue * 100) if monthly_revenue > 0 else 0,
                "message": f"Break-even achieved in month {break_even_month}"
            }
        else:
            return {
                "break_even_month": None,
                "break_even_achievable": False,
                "total_costs": total_costs,
                "monthly_costs": monthly_costs,
                "monthly_revenue": monthly_revenue,
                "monthly_contribution": monthly_revenue - monthly_costs,
                "message": "Monthly revenue is less than monthly costs - break-even not achievable"
            }
    
    def assess_financial_feasibility(
        self,
        budget: Dict[str, Any],
        revenue_projections: Dict[str, Any],
        break_even: Dict[str, Any],
        funding_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Assess overall financial feasibility of the project
        
        Args:
            budget: Project budget
            revenue_projections: Revenue projections
            break_even: Break-even analysis
            funding_amount: Available funding amount (if applicable)
            
        Returns:
            Feasibility assessment with recommendation and risk factors
        """
        self.log_action("Assessing financial feasibility")
        
        total_budget = budget.get("total_budget", 0)
        is_break_even_achievable = break_even.get("break_even_achievable", False)
        
        # Check funding adequacy
        funding_adequate = True
        funding_gap = 0
        if funding_amount is not None:
            funding_gap = total_budget - funding_amount
            funding_adequate = funding_amount >= total_budget
        
        # Assess feasibility factors
        feasibility_factors = []
        risks = []
        
        if funding_adequate:
            feasibility_factors.append("Funding is adequate for project budget")
        else:
            risks.append(f"Funding gap of ${funding_gap:,.2f} - need additional ${funding_gap:,.2f}")
            feasibility_factors.append(f"Funding shortfall: ${funding_gap:,.2f}")
        
        if is_break_even_achievable:
            feasibility_factors.append(f"Break-even achievable in month {break_even.get('break_even_month')}")
        else:
            risks.append("Break-even not achievable within project timeline")
            feasibility_factors.append("Break-even timeline exceeds project duration")
        
        # Calculate ROI
        scenarios = revenue_projections.get("scenarios", {})
        realistic = scenarios.get("realistic", {})
        annual_revenue = realistic.get("annual_revenue", 0)
        roi = ((annual_revenue - total_budget) / total_budget * 100) if total_budget > 0 else 0
        
        if roi > 0:
            feasibility_factors.append(f"Positive ROI: {roi:.1f}%")
        else:
            risks.append(f"Negative ROI: {roi:.1f}%")
        
        # Overall feasibility score (0-10)
        score = 5.0  # Start at neutral
        if funding_adequate:
            score += 2.0
        if is_break_even_achievable:
            score += 2.0
        if roi > 0:
            score += 1.0
        
        score = min(10.0, max(0.0, score))
        
        # Recommendation
        if score >= 7.0 and len(risks) == 0:
            recommendation = "FEASIBLE - Project is financially viable"
        elif score >= 5.0:
            recommendation = "CONDITIONALLY FEASIBLE - Proceed with risk mitigation"
        else:
            recommendation = "NOT FEASIBLE - Significant financial risks identified"
        
        return {
            "feasible": score >= 5.0,
            "feasibility_score": round(score, 2),
            "recommendation": recommendation,
            "funding_adequate": funding_adequate,
            "funding_gap": funding_gap,
            "break_even_achievable": is_break_even_achievable,
            "roi_percentage": round(roi, 2),
            "feasibility_factors": feasibility_factors,
            "risks": risks,
            "mitigation_suggestions": self._generate_mitigation_suggestions(risks)
        }
    
    def _validate_budget(self, budget: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and recalculate budget totals"""
        categories = budget.get("categories", [])
        calculated_total = sum(cat.get("amount", 0) for cat in categories)
        
        # Update total if it doesn't match
        if abs(calculated_total - budget.get("total_budget", 0)) > 0.01:
            budget["total_budget"] = calculated_total
        
        # Ensure contingency is calculated
        if "contingency_percentage" in budget and "contingency_amount" not in budget:
            budget["contingency_amount"] = calculated_total * (budget["contingency_percentage"] / 100)
        
        return budget
    
    def _create_fallback_budget(
        self,
        project_requirements: Dict[str, Any],
        cost_estimates: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create basic budget structure as fallback"""
        base_amount = cost_estimates.get("estimated_cost", 100000) if cost_estimates else 100000
        
        return {
            "total_budget": base_amount,
            "categories": [
                {
                    "category": "Personnel",
                    "amount": base_amount * 0.5,
                    "justification": "Team salaries and benefits",
                    "period": "Project duration"
                },
                {
                    "category": "Equipment & Materials",
                    "amount": base_amount * 0.2,
                    "justification": "Required equipment and materials",
                    "period": "One-time"
                },
                {
                    "category": "Travel",
                    "amount": base_amount * 0.1,
                    "justification": "Travel and accommodation",
                    "period": "As needed"
                },
                {
                    "category": "Overhead",
                    "amount": base_amount * 0.15,
                    "justification": "Indirect costs and overhead",
                    "period": "Project duration"
                },
                {
                    "category": "Contingency",
                    "amount": base_amount * 0.05,
                    "justification": "Risk buffer",
                    "period": "Project duration"
                }
            ],
            "contingency_percentage": 5.0,
            "contingency_amount": base_amount * 0.05,
            "budget_breakdown": {
                "personnel": base_amount * 0.5,
                "equipment": base_amount * 0.2,
                "travel": base_amount * 0.1,
                "overhead": base_amount * 0.15,
                "other": base_amount * 0.05
            },
            "assumptions": ["Budget estimates based on standard industry rates"]
        }
    
    def _calculate_break_even_month(self, cash_flow: List[Dict[str, Any]]) -> Optional[int]:
        """Calculate break-even month from cash flow"""
        cumulative = 0
        for entry in cash_flow:
            cumulative += entry.get("net_cash_flow", 0)
            if cumulative >= 0:
                return entry.get("month")
        return None
    
    def _generate_mitigation_suggestions(self, risks: List[str]) -> List[str]:
        """Generate risk mitigation suggestions"""
        suggestions = []
        for risk in risks:
            if "funding gap" in risk.lower():
                suggestions.append("Seek additional funding sources or reduce project scope")
            elif "break-even" in risk.lower():
                suggestions.append("Increase revenue projections or extend project timeline")
            elif "roi" in risk.lower():
                suggestions.append("Review cost structure and revenue model for optimization")
            else:
                suggestions.append(f"Develop mitigation plan for: {risk}")
        return suggestions
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input - Finance Director workflow
        
        Expected input:
        {
            "action": "create_budget" | "analyze_costs" | "project_revenue" | 
                      "calculate_break_even" | "assess_feasibility" | "develop_model",
            "project_requirements": {...},
            "budget": {...},
            "revenue_projections": {...},
            ...
        }
        """
        action = input_data.get("action", "create_budget")
        
        if action == "create_budget":
            return self.create_budget(
                input_data.get("project_requirements", {}),
                input_data.get("cost_estimates")
            )
        elif action == "analyze_costs":
            return self.analyze_costs(
                input_data.get("budget", {}),
                input_data.get("benchmark_data")
            )
        elif action == "project_revenue":
            return self.project_revenue(
                input_data.get("project_scope", {}),
                input_data.get("market_data")
            )
        elif action == "calculate_break_even":
            return self.calculate_break_even(
                input_data.get("budget", {}),
                input_data.get("revenue_projections", {}),
                input_data.get("timeline")
            )
        elif action == "assess_feasibility":
            return self.assess_financial_feasibility(
                input_data.get("budget", {}),
                input_data.get("revenue_projections", {}),
                input_data.get("break_even", {}),
                input_data.get("funding_amount")
            )
        elif action == "develop_model":
            return self.develop_financial_model(
                input_data.get("budget", {}),
                input_data.get("revenue_projections"),
                input_data.get("timeline")
            )
        else:
            # Default: create budget
            return self.create_budget(
                input_data.get("project_requirements", {}),
                input_data.get("cost_estimates")
            )

