"""
Tests for Legal, Operations, and HR Department Agents
Tests COO Agent, Legal Director, Operations Director, and HR Director
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.coo_agent import COOAgent
from agents.departments.legal_director import LegalDirectorAgent
from agents.departments.operations_director import OperationsDirectorAgent
from agents.departments.hr_director import HRDirectorAgent


class TestCOOAgent(unittest.TestCase):
    """Test COO Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = COOAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "COO Agent")
        self.assertEqual(self.agent.role, "Operations oversight, process efficiency, and resource management")
        self.assertEqual(self.agent.task_type, "analysis")
        self.assertEqual(self.agent.approval_threshold, 7.0)
    
    def test_review_operations_plan_approved(self):
        """Test operations plan review - approved case"""
        operations_plan = {
            "processes": [
                {"name": "Process 1", "steps": 5}
            ],
            "workflows": [
                {"name": "Workflow 1", "complexity": "low", "steps": []}
            ],
            "resource_allocation": {
                "required": {"team_size": 5},
                "allocated": {"team_size": 5}
            },
            "timeline": {"duration_months": 12}
        }
        project_requirements = {"project_name": "Test"}
        
        review = self.agent.review_operations_plan(operations_plan, project_requirements)
        
        self.assertIn("approved", review)
        self.assertIn("score", review)
        self.assertIn("issues", review)
        self.assertIn("strengths", review)
        self.assertIn("recommendations", review)
    
    def test_review_operations_plan_not_approved(self):
        """Test operations plan review - not approved case"""
        operations_plan = {
            "processes": [],
            "workflows": [],
            "resource_allocation": {},
            "timeline": {"duration_months": 0}
        }
        project_requirements = {"project_name": "Test"}
        
        review = self.agent.review_operations_plan(operations_plan, project_requirements)
        
        self.assertFalse(review["approved"])
        self.assertGreater(len(review["issues"]), 0)
    
    def test_analyze_process_efficiency(self):
        """Test process efficiency analysis"""
        processes = [
            {"name": "Process 1", "automation_level": "high"},
            {"name": "Process 2", "automation_level": "low"}
        ]
        workflows = [
            {
                "name": "Workflow 1",
                "complexity": "low",
                "steps": [
                    {"can_parallelize": True},
                    {"can_parallelize": True}
                ]
            }
        ]
        
        analysis = self.agent.analyze_process_efficiency(processes, workflows)
        
        self.assertIn("total_processes", analysis)
        self.assertIn("total_workflows", analysis)
        self.assertIn("bottlenecks", analysis)
        self.assertIn("optimization_opportunities", analysis)
        self.assertIn("efficiency_score", analysis)
        self.assertEqual(analysis["total_processes"], 2)
        self.assertEqual(analysis["total_workflows"], 1)
    
    def test_validate_timeline_feasible(self):
        """Test timeline validation - feasible case"""
        timeline = {
            "duration_months": 12,
            "milestones": [
                {"name": "Milestone 1", "month": 3},
                {"name": "Milestone 2", "month": 6},
                {"name": "Milestone 3", "month": 12}
            ],
            "phases": [
                {"name": "Phase 1", "duration_weeks": 12}
            ]
        }
        project_scope = {"project_name": "Test"}
        
        validation = self.agent.validate_timeline(timeline, project_scope)
        
        self.assertIn("feasible", validation)
        self.assertIn("duration_months", validation)
        self.assertIn("issues", validation)
        self.assertIn("strengths", validation)
        self.assertIn("feasibility_score", validation)
    
    def test_validate_timeline_not_feasible(self):
        """Test timeline validation - not feasible case"""
        timeline = {
            "duration_months": 0,
            "milestones": [],
            "phases": []
        }
        project_scope = {"project_name": "Test"}
        
        validation = self.agent.validate_timeline(timeline, project_scope)
        
        self.assertFalse(validation["feasible"])
        self.assertGreater(len(validation["issues"]), 0)
    
    def test_assess_operational_feasibility(self):
        """Test operational feasibility assessment"""
        operations_plan = {
            "resource_allocation": {
                "required": {"team_size": 5, "budget": 100000}
            }
        }
        resource_availability = {
            "team_size": 5,
            "budget": 100000
        }
        timeline = {
            "duration_months": 12,
            "milestones": [{"name": "M1"}]
        }
        process_efficiency = {
            "efficiency_score": 8.0
        }
        
        feasibility = self.agent.assess_operational_feasibility(
            operations_plan, resource_availability, timeline, process_efficiency
        )
        
        self.assertIn("feasible", feasibility)
        self.assertIn("feasibility_score", feasibility)
        self.assertIn("factors", feasibility)
        self.assertIn("risks", feasibility)
        self.assertIn("recommendation", feasibility)
    
    def test_process_review_operations(self):
        """Test process method with review_operations action"""
        input_data = {
            "action": "review_operations",
            "operations_plan": {"processes": []},
            "project_requirements": {}
        }
        
        with patch.object(self.agent, 'review_operations_plan') as mock_review:
            mock_review.return_value = {"approved": True}
            
            result = self.agent.process(input_data)
            
            mock_review.assert_called_once()
            self.assertIn("approved", result)


class TestLegalDirectorAgent(unittest.TestCase):
    """Test Legal Director Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = LegalDirectorAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "Legal Director")
        self.assertEqual(self.agent.role, "Regulatory compliance, risk assessment, and legal requirements verification")
        self.assertEqual(self.agent.task_type, "analysis")
    
    def test_check_regulatory_compliance(self):
        """Test regulatory compliance check"""
        project_details = {
            "project_name": "Test Project",
            "industry": "Technology"
        }
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"compliant": true, "compliance_score": 8.0, "applicable_regulations": []}'
            
            compliance = self.agent.check_regulatory_compliance(project_details)
            
            self.assertIn("compliant", compliance)
            self.assertIn("compliance_score", compliance)
            self.assertIn("applicable_regulations", compliance)
            mock_llm.assert_called_once()
    
    def test_check_regulatory_compliance_fallback(self):
        """Test compliance check fallback"""
        project_details = {"project_name": "Test"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM call failed")
            
            compliance = self.agent.check_regulatory_compliance(project_details)
            
            self.assertIn("compliant", compliance)
            self.assertIn("compliance_score", compliance)
            self.assertIn("recommendations", compliance)
    
    def test_assess_legal_risk(self):
        """Test legal risk assessment"""
        project_scope = {
            "handles_personal_data": True,
            "uses_third_party_ip": False
        }
        compliance_status = {
            "compliance_gaps": ["GDPR compliance"],
            "applicable_regulations": [
                {"regulation": "GDPR", "status": "non_compliant"}
            ]
        }
        
        risk_assessment = self.agent.assess_legal_risk(project_scope, None, compliance_status)
        
        self.assertIn("overall_risk_level", risk_assessment)
        self.assertIn("risk_score", risk_assessment)
        self.assertIn("risks", risk_assessment)
        self.assertIn("risk_by_category", risk_assessment)
        self.assertIn("mitigation_strategies", risk_assessment)
        self.assertGreater(len(risk_assessment["risks"]), 0)
    
    def test_verify_legal_requirements(self):
        """Test legal requirements verification"""
        project_requirements = {
            "business_license": True,
            "insurance_coverage": True,
            "data_protection_policy": False
        }
        
        verification = self.agent.verify_legal_requirements(project_requirements)
        
        self.assertIn("verified", verification)
        self.assertIn("requirements_met", verification)
        self.assertIn("requirements_missing", verification)
        self.assertIn("requirements_pending", verification)
    
    def test_review_contract(self):
        """Test contract review"""
        contract_details = {
            "type": "vendor",
            "liability_limitation": True,
            "payment_terms": "Net 30"
        }
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"approved": true, "review_score": 8.0, "issues": [], "strengths": []}'
            
            review = self.agent.review_contract(contract_details, "vendor")
            
            self.assertIn("approved", review)
            self.assertIn("review_score", review)
            self.assertIn("issues", review)
            self.assertIn("strengths", review)
            mock_llm.assert_called_once()
    
    def test_analyze_liability(self):
        """Test liability analysis"""
        project_activities = {
            "handles_sensitive_data": True,
            "provides_advice": True,
            "physical_operations": False
        }
        insurance_coverage = {
            "general_liability": 2000000,
            "professional_liability": 1000000,
            "cyber_liability": 500000
        }
        
        liability = self.agent.analyze_liability(project_activities, insurance_coverage)
        
        self.assertIn("liability_areas", liability)
        self.assertIn("coverage_adequate", liability)
        self.assertIn("recommendations", liability)
        self.assertIn("overall_exposure", liability)
    
    def test_create_compliance_documentation(self):
        """Test compliance documentation creation"""
        compliance_requirements = {
            "required_documents": ["Privacy Policy", "Terms of Service"]
        }
        project_details = {
            "project_name": "Test",
            "industry": "Technology"
        }
        
        documentation = self.agent.create_compliance_documentation(
            compliance_requirements, project_details
        )
        
        self.assertIn("required_documents", documentation)
        self.assertIn("document_status", documentation)
        self.assertIn("completion_percentage", documentation)
    
    def test_process_check_compliance(self):
        """Test process method with check_compliance action"""
        input_data = {
            "action": "check_compliance",
            "project_details": {"project_name": "Test"}
        }
        
        with patch.object(self.agent, 'check_regulatory_compliance') as mock_check:
            mock_check.return_value = {"compliant": True}
            
            result = self.agent.process(input_data)
            
            mock_check.assert_called_once()
            self.assertIn("compliant", result)


class TestOperationsDirectorAgent(unittest.TestCase):
    """Test Operations Director Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = OperationsDirectorAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "Operations Director")
        self.assertEqual(self.agent.role, "Process optimization, workflow efficiency, and resource allocation")
        self.assertEqual(self.agent.task_type, "analysis")
    
    def test_optimize_processes(self):
        """Test process optimization"""
        current_processes = [
            {"name": "Process 1", "steps": 10},
            {"name": "Process 2", "steps": 8}
        ]
        project_requirements = {"project_name": "Test"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"optimized_processes": [], "overall_efficiency_improvement": "15%"}'
            
            optimization = self.agent.optimize_processes(current_processes, project_requirements)
            
            self.assertIn("optimized_processes", optimization)
            self.assertIn("overall_efficiency_improvement", optimization)
            self.assertIn("recommendations", optimization)
            mock_llm.assert_called_once()
    
    def test_optimize_processes_fallback(self):
        """Test process optimization fallback"""
        current_processes = [{"name": "Process 1"}]
        project_requirements = {"project_name": "Test"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM call failed")
            
            optimization = self.agent.optimize_processes(current_processes, project_requirements)
            
            self.assertIn("optimized_processes", optimization)
            self.assertIn("recommendations", optimization)
    
    def test_analyze_workflow_efficiency(self):
        """Test workflow efficiency analysis"""
        workflows = [
            {
                "name": "Workflow 1",
                "complexity": "low",
                "steps": [
                    {"can_parallelize": True},
                    {"can_parallelize": False}
                ]
            },
            {
                "name": "Workflow 2",
                "complexity": "high",
                "steps": [
                    {"can_parallelize": False},
                    {"can_parallelize": False},
                    {"can_parallelize": False},
                    {"can_parallelize": False},
                    {"can_parallelize": False},
                    {"can_parallelize": False}
                ]
            }
        ]
        
        analysis = self.agent.analyze_workflow_efficiency(workflows)
        
        self.assertIn("total_workflows", analysis)
        self.assertIn("workflow_analysis", analysis)
        self.assertIn("bottlenecks", analysis)
        self.assertIn("efficiency_score", analysis)
        self.assertIn("recommendations", analysis)
        self.assertEqual(analysis["total_workflows"], 2)
        self.assertGreater(len(analysis["bottlenecks"]), 0)
    
    def test_allocate_resources(self):
        """Test resource allocation"""
        project_requirements = {
            "team_size": 10,
            "budget": 200000,
            "equipment": ["Laptop", "Server"]
        }
        available_resources = {
            "team_size": 8,
            "budget": 200000,
            "equipment": ["Laptop"]
        }
        
        allocation = self.agent.allocate_resources(
            project_requirements, available_resources
        )
        
        self.assertIn("allocated", allocation)
        self.assertIn("required", allocation)
        self.assertIn("gaps", allocation)
        self.assertIn("utilization", allocation)
        self.assertIn("recommendations", allocation)
        self.assertIn("team_size", allocation["gaps"])
    
    def test_assess_timeline_feasibility(self):
        """Test timeline feasibility assessment"""
        timeline = {
            "duration_months": 12,
            "milestones": [
                {"name": "M1", "month": 3},
                {"name": "M2", "month": 6},
                {"name": "M3", "month": 12}
            ],
            "phases": [
                {"name": "Phase 1", "duration_weeks": 12}
            ]
        }
        project_scope = {"project_name": "Test"}
        resource_allocation = {
            "gaps": {}
        }
        
        feasibility = self.agent.assess_timeline_feasibility(
            timeline, project_scope, resource_allocation
        )
        
        self.assertIn("feasible", feasibility)
        self.assertIn("duration_months", feasibility)
        self.assertIn("issues", feasibility)
        self.assertIn("strengths", feasibility)
        self.assertIn("recommendation", feasibility)
    
    def test_assess_operational_capacity(self):
        """Test operational capacity assessment"""
        current_capacity = {
            "team_size": 10,
            "infrastructure_capacity": 100
        }
        project_demand = {
            "team_size": 8,
            "infrastructure_requirements": 80
        }
        
        assessment = self.agent.assess_operational_capacity(current_capacity, project_demand)
        
        self.assertIn("capacity_adequate", assessment)
        self.assertIn("utilization", assessment)
        self.assertIn("constraints", assessment)
        self.assertIn("recommendations", assessment)
        self.assertTrue(assessment["capacity_adequate"])
    
    def test_develop_risk_mitigation_strategies(self):
        """Test risk mitigation strategy development"""
        identified_risks = [
            {
                "risk": "Resource shortage",
                "severity": "high",
                "category": "resource"
            },
            {
                "risk": "Timeline delay",
                "severity": "medium",
                "category": "timeline"
            }
        ]
        operations_context = {"context": "test"}
        
        strategies = self.agent.develop_risk_mitigation_strategies(
            identified_risks, operations_context
        )
        
        self.assertIn("mitigation_plans", strategies)
        self.assertIn("priority_actions", strategies)
        self.assertIn("monitoring_requirements", strategies)
        self.assertEqual(len(strategies["mitigation_plans"]), 2)
    
    def test_process_optimize_processes(self):
        """Test process method with optimize_processes action"""
        input_data = {
            "action": "optimize_processes",
            "current_processes": [],
            "project_requirements": {}
        }
        
        with patch.object(self.agent, 'optimize_processes') as mock_optimize:
            mock_optimize.return_value = {"optimized_processes": []}
            
            result = self.agent.process(input_data)
            
            mock_optimize.assert_called_once()
            self.assertIn("optimized_processes", result)


class TestHRDirectorAgent(unittest.TestCase):
    """Test HR Director Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = HRDirectorAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "HR Director")
        self.assertEqual(self.agent.role, "Team presentation, credentials verification, and capacity planning")
        self.assertEqual(self.agent.task_type, "analysis")
    
    def test_present_team(self):
        """Test team presentation"""
        team_members = [
            {
                "name": "John Doe",
                "role": "Lead Developer",
                "credentials": ["BS Computer Science"],
                "experience_years": 5,
                "skills": ["Python", "JavaScript"]
            },
            {
                "name": "Jane Smith",
                "role": "Project Manager",
                "credentials": ["PMP"],
                "experience_years": 8,
                "skills": ["Project Management", "Agile"]
            }
        ]
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"team_presentation": {"total_members": 2}, "member_profiles": [], "team_alignment": {}}'
            
            presentation = self.agent.present_team(team_members)
            
            self.assertIn("team_presentation", presentation)
            self.assertIn("member_profiles", presentation)
            self.assertIn("team_alignment", presentation)
            mock_llm.assert_called_once()
    
    def test_present_team_fallback(self):
        """Test team presentation fallback"""
        team_members = [
            {"name": "John Doe", "role": "Developer", "credentials": [], "experience_years": 5, "skills": []}
        ]
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM call failed")
            
            presentation = self.agent.present_team(team_members)
            
            self.assertIn("team_presentation", presentation)
            self.assertIn("member_profiles", presentation)
            self.assertEqual(presentation["team_presentation"]["total_members"], 1)
    
    def test_verify_credentials(self):
        """Test credentials verification"""
        team_members = [
            {
                "name": "John Doe",
                "credentials": ["BS Computer Science", "AWS Certified"]
            },
            {
                "name": "Jane Smith",
                "credentials": ["PMP"]
            }
        ]
        required_credentials = ["PMP", "AWS Certified"]
        
        verification = self.agent.verify_credentials(team_members, required_credentials)
        
        self.assertIn("all_verified", verification)
        self.assertIn("verification_status", verification)
        self.assertIn("missing_credentials", verification)
        self.assertIn("recommendations", verification)
        self.assertIn("John Doe", verification["verification_status"])
        self.assertIn("Jane Smith", verification["verification_status"])
    
    def test_assess_organizational_capacity(self):
        """Test organizational capacity assessment"""
        current_organization = {
            "team_size": 10,
            "available_skills": ["Python", "JavaScript", "Project Management"],
            "average_experience_years": 5
        }
        project_demand = {
            "team_size": 8,
            "required_skills": ["Python", "JavaScript", "DevOps"],
            "required_experience_years": 4
        }
        
        assessment = self.agent.assess_organizational_capacity(
            current_organization, project_demand
        )
        
        self.assertIn("capacity_adequate", assessment)
        self.assertIn("current_capacity", assessment)
        self.assertIn("project_demand", assessment)
        self.assertIn("capacity_gaps", assessment)
        self.assertIn("utilization", assessment)
        self.assertIn("DevOps", assessment["capacity_gaps"].get("skills", []))
    
    def test_analyze_skills_gap(self):
        """Test skills gap analysis"""
        current_skills = ["Python", "JavaScript", "SQL"]
        required_skills = ["Python", "JavaScript", "DevOps", "Kubernetes"]
        
        gap_analysis = self.agent.analyze_skills_gap(current_skills, required_skills)
        
        self.assertIn("current_skills", gap_analysis)
        self.assertIn("required_skills", gap_analysis)
        self.assertIn("skills_gap", gap_analysis)
        self.assertIn("excess_skills", gap_analysis)
        self.assertIn("coverage_percentage", gap_analysis)
        self.assertIn("recommendations", gap_analysis)
        self.assertIn("DevOps", gap_analysis["skills_gap"])
        self.assertIn("Kubernetes", gap_analysis["skills_gap"])
    
    def test_optimize_team_structure(self):
        """Test team structure optimization"""
        current_structure = {
            "hierarchy": "flat",
            "teams": [
                {"team_name": "Development", "members": 5}
            ]
        }
        project_requirements = {"project_name": "Test"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"optimized_structure": {}, "improvements": [], "recommendations": []}'
            
            optimization = self.agent.optimize_team_structure(
                current_structure, project_requirements
            )
            
            self.assertIn("optimized_structure", optimization)
            self.assertIn("improvements", optimization)
            self.assertIn("recommendations", optimization)
            mock_llm.assert_called_once()
    
    def test_plan_capacity(self):
        """Test capacity planning"""
        project_roadmap = {
            "phases": [
                {"name": "Phase 1", "required_team_size": 5},
                {"name": "Phase 2", "required_team_size": 8},
                {"name": "Phase 3", "required_team_size": 6}
            ]
        }
        current_capacity = {
            "team_size": 5
        }
        
        capacity_plan = self.agent.plan_capacity(project_roadmap, current_capacity)
        
        self.assertIn("current_capacity", capacity_plan)
        self.assertIn("projected_needs", capacity_plan)
        self.assertIn("hiring_plan", capacity_plan)
        self.assertIn("timeline", capacity_plan)
        self.assertIn("recommendations", capacity_plan)
        self.assertEqual(capacity_plan["projected_needs"]["peak_team_size"], 8)
    
    def test_process_present_team(self):
        """Test process method with present_team action"""
        input_data = {
            "action": "present_team",
            "team_members": []
        }
        
        with patch.object(self.agent, 'present_team') as mock_present:
            mock_present.return_value = {"team_presentation": {}}
            
            result = self.agent.process(input_data)
            
            mock_present.assert_called_once()
            self.assertIn("team_presentation", result)


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agent collaboration"""
    
    def test_operations_director_to_coo_workflow(self):
        """Test Operations Director creates plan, COO reviews it"""
        operations_director = OperationsDirectorAgent()
        coo = COOAgent()
        
        # Operations Director creates operations plan
        workflows = [
            {"name": "Workflow 1", "complexity": "low", "steps": []}
        ]
        operations_plan = {
            "processes": [{"name": "Process 1"}],
            "workflows": workflows,
            "resource_allocation": {
                "required": {"team_size": 5},
                "allocated": {"team_size": 5}
            },
            "timeline": {"duration_months": 12}
        }
        
        # COO reviews operations plan
        review = coo.review_operations_plan(operations_plan, {})
        
        self.assertIn("approved", review)
        self.assertIn("score", review)
    
    def test_legal_director_compliance_workflow(self):
        """Test Legal Director complete compliance workflow"""
        legal_director = LegalDirectorAgent()
        
        project_details = {"project_name": "Test", "industry": "Technology"}
        
        # Check compliance
        compliance = legal_director.check_regulatory_compliance(project_details)
        
        # Assess legal risk
        project_scope = {"handles_personal_data": True}
        risk_assessment = legal_director.assess_legal_risk(project_scope, None, compliance)
        
        self.assertIn("compliant", compliance)
        self.assertIn("overall_risk_level", risk_assessment)
    
    def test_hr_director_team_workflow(self):
        """Test HR Director complete team workflow"""
        hr_director = HRDirectorAgent()
        
        team_members = [
            {"name": "John", "role": "Developer", "credentials": [], "experience_years": 5, "skills": ["Python"]}
        ]
        
        # Present team
        presentation = hr_director.present_team(team_members)
        
        # Verify credentials
        verification = hr_director.verify_credentials(team_members, ["PMP"])
        
        # Analyze skills gap
        gap_analysis = hr_director.analyze_skills_gap(
            ["Python"], ["Python", "DevOps"]
        )
        
        self.assertIn("team_presentation", presentation)
        self.assertIn("all_verified", verification)
        self.assertIn("skills_gap", gap_analysis)


if __name__ == '__main__':
    unittest.main()

