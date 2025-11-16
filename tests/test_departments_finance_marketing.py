"""
Tests for Finance and Marketing Department Agents
Tests CFO Agent, Finance Director, and Marketing Director
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.cfo_agent import CFOAgent
from agents.departments.finance_director import FinanceDirectorAgent
from agents.departments.marketing_director import MarketingDirectorAgent


class TestFinanceDirectorAgent(unittest.TestCase):
    """Test Finance Director Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = FinanceDirectorAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "Finance Director")
        self.assertEqual(self.agent.role, "Budget creation, financial modeling, and cost analysis")
        self.assertEqual(self.agent.task_type, "analysis")
    
    def test_create_budget_basic(self):
        """Test basic budget creation"""
        project_requirements = {
            "project_name": "Test Project",
            "duration_months": 12,
            "team_size": 5
        }
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"total_budget": 100000, "categories": []}'
            
            budget = self.agent.create_budget(project_requirements)
            
            self.assertIn("total_budget", budget)
            self.assertIn("categories", budget)
            mock_llm.assert_called_once()
    
    def test_create_budget_fallback(self):
        """Test budget creation fallback"""
        project_requirements = {
            "project_name": "Test Project"
        }
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM call failed")
            
            budget = self.agent.create_budget(project_requirements)
            
            self.assertIn("total_budget", budget)
            self.assertIn("categories", budget)
            self.assertGreater(budget["total_budget"], 0)
    
    def test_develop_financial_model(self):
        """Test financial model development"""
        budget = {
            "total_budget": 120000,
            "categories": []
        }
        timeline = {"duration_months": 12}
        
        model = self.agent.develop_financial_model(budget, None, timeline)
        
        self.assertIn("total_budget", model)
        self.assertIn("monthly_burn_rate", model)
        self.assertIn("cash_flow_projection", model)
        self.assertIn("key_metrics", model)
        self.assertEqual(model["timeline_months"], 12)
        self.assertEqual(model["monthly_burn_rate"], 10000)
    
    def test_analyze_costs(self):
        """Test cost analysis"""
        budget = {
            "total_budget": 100000,
            "categories": [
                {"category": "Personnel", "amount": 60000, "justification": "Salaries"},
                {"category": "Equipment", "amount": 20000, "justification": "Hardware"},
                {"category": "Travel", "amount": 20000, "justification": "Travel costs"}
            ]
        }
        
        analysis = self.agent.analyze_costs(budget)
        
        self.assertIn("total_budget", analysis)
        self.assertIn("category_breakdown", analysis)
        self.assertIn("high_cost_areas", analysis)
        self.assertEqual(len(analysis["category_breakdown"]), 3)
    
    def test_calculate_break_even(self):
        """Test break-even calculation"""
        budget = {"total_budget": 120000}
        revenue_projections = {
            "scenarios": {
                "realistic": {"monthly_revenue": 15000}
            }
        }
        timeline = {"duration_months": 12}
        
        break_even = self.agent.calculate_break_even(budget, revenue_projections, timeline)
        
        self.assertIn("break_even_month", break_even)
        self.assertIn("break_even_achievable", break_even)
        self.assertIn("monthly_costs", break_even)
        self.assertIn("monthly_revenue", break_even)
    
    def test_calculate_break_even_not_achievable(self):
        """Test break-even when not achievable"""
        budget = {"total_budget": 120000}
        revenue_projections = {
            "scenarios": {
                "realistic": {"monthly_revenue": 5000}
            }
        }
        timeline = {"duration_months": 12}
        
        break_even = self.agent.calculate_break_even(budget, revenue_projections, timeline)
        
        self.assertFalse(break_even["break_even_achievable"])
    
    def test_assess_financial_feasibility(self):
        """Test financial feasibility assessment"""
        budget = {"total_budget": 100000}
        revenue_projections = {
            "scenarios": {
                "realistic": {"annual_revenue": 150000}
            }
        }
        break_even = {
            "break_even_achievable": True,
            "break_even_month": 8
        }
        
        feasibility = self.agent.assess_financial_feasibility(
            budget, revenue_projections, break_even, 100000
        )
        
        self.assertIn("feasible", feasibility)
        self.assertIn("feasibility_score", feasibility)
        self.assertIn("recommendation", feasibility)
        self.assertIn("risks", feasibility)
    
    def test_process_create_budget(self):
        """Test process method with create_budget action"""
        input_data = {
            "action": "create_budget",
            "project_requirements": {"project_name": "Test"}
        }
        
        with patch.object(self.agent, 'create_budget') as mock_create:
            mock_create.return_value = {"total_budget": 100000}
            
            result = self.agent.process(input_data)
            
            mock_create.assert_called_once()
            self.assertIn("total_budget", result)


class TestMarketingDirectorAgent(unittest.TestCase):
    """Test Marketing Director Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = MarketingDirectorAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "Marketing Director")
        self.assertEqual(self.agent.role, "Brand positioning, messaging, and competitive strategy")
        self.assertEqual(self.agent.task_type, "strategy")
    
    def test_develop_brand_positioning(self):
        """Test brand positioning development"""
        project_scope = {
            "project_name": "Test Project",
            "description": "A test project"
        }
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"positioning_statement": "Test statement", "key_differentiators": []}'
            
            positioning = self.agent.develop_brand_positioning(project_scope)
            
            self.assertIn("positioning_statement", positioning)
            mock_llm.assert_called_once()
    
    def test_develop_brand_positioning_fallback(self):
        """Test brand positioning fallback"""
        project_scope = {"project_name": "Test"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM call failed")
            
            positioning = self.agent.develop_brand_positioning(project_scope)
            
            self.assertIn("positioning_statement", positioning)
            self.assertIn("key_differentiators", positioning)
    
    def test_develop_messaging(self):
        """Test messaging development"""
        brand_positioning = {
            "positioning_statement": "Test positioning",
            "unique_value_proposition": "Test value"
        }
        project_scope = {"project_name": "Test"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"core_message": "Test message", "supporting_messages": []}'
            
            messaging = self.agent.develop_messaging(brand_positioning, project_scope)
            
            self.assertIn("core_message", messaging)
            mock_llm.assert_called_once()
    
    def test_analyze_differentiation(self):
        """Test differentiation analysis"""
        project_scope = {"project_name": "Test"}
        competitive_landscape = {
            "competitors": [
                {"name": "Competitor 1", "strengths": ["Price"]}
            ]
        }
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"competitive_advantages": [], "unique_differentiators": []}'
            
            analysis = self.agent.analyze_differentiation(
                project_scope, competitive_landscape
            )
            
            self.assertIn("competitive_advantages", analysis)
            self.assertIn("unique_differentiators", analysis)
            mock_llm.assert_called_once()
    
    def test_develop_value_proposition(self):
        """Test value proposition development"""
        project_scope = {"project_name": "Test"}
        target_audience = {"segment": "Businesses"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"value_proposition_statement": "Test", "key_benefits": []}'
            
            value_prop = self.agent.develop_value_proposition(
                project_scope, target_audience
            )
            
            self.assertIn("value_proposition_statement", value_prop)
            mock_llm.assert_called_once()
    
    def test_analyze_target_audience(self):
        """Test target audience analysis"""
        project_scope = {"project_name": "Test"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"primary_segments": [], "personas": []}'
            
            analysis = self.agent.analyze_target_audience(project_scope)
            
            self.assertIn("primary_segments", analysis)
            self.assertIn("personas", analysis)
            mock_llm.assert_called_once()
    
    def test_develop_competitive_positioning(self):
        """Test competitive positioning development"""
        brand_positioning = {
            "positioning_statement": "Test positioning"
        }
        differentiation_analysis = {
            "unique_differentiators": ["Quality", "Innovation"],
            "competitive_advantages": [
                {"advantage": "Expertise"}
            ],
            "competitive_gaps": []
        }
        competitive_landscape = {}
        
        positioning = self.agent.develop_competitive_positioning(
            brand_positioning, differentiation_analysis, competitive_landscape
        )
        
        self.assertIn("positioning_statement", positioning)
        self.assertIn("key_differentiators", positioning)
        self.assertIn("competitive_strategy", positioning)
    
    def test_process_develop_brand_positioning(self):
        """Test process method with develop_brand_positioning action"""
        input_data = {
            "action": "develop_brand_positioning",
            "project_scope": {"project_name": "Test"}
        }
        
        with patch.object(self.agent, 'develop_brand_positioning') as mock_develop:
            mock_develop.return_value = {"positioning_statement": "Test"}
            
            result = self.agent.process(input_data)
            
            mock_develop.assert_called_once()
            self.assertIn("positioning_statement", result)


class TestCFOAgent(unittest.TestCase):
    """Test CFO Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = CFOAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "CFO Agent")
        self.assertEqual(self.agent.role, "Financial oversight, budget approval, and risk assessment")
        self.assertEqual(self.agent.task_type, "analysis")
        self.assertEqual(self.agent.approval_threshold, 7.0)
    
    def test_review_budget_approved(self):
        """Test budget review - approved case"""
        budget = {
            "total_budget": 100000,
            "categories": [
                {"category": "Personnel", "amount": 50000},
                {"category": "Equipment", "amount": 30000},
                {"category": "Contingency", "amount": 20000}
            ],
            "contingency_percentage": 20,
            "contingency_amount": 20000
        }
        project_requirements = {"project_name": "Test"}
        financial_constraints = {"max_budget": 150000}
        
        review = self.agent.review_budget(budget, project_requirements, financial_constraints)
        
        self.assertIn("approved", review)
        self.assertIn("score", review)
        self.assertIn("issues", review)
        self.assertIn("strengths", review)
        self.assertIn("recommendations", review)
    
    def test_review_budget_not_approved(self):
        """Test budget review - not approved case"""
        budget = {
            "total_budget": 200000,
            "categories": [],
            "contingency_percentage": 2,
            "contingency_amount": 4000
        }
        project_requirements = {"project_name": "Test"}
        financial_constraints = {"max_budget": 150000}
        
        review = self.agent.review_budget(budget, project_requirements, financial_constraints)
        
        self.assertFalse(review["approved"])
        self.assertGreater(len(review["issues"]), 0)
    
    def test_calculate_roi_single(self):
        """Test ROI calculation - single return value"""
        investment = 100000
        returns = 150000
        
        roi = self.agent.calculate_roi(investment, returns)
        
        self.assertIn("investment", roi)
        self.assertIn("roi_percentage", roi)
        self.assertIn("net_return", roi)
        self.assertEqual(roi["investment"], investment)
        self.assertEqual(roi["roi_percentage"], 50.0)
        self.assertEqual(roi["net_return"], 50000)
    
    def test_calculate_roi_scenarios(self):
        """Test ROI calculation - multiple scenarios"""
        investment = 100000
        returns = {
            "conservative": {"total_return": 120000},
            "realistic": {"total_return": 150000},
            "optimistic": {"total_return": 200000}
        }
        
        roi = self.agent.calculate_roi(investment, returns)
        
        self.assertIn("investment", roi)
        self.assertIn("scenarios", roi)
        self.assertIn("roi_percentage", roi)
        self.assertIn(roi["scenarios"], "realistic")
    
    def test_assess_financial_risk(self):
        """Test financial risk assessment"""
        budget = {
            "total_budget": 100000,
            "contingency_percentage": 10,
            "contingency_amount": 10000
        }
        financial_model = {
            "key_metrics": {"break_even_month": 8},
            "timeline_months": 12
        }
        revenue_projections = {
            "scenarios": {
                "conservative": {"annual_revenue": 120000},
                "realistic": {"annual_revenue": 150000}
            }
        }
        
        risk_assessment = self.agent.assess_financial_risk(
            budget, financial_model, revenue_projections
        )
        
        self.assertIn("overall_risk_level", risk_assessment)
        self.assertIn("risk_score", risk_assessment)
        self.assertIn("risks", risk_assessment)
        self.assertIn("mitigation_strategies", risk_assessment)
    
    def test_perform_cost_benefit_analysis(self):
        """Test cost-benefit analysis"""
        costs = {
            "total_budget": 100000,
            "ongoing_monthly_cost": 5000
        }
        benefits = {
            "total_revenue": 150000,
            "monthly_revenue": 12500
        }
        
        cba = self.agent.perform_cost_benefit_analysis(costs, benefits, 12)
        
        self.assertIn("total_costs", cba)
        self.assertIn("total_benefits", cba)
        self.assertIn("benefit_cost_ratio", cba)
        self.assertIn("npv", cba)
        self.assertIn("recommendation", cba)
        self.assertGreater(cba["benefit_cost_ratio"], 1.0)
    
    def test_approve_financial_plan(self):
        """Test financial plan approval"""
        budget = {"approved": True, "issues": []}
        financial_model = {"timeline_months": 12}
        revenue_projections = {"scenarios": {"realistic": {"annual_revenue": 150000}}}
        risk_assessment = {"overall_risk_level": "low"}
        cost_benefit = {"benefit_cost_ratio": 1.5, "npv": 50000}
        
        approval = self.agent.approve_financial_plan(
            budget, financial_model, revenue_projections, risk_assessment, cost_benefit
        )
        
        self.assertIn("approved", approval)
        self.assertIn("approval_score", approval)
        self.assertIn("feedback", approval)
        self.assertTrue(approval["approved"])
    
    def test_approve_financial_plan_not_approved(self):
        """Test financial plan approval - not approved"""
        budget = {"approved": False, "issues": ["Budget too high"]}
        financial_model = {"timeline_months": 12}
        revenue_projections = {"scenarios": {"realistic": {"annual_revenue": 50000}}}
        risk_assessment = {"overall_risk_level": "high"}
        cost_benefit = {"benefit_cost_ratio": 0.5, "npv": -50000}
        
        approval = self.agent.approve_financial_plan(
            budget, financial_model, revenue_projections, risk_assessment, cost_benefit
        )
        
        self.assertFalse(approval["approved"])
        self.assertGreater(len(approval["issues"]), 0)
        self.assertIn("conditions", approval)
    
    def test_process_review_budget(self):
        """Test process method with review_budget action"""
        input_data = {
            "action": "review_budget",
            "budget": {"total_budget": 100000},
            "project_requirements": {}
        }
        
        with patch.object(self.agent, 'review_budget') as mock_review:
            mock_review.return_value = {"approved": True}
            
            result = self.agent.process(input_data)
            
            mock_review.assert_called_once()
            self.assertIn("approved", result)


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agent collaboration"""
    
    def test_finance_director_to_cfo_workflow(self):
        """Test Finance Director creates budget, CFO reviews it"""
        finance_director = FinanceDirectorAgent()
        cfo = CFOAgent()
        
        # Finance Director creates budget
        project_requirements = {"project_name": "Test", "duration_months": 12}
        budget = finance_director.create_budget(project_requirements)
        
        # CFO reviews budget
        review = cfo.review_budget(budget, project_requirements)
        
        self.assertIn("approved", review)
        self.assertIn("total_budget", review)
    
    def test_marketing_director_workflow(self):
        """Test Marketing Director complete workflow"""
        marketing_director = MarketingDirectorAgent()
        
        project_scope = {"project_name": "Test Project"}
        
        # Develop positioning
        positioning = marketing_director.develop_brand_positioning(project_scope)
        
        # Develop messaging based on positioning
        messaging = marketing_director.develop_messaging(positioning, project_scope)
        
        self.assertIn("positioning_statement", positioning)
        self.assertIn("core_message", messaging)


if __name__ == '__main__':
    unittest.main()

