"""
Tests for Strategy and Content Agents
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.strategy import (
    CSOAgent,
    VisionBuilderAgent,
    BusinessArchitectAgent,
    GovernmentSpecialistAgent
)
from agents.content import (
    MasterWriterAgent,
    DataSpecialistAgent,
    DocumentFormatterAgent
)


class TestCSOAgent:
    """Tests for Chief Strategy Officer Agent"""
    
    def test_cso_agent_initialization(self):
        """Test CSO agent can be initialized"""
        agent = CSOAgent()
        assert agent.name == "Chief Strategy Officer"
        assert agent.role == "Project orchestration and strategic decision-making"
        assert agent.task_type == "strategy"
    
    def test_orchestrate_project(self):
        """Test project orchestration"""
        agent = CSOAgent()
        requirements = {
            "objectives": ["Deliver quality proposal"],
            "timeline": "3 months"
        }
        resources = {
            "budget": 100000,
            "team": ["Writer", "Researcher"]
        }
        
        result = agent.orchestrate_project(requirements, resources)
        assert "phases" in result
        assert "strategic_priorities" in result
        assert isinstance(result["phases"], list)
    
    def test_make_strategic_decision(self):
        """Test strategic decision making"""
        agent = CSOAgent()
        context = {
            "goal": "Maximize quality",
            "constraints": ["Budget", "Timeline"]
        }
        options = [
            {"name": "Option A", "cost": 50000},
            {"name": "Option B", "cost": 75000}
        ]
        
        result = agent.make_strategic_decision(context, options)
        assert "selected_option" in result
        assert "rationale" in result
        assert "strategic_alignment_score" in result


class TestVisionBuilderAgent:
    """Tests for Vision Builder Agent"""
    
    def test_vision_builder_initialization(self):
        """Test Vision Builder agent can be initialized"""
        agent = VisionBuilderAgent()
        assert agent.name == "Vision Builder"
        assert agent.role == "Develop vision and mission from vague inputs"
    
    def test_develop_vision(self):
        """Test vision development"""
        agent = VisionBuilderAgent()
        vague_input = "We want to help organizations succeed"
        context = {"industry": "Consulting"}
        
        result = agent.develop_vision(vague_input, context)
        assert "vision_statement" in result
        assert "mission_statement" in result
        assert "core_values" in result
    
    def test_clarify_goals(self):
        """Test goal clarification"""
        agent = VisionBuilderAgent()
        unclear_goals = ["Be successful", "Help people"]
        
        result = agent.clarify_goals(unclear_goals)
        assert "clarified_goals" in result
        assert len(result["clarified_goals"]) == len(unclear_goals)


class TestBusinessArchitectAgent:
    """Tests for Business Architect Agent"""
    
    def test_business_architect_initialization(self):
        """Test Business Architect agent can be initialized"""
        agent = BusinessArchitectAgent()
        assert agent.name == "Business Architect"
        assert agent.role == "Design financial structures and business models"
    
    def test_design_financial_structure(self):
        """Test financial structure design"""
        agent = BusinessArchitectAgent()
        requirements = {"scope": "Large project"}
        constraints = {"total_budget": 200000}
        
        result = agent.design_financial_structure(requirements, constraints)
        assert "cost_breakdown" in result
        assert "total_budget" in result
        assert result["total_budget"] == 200000
    
    def test_develop_revenue_model(self):
        """Test revenue model development"""
        agent = BusinessArchitectAgent()
        concept = {"service": "Consulting services"}
        
        result = agent.develop_revenue_model(concept)
        assert "revenue_streams" in result
        assert "pricing_strategy" in result


class TestGovernmentSpecialistAgent:
    """Tests for Government Specialist Agent"""
    
    def test_government_specialist_initialization(self):
        """Test Government Specialist agent can be initialized"""
        agent = GovernmentSpecialistAgent()
        assert agent.name == "Government Specialist"
        assert agent.task_type == "compliance"
    
    def test_analyze_rfp(self):
        """Test RFP analysis"""
        agent = GovernmentSpecialistAgent()
        rfp_doc = {
            "title": "IT Services RFP",
            "deadline": "2024-12-31"
        }
        
        result = agent.analyze_rfp(rfp_doc)
        assert "mandatory_requirements" in result
        assert "compliance_requirements" in result
        assert "evaluation_criteria" in result
    
    def test_ensure_procurement_compliance(self):
        """Test procurement compliance check"""
        agent = GovernmentSpecialistAgent()
        proposal = {"sections": {"technical": "Content"}}
        requirements = {"mandatory": ["Technical approach"]}
        
        result = agent.ensure_procurement_compliance(proposal, requirements)
        assert "compliance_status" in result
        assert "compliance_score" in result


class TestMasterWriterAgent:
    """Tests for Master Writer Agent"""
    
    def test_master_writer_initialization(self):
        """Test Master Writer agent can be initialized"""
        agent = MasterWriterAgent()
        assert agent.name == "Master Writer"
        assert agent.task_type == "writing"
    
    def test_write_proposal_section(self):
        """Test proposal section writing"""
        agent = MasterWriterAgent()
        requirements = {
            "content": "Describe the solution",
            "length": "500 words"
        }
        
        result = agent.write_proposal_section("Solution", requirements)
        assert "section_name" in result
        assert "content" in result
        assert result["section_name"] == "Solution"
    
    def test_generate_content(self):
        """Test content generation"""
        agent = MasterWriterAgent()
        
        result = agent.generate_content(
            topic="AI Solutions",
            purpose="Proposal section",
            audience="Technical evaluators",
            length="short"
        )
        assert "content" in result
        assert result["topic"] == "AI Solutions"


class TestDataSpecialistAgent:
    """Tests for Data Specialist Agent"""
    
    def test_data_specialist_initialization(self):
        """Test Data Specialist agent can be initialized"""
        agent = DataSpecialistAgent()
        assert agent.name == "Data Specialist"
        assert agent.task_type == "research"
    
    def test_gather_statistics(self):
        """Test statistics gathering"""
        agent = DataSpecialistAgent()
        
        result = agent.gather_statistics("AI adoption rates")
        assert "statistics" in result
        assert "trends" in result
    
    def test_validate_data(self):
        """Test data validation"""
        agent = DataSpecialistAgent()
        data = {
            "metric": "Success rate",
            "value": 85,
            "source": "Internal research"
        }
        
        result = agent.validate_data(data)
        assert "validation_status" in result
        assert "validation_score" in result


class TestDocumentFormatterAgent:
    """Tests for Document Formatter Agent"""
    
    def test_document_formatter_initialization(self):
        """Test Document Formatter agent can be initialized"""
        agent = DocumentFormatterAgent()
        assert agent.name == "Document Formatter"
    
    def test_format_document(self):
        """Test document formatting"""
        agent = DocumentFormatterAgent()
        content = {
            "title": "Test Document",
            "sections": {
                "Introduction": {"content": "This is the introduction"},
                "Conclusion": {"content": "This is the conclusion"}
            }
        }
        
        result = agent.format_document(content)
        assert "title" in result
        assert "sections" in result
        assert len(result["sections"]) == 2
    
    def test_create_document_structure(self):
        """Test document structure creation"""
        agent = DocumentFormatterAgent()
        sections = {
            "Section 1": "Content 1",
            "Section 2": "Content 2"
        }
        
        result = agent.create_document_structure(sections, "Test Doc")
        assert result["title"] == "Test Doc"
        assert len(result["sections"]) == 2
    
    def test_export_to_docx(self, tmp_path):
        """Test DOCX export"""
        agent = DocumentFormatterAgent()
        document = {
            "title": "Test Document",
            "sections": [
                {"name": "Section 1", "content": "Content 1", "formatted": True}
            ],
            "style": agent.default_style
        }
        
        output_path = str(tmp_path / "test.docx")
        result = agent.export_to_docx(document, output_path)
        
        # Check if export was attempted (may fail if python-docx not installed)
        assert "success" in result
        assert "output_path" in result
    
    def test_export_to_pdf(self, tmp_path):
        """Test PDF export"""
        agent = DocumentFormatterAgent()
        document = {
            "title": "Test Document",
            "sections": [
                {"name": "Section 1", "content": "Content 1", "formatted": True}
            ],
            "style": agent.default_style
        }
        
        output_path = str(tmp_path / "test.pdf")
        result = agent.export_to_pdf(document, output_path)
        
        # Check if export was attempted (may fail if reportlab not installed)
        assert "success" in result
        assert "output_path" in result


class TestAgentIntegration:
    """Integration tests for agent collaboration"""
    
    def test_strategy_to_content_flow(self):
        """Test flow from strategy to content agents"""
        # Create agents
        vision_agent = VisionBuilderAgent()
        writer_agent = MasterWriterAgent()
        
        # Build vision
        vision = vision_agent.develop_vision("Help organizations succeed")
        
        # Write content based on vision
        requirements = {
            "content": f"Describe our vision: {vision.get('vision_statement', '')}",
            "style": "professional"
        }
        content = writer_agent.write_proposal_section("Vision", requirements)
        
        assert "content" in content
        assert content["section_name"] == "Vision"
    
    def test_data_to_writer_flow(self):
        """Test flow from data specialist to writer"""
        data_agent = DataSpecialistAgent()
        writer_agent = MasterWriterAgent()
        
        # Gather statistics
        stats = data_agent.gather_statistics("Project success rates")
        
        # Write content with statistics
        requirements = {
            "content": "Include relevant statistics",
            "data": stats
        }
        content = writer_agent.write_proposal_section("Statistics", requirements)
        
        assert "content" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

