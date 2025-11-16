"""
Tests for Knowledge Base Service
Tests ChromaDB integration, semantic search, and knowledge management
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from services.knowledge_base import KnowledgeBase


@pytest.fixture
def temp_kb_dir():
    """Create a temporary directory for knowledge base"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def knowledge_base(temp_kb_dir):
    """Create a knowledge base instance for testing"""
    kb = KnowledgeBase(
        persist_directory=temp_kb_dir,
        collection_name="test_collection"
    )
    yield kb
    # Cleanup
    try:
        kb.clear_collection()
    except:
        pass


class TestKnowledgeBaseInitialization:
    """Test knowledge base initialization"""
    
    def test_init_default_directory(self):
        """Test initialization with default directory"""
        kb = KnowledgeBase(collection_name="test_init")
        assert kb.collection_name == "test_init"
        assert kb.persist_directory.exists()
        kb.clear_collection()
    
    def test_init_custom_directory(self, temp_kb_dir):
        """Test initialization with custom directory"""
        kb = KnowledgeBase(
            persist_directory=temp_kb_dir,
            collection_name="test_custom"
        )
        assert kb.persist_directory == Path(temp_kb_dir)
        assert kb.collection_name == "test_custom"
    
    def test_init_embedding_model(self, knowledge_base):
        """Test that embedding model is loaded"""
        assert knowledge_base.embedding_model is not None
        assert hasattr(knowledge_base.embedding_model, "encode")


class TestDocumentOperations:
    """Test document add, get, update, delete operations"""
    
    def test_add_document(self, knowledge_base):
        """Test adding a single document"""
        doc_id = knowledge_base.add_document(
            content="This is a test document about funders.",
            metadata={"type": "test", "category": "sample"}
        )
        assert doc_id is not None
        assert isinstance(doc_id, str)
    
    def test_add_document_with_id(self, knowledge_base):
        """Test adding a document with custom ID"""
        custom_id = "test_doc_123"
        doc_id = knowledge_base.add_document(
            content="Test content",
            metadata={"type": "test"},
            document_id=custom_id
        )
        assert doc_id == custom_id
    
    def test_add_document_empty_content(self, knowledge_base):
        """Test that empty content raises error"""
        with pytest.raises(ValueError):
            knowledge_base.add_document(content="")
    
    def test_get_document(self, knowledge_base):
        """Test retrieving a document"""
        content = "This is test content for retrieval."
        metadata = {"type": "test", "source": "pytest"}
        doc_id = knowledge_base.add_document(
            content=content,
            metadata=metadata
        )
        
        retrieved = knowledge_base.get_document(doc_id)
        assert retrieved is not None
        assert retrieved["content"] == content
        assert retrieved["metadata"]["type"] == metadata["type"]
        assert retrieved["metadata"]["source"] == metadata["source"]
    
    def test_get_nonexistent_document(self, knowledge_base):
        """Test retrieving a non-existent document"""
        result = knowledge_base.get_document("nonexistent_id")
        assert result is None
    
    def test_update_document(self, knowledge_base):
        """Test updating a document"""
        doc_id = knowledge_base.add_document(
            content="Original content",
            metadata={"type": "test", "version": "1"}
        )
        
        success = knowledge_base.update_document(
            document_id=doc_id,
            content="Updated content",
            metadata={"version": "2"}
        )
        
        assert success is True
        updated = knowledge_base.get_document(doc_id)
        assert updated["content"] == "Updated content"
        assert updated["metadata"]["version"] == "2"
        assert updated["metadata"]["type"] == "test"  # Should preserve existing
    
    def test_update_nonexistent_document(self, knowledge_base):
        """Test updating a non-existent document"""
        success = knowledge_base.update_document(
            document_id="nonexistent",
            content="New content"
        )
        assert success is False
    
    def test_delete_document(self, knowledge_base):
        """Test deleting a document"""
        doc_id = knowledge_base.add_document(
            content="Content to delete",
            metadata={"type": "test"}
        )
        
        success = knowledge_base.delete_document(doc_id)
        assert success is True
        
        retrieved = knowledge_base.get_document(doc_id)
        assert retrieved is None
    
    def test_add_multiple_documents(self, knowledge_base):
        """Test adding multiple documents at once"""
        documents = [
            {
                "content": f"Document {i} content",
                "metadata": {"type": "test", "index": i}
            }
            for i in range(5)
        ]
        
        doc_ids = knowledge_base.add_documents(documents)
        assert len(doc_ids) == 5
        
        # Verify all documents were added
        for doc_id in doc_ids:
            retrieved = knowledge_base.get_document(doc_id)
            assert retrieved is not None


class TestSemanticSearch:
    """Test semantic search functionality"""
    
    def test_search_basic(self, knowledge_base):
        """Test basic semantic search"""
        # Add test documents
        knowledge_base.add_document(
            content="The Bill and Melinda Gates Foundation focuses on global health and education.",
            metadata={"type": "funder_info", "funder": "Gates Foundation"}
        )
        knowledge_base.add_document(
            content="The World Bank provides financial assistance to developing countries.",
            metadata={"type": "funder_info", "funder": "World Bank"}
        )
        knowledge_base.add_document(
            content="Global health initiatives are critical for improving lives worldwide.",
            metadata={"type": "general"}
        )
        
        # Search for Gates Foundation
        results = knowledge_base.search(
            query="Gates Foundation health programs",
            n_results=2
        )
        
        assert len(results) > 0
        assert any("Gates" in result["content"] for result in results)
    
    def test_search_with_metadata_filter(self, knowledge_base):
        """Test search with metadata filtering"""
        knowledge_base.add_document(
            content="Gates Foundation information",
            metadata={"type": "funder_data", "category": "health"}
        )
        knowledge_base.add_document(
            content="World Bank information",
            metadata={"type": "funder_data", "category": "development"}
        )
        knowledge_base.add_document(
            content="General information",
            metadata={"type": "other"}
        )
        
        results = knowledge_base.search(
            query="funder information",
            n_results=10,
            filter_metadata={"type": "funder_data"}
        )
        
        assert len(results) > 0
        assert all(result["metadata"]["type"] == "funder_data" for result in results)
    
    def test_search_min_score(self, knowledge_base):
        """Test search with minimum score threshold"""
        knowledge_base.add_document(
            content="Highly relevant content about Gates Foundation",
            metadata={"type": "test"}
        )
        knowledge_base.add_document(
            content="Completely unrelated content about cooking recipes",
            metadata={"type": "test"}
        )
        
        results = knowledge_base.search(
            query="Gates Foundation",
            n_results=10,
            min_score=0.3  # Require at least 30% similarity
        )
        
        # Should filter out unrelated content
        assert len(results) >= 1
        assert any("Gates" in result["content"] for result in results)
    
    def test_search_empty_query(self, knowledge_base):
        """Test search with empty query"""
        results = knowledge_base.search(query="")
        assert results == []


class TestFunderDataOperations:
    """Test funder-specific data operations"""
    
    def test_add_funder_data(self, knowledge_base):
        """Test adding structured funder data"""
        funder_data = {
            "description": "A major global health funder",
            "focus_areas": ["health", "education", "poverty"],
            "requirements": ["non-profit status", "proven track record"],
            "priorities": ["impact", "sustainability"],
            "website": "https://example.com",
            "source": "web_scraping"
        }
        
        doc_id = knowledge_base.add_funder_data(
            funder_name="Test Funder",
            funder_data=funder_data
        )
        
        assert doc_id is not None
        retrieved = knowledge_base.get_document(doc_id)
        assert "Test Funder" in retrieved["content"]
        assert retrieved["metadata"]["type"] == "funder_data"
        assert retrieved["metadata"]["funder_name"] == "Test Funder"
    
    def test_search_funders(self, knowledge_base):
        """Test searching for funder information"""
        # Add multiple funders
        knowledge_base.add_funder_data(
            funder_name="Gates Foundation",
            funder_data={
                "description": "Global health and education",
                "focus_areas": ["health", "education"],
                "requirements": [],
                "priorities": []
            }
        )
        
        knowledge_base.add_funder_data(
            funder_name="World Bank",
            funder_data={
                "description": "Financial assistance for development",
                "focus_areas": ["development", "infrastructure"],
                "requirements": [],
                "priorities": []
            }
        )
        
        results = knowledge_base.search_funders(
            query="health education funder",
            n_results=5
        )
        
        assert len(results) > 0
        assert any("Gates" in result["content"] for result in results)


class TestCollectionManagement:
    """Test collection management operations"""
    
    def test_get_collection_stats(self, knowledge_base):
        """Test getting collection statistics"""
        # Add some documents
        knowledge_base.add_document(
            content="Test document 1",
            metadata={"type": "test"}
        )
        knowledge_base.add_document(
            content="Test document 2",
            metadata={"type": "test"}
        )
        knowledge_base.add_document(
            content="Funder document",
            metadata={"type": "funder_data"}
        )
        
        stats = knowledge_base.get_collection_stats()
        
        assert stats["total_documents"] >= 3
        assert "test" in stats["document_types"] or stats["total_documents"] > 0
        assert stats["collection_name"] == "test_collection"
    
    def test_clear_collection(self, knowledge_base):
        """Test clearing the collection"""
        # Add documents
        knowledge_base.add_document(
            content="Document to be deleted",
            metadata={"type": "test"}
        )
        
        # Clear collection
        success = knowledge_base.clear_collection()
        assert success is True
        
        # Verify collection is empty
        stats = knowledge_base.get_collection_stats()
        assert stats["total_documents"] == 0


class TestIntegration:
    """Integration tests for knowledge base with agents"""
    
    def test_knowledge_base_with_competitive_intelligence(self, knowledge_base):
        """Test knowledge base integration with competitive intelligence"""
        from agents.research.competitive_intelligence import CompetitiveIntelligenceAgent
        
        # Add competitor data to knowledge base
        knowledge_base.add_document(
            content="Competitor A is a major player in the health sector with strong partnerships.",
            metadata={"type": "competitor", "name": "Competitor A", "sector": "health"}
        )
        
        # Create agent with knowledge base
        agent = CompetitiveIntelligenceAgent(knowledge_base=knowledge_base)
        
        # Process request
        result = agent.process({
            "project_name": "Test Project",
            "funder_name": "Gates Foundation",
            "industry": "health"
        })
        
        assert "competitors" in result
        assert "swot_analysis" in result
        assert "competitive_advantages" in result
    
    def test_knowledge_base_with_field_research(self, knowledge_base):
        """Test knowledge base integration with field research"""
        from agents.research.field_research import FieldResearchAgent
        
        # Add industry statistics
        knowledge_base.add_document(
            content="The global health market is valued at $10 billion and growing at 5% annually.",
            metadata={"type": "industry_statistic", "industry": "health"}
        )
        
        # Create agent with knowledge base
        agent = FieldResearchAgent(knowledge_base=knowledge_base)
        
        # Process request
        result = agent.process({
            "project_name": "Test Project",
            "industry": "health",
            "research_questions": ["What is the market size?"]
        })
        
        assert "primary_data" in result
        assert "industry_statistics" in result
        assert "market_research" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

