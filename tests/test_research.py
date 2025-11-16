"""
Tests for Research Agents (Funder Intelligence and Success Analyzer)
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from agents.research.funder_intelligence import FunderIntelligenceAgent
from agents.research.success_analyzer import SuccessAnalyzerAgent


class TestFunderIntelligenceAgent:
    """Tests for Funder Intelligence Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return FunderIntelligenceAgent()
    
    @pytest.fixture
    def sample_funder_data(self):
        """Sample funder data"""
        return {
            "name": "Test Foundation",
            "website": "https://testfoundation.org",
            "focus_areas": ["education", "research"],
            "requirements": {
                "application_format": "Online",
                "required_documents": ["proposal", "budget"]
            }
        }
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "Funder Intelligence Agent"
        assert agent.role == "Research funding organizations and extract requirements"
        assert agent.task_type == "research"
    
    def test_load_funder_database(self, agent):
        """Test loading funder database"""
        # Database should be loaded (even if empty)
        assert hasattr(agent, 'funder_database')
        assert isinstance(agent.funder_database, dict)
    
    @patch('agents.research.funder_intelligence.web_scraper')
    @patch('agents.research.funder_intelligence.FunderIntelligenceAgent._extract_structured_info')
    def test_research_funder_with_website(
        self,
        mock_extract,
        mock_scraper,
        agent,
        sample_funder_data
    ):
        """Test researching funder with provided website"""
        # Mock web scraper
        mock_scraper.scrape.return_value = {
            "url": "https://testfoundation.org",
            "title": "Test Foundation",
            "text": "Sample website content",
            "status_code": 200
        }
        
        # Mock structured info extraction
        mock_extract.return_value = {
            "focus_areas": ["education"],
            "mission": "Test mission"
        }
        
        result = agent.research_funder(
            funder_name="Test Foundation",
            website="https://testfoundation.org",
            deep_research=True
        )
        
        assert result["name"] == "Test Foundation"
        assert result["website"] == "https://testfoundation.org"
        assert "focus_areas" in result or "mission" in result
    
    def test_research_funder_cached(self, agent):
        """Test using cached funder data"""
        # Add to cache
        agent.funder_database["test foundation"] = {
            "name": "Test Foundation",
            "website": "https://testfoundation.org"
        }
        
        result = agent.research_funder(
            funder_name="Test Foundation",
            deep_research=False
        )
        
        assert result["name"] == "Test Foundation"
        assert result["research_method"] == "cached"
    
    def test_get_funder_info(self, agent):
        """Test getting cached funder info"""
        agent.funder_database["test foundation"] = {
            "name": "Test Foundation",
            "website": "https://testfoundation.org"
        }
        
        info = agent.get_funder_info("Test Foundation")
        assert info is not None
        assert info["name"] == "Test Foundation"
    
    def test_list_known_funders(self, agent):
        """Test listing known funders"""
        agent.funder_database = {
            "foundation 1": {"name": "Foundation 1"},
            "foundation 2": {"name": "Foundation 2"}
        }
        
        funders = agent.list_known_funders()
        assert len(funders) == 2
        assert "Foundation 1" in funders
        assert "Foundation 2" in funders
    
    def test_process_method(self, agent):
        """Test process method"""
        with patch.object(agent, 'research_funder') as mock_research:
            mock_research.return_value = {
                "name": "Test Foundation",
                "website": "https://testfoundation.org"
            }
            
            result = agent.process({
                "funder_name": "Test Foundation",
                "deep_research": False
            })
            
            assert result["status"] == "success"
            assert "funder_info" in result
            mock_research.assert_called_once()
    
    def test_process_method_missing_funder_name(self, agent):
        """Test process method raises error when funder_name is missing"""
        with pytest.raises(ValueError, match="funder_name is required"):
            agent.process({})


class TestSuccessAnalyzerAgent:
    """Tests for Success Analyzer Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return SuccessAnalyzerAgent()
    
    @pytest.fixture
    def sample_proposal(self):
        """Sample winning proposal content"""
        return """
        Executive Summary:
        This proposal outlines an innovative approach to solving critical challenges
        in education through technology integration.
        
        Problem Statement:
        Current educational systems face significant barriers to accessibility.
        
        Solution:
        Our solution leverages AI to personalize learning experiences.
        
        Impact:
        This project will reach 10,000 students and improve learning outcomes by 30%.
        """
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "Success Analyzer Agent"
        assert agent.role == "Analyze winning proposals and extract success patterns"
        assert agent.task_type == "research"
    
    def test_load_patterns(self, agent):
        """Test loading patterns"""
        assert hasattr(agent, 'patterns')
        assert isinstance(agent.patterns, dict)
        assert "patterns" in agent.patterns
        assert "common_elements" in agent.patterns
    
    @patch('agents.research.success_analyzer.SuccessAnalyzerAgent._analyze_with_llm')
    @patch('agents.research.success_analyzer.SuccessAnalyzerAgent._extract_patterns')
    def test_analyze_winning_proposal(
        self,
        mock_extract,
        mock_analyze,
        agent,
        sample_proposal
    ):
        """Test analyzing a winning proposal"""
        mock_analyze.return_value = {
            "winning_factors": ["clear impact", "innovative solution"],
            "key_elements": ["executive summary", "data"]
        }
        
        mock_extract.return_value = {
            "winning_factors": ["clear impact"],
            "common_elements": ["executive summary"]
        }
        
        result = agent.analyze_winning_proposal(
            proposal_content=sample_proposal,
            funder_name="Test Foundation"
        )
        
        assert "analysis" in result
        assert "patterns" in result
        assert result["funder"] == "Test Foundation"
    
    def test_get_success_patterns(self, agent):
        """Test getting success patterns"""
        patterns = agent.get_success_patterns()
        assert isinstance(patterns, dict)
        assert "patterns" in patterns
        assert "common_elements" in patterns
    
    def test_get_recommendations(self, agent):
        """Test getting recommendations"""
        # Set up some patterns
        agent.patterns = {
            "winning_strategies": [
                {"strategy": "Clear impact metrics", "frequency": 10},
                {"strategy": "Strong team", "frequency": 8}
            ],
            "common_elements": [
                {"element": "Executive summary", "frequency": 15},
                {"element": "Budget", "frequency": 12}
            ]
        }
        
        recommendations = agent.get_recommendations()
        assert len(recommendations) > 0
        assert any("Clear impact metrics" in rec for rec in recommendations)
    
    def test_process_analyze_proposal(self, agent, sample_proposal):
        """Test process method for analyzing proposal"""
        with patch.object(agent, 'analyze_winning_proposal') as mock_analyze:
            mock_analyze.return_value = {"analysis": "test"}
            
            result = agent.process({
                "proposal_content": sample_proposal,
                "funder_name": "Test Foundation"
            })
            
            assert result["status"] == "success"
            assert "result" in result
    
    def test_process_research_winners(self, agent):
        """Test process method for researching winners"""
        with patch.object(agent, 'research_public_winners') as mock_research:
            mock_research.return_value = {"sources": []}
            
            result = agent.process({
                "funder_name": "Test Foundation"
            })
            
            assert result["status"] == "success"
            assert "result" in result
    
    def test_process_get_patterns(self, agent):
        """Test process method for getting patterns"""
        result = agent.process({
            "get_patterns": True
        })
        
        assert result["status"] == "success"
        assert "patterns" in result
        assert "recommendations" in result
    
    def test_process_invalid_input(self, agent):
        """Test process method with invalid input"""
        with pytest.raises(ValueError, match="Invalid input"):
            agent.process({})


class TestIntegration:
    """Integration tests for research agents"""
    
    def test_funder_database_exists(self):
        """Test that funder database file exists and is valid JSON"""
        db_path = Path("data/funder_database.json")
        if db_path.exists():
            with open(db_path, 'r') as f:
                data = json.load(f)
                assert "funders" in data
                assert isinstance(data["funders"], list)
    
    def test_success_patterns_directory_exists(self):
        """Test that success patterns directory exists"""
        patterns_dir = Path("data/success_patterns")
        assert patterns_dir.exists()
        assert patterns_dir.is_dir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

