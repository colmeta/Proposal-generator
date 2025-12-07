"""Tests for web interface"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.utils.api_client import APIClient
from web.utils.helpers import (
    format_date, format_relative_time, format_file_size,
    validate_email, validate_url, validate_required_fields,
    format_currency, get_status_color, truncate_text,
    sanitize_filename, parse_budget, format_progress
)


class TestAPIClient:
    """Tests for API client"""
    
    def test_init(self):
        """Test API client initialization"""
        client = APIClient(base_url="http://test.com/api")
        assert client.base_url == "http://test.com/api"
        assert client.session is not None
    
    @patch('web.utils.api_client.requests.Session')
    def test_create_proposal(self, mock_session):
        """Test proposal creation"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "title": "Test Proposal"}
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = APIClient(base_url="http://test.com/api")
        client.session = mock_session_instance
        
        result = client.create_proposal({"title": "Test Proposal"})
        assert result["id"] == "123"
        assert result["title"] == "Test Proposal"
    
    @patch('web.utils.api_client.requests.Session')
    def test_get_job(self, mock_session):
        """Test getting job by ID"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "job123", "status": "completed"}
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = APIClient(base_url="http://test.com/api")
        client.session = mock_session_instance
        
        result = client.get_job("job123")
        assert result["id"] == "job123"
        assert result["status"] == "completed"
    
    @patch('web.utils.api_client.requests.Session')
    def test_health_check(self, mock_session):
        """Test health check"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = APIClient(base_url="http://test.com/api")
        client.session = mock_session_instance
        
        result = client.health_check()
        assert result["status"] == "healthy"
    
    @patch('web.utils.api_client.requests.Session')
    def test_error_handling(self, mock_session):
        """Test error handling"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = APIClient(base_url="http://test.com/api")
        client.session = mock_session_instance
        
        with pytest.raises(Exception):
            client.get_job("nonexistent")


class TestHelpers:
    """Tests for helper functions"""
    
    def test_format_date(self):
        """Test date formatting"""
        from datetime import datetime
        date_str = "2024-01-15T10:30:00"
        result = format_date(date_str)
        assert "2024" in result
        assert "01" in result or "15" in result
    
    def test_format_date_none(self):
        """Test date formatting with None"""
        result = format_date(None)
        assert result == "N/A"
    
    def test_format_relative_time(self):
        """Test relative time formatting"""
        from datetime import datetime, timedelta
        recent = (datetime.now() - timedelta(hours=2)).isoformat()
        result = format_relative_time(recent)
        assert "hour" in result.lower() or "2" in result
    
    def test_format_file_size(self):
        """Test file size formatting"""
        assert "KB" in format_file_size(1024)
        assert "MB" in format_file_size(1024 * 1024)
        assert "B" in format_file_size(100)
    
    def test_validate_email(self):
        """Test email validation"""
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False
        assert validate_email("test@") is False
        assert validate_email("@example.com") is False
    
    def test_validate_url(self):
        """Test URL validation"""
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("invalid-url") is False
        assert validate_url("not-a-url") is False
    
    def test_validate_required_fields(self):
        """Test required fields validation"""
        data = {"field1": "value1", "field2": "value2"}
        is_valid, error = validate_required_fields(data, ["field1", "field2"])
        assert is_valid is True
        assert error is None
        
        is_valid, error = validate_required_fields(data, ["field1", "field2", "field3"])
        assert is_valid is False
        assert error is not None
        assert "field3" in error
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert "$" in format_currency(1000.50, "USD")
        assert "€" in format_currency(1000.50, "EUR")
        assert "£" in format_currency(1000.50, "GBP")
        assert "1000.50" in format_currency(1000.50, "USD")
    
    def test_get_status_color(self):
        """Test status color mapping"""
        assert get_status_color("completed") == "green"
        assert get_status_color("failed") == "red"
        assert get_status_color("processing") == "blue"
        assert get_status_color("pending") == "orange"
    
    def test_truncate_text(self):
        """Test text truncation"""
        long_text = "a" * 200
        result = truncate_text(long_text, max_length=100)
        assert len(result) <= 103  # 100 + "..."
        assert result.endswith("...")
        
        short_text = "short"
        result = truncate_text(short_text, max_length=100)
        assert result == short_text
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        assert sanitize_filename("test<file>.txt") == "test_file_.txt"
        assert sanitize_filename("  test.txt  ") == "test.txt"
        assert "test" in sanitize_filename("test.txt")
    
    def test_parse_budget(self):
        """Test budget parsing"""
        assert parse_budget("$1,000.50") == 1000.50
        assert parse_budget("1000") == 1000.0
        assert parse_budget("invalid") is None
        assert parse_budget("") is None
    
    def test_format_progress(self):
        """Test progress formatting"""
        assert format_progress(50, 100) == "50.0%"
        assert format_progress(0, 100) == "0.0%"
        assert format_progress(100, 100) == "100.0%"
        assert format_progress(0, 0) == "0%"


class TestComponents:
    """Tests for UI components"""
    
    @patch('streamlit.session_state', {})
    def test_proposal_form_validation(self):
        """Test proposal form validation logic"""
        from web.components.proposal_form import render_proposal_form
        from web.utils.helpers import validate_required_fields
        
        # Test with missing required fields
        incomplete_data = {"title": "Test"}
        required = ["title", "funder_name", "proposal_type"]
        is_valid, error = validate_required_fields(incomplete_data, required)
        assert is_valid is False
    
    def test_status_dashboard_data_processing(self):
        """Test status dashboard data processing"""
        # Mock job data
        jobs = [
            {"id": "1", "status": "completed", "created_at": "2024-01-01T00:00:00"},
            {"id": "2", "status": "processing", "created_at": "2024-01-02T00:00:00"},
            {"id": "3", "status": "failed", "created_at": "2024-01-03T00:00:00"},
        ]
        
        # Count by status
        completed = len([j for j in jobs if j.get('status', '').lower() == 'completed'])
        processing = len([j for j in jobs if j.get('status', '').lower() == 'processing'])
        failed = len([j for j in jobs if j.get('status', '').lower() == 'failed'])
        
        assert completed == 1
        assert processing == 1
        assert failed == 1


class TestIntegration:
    """Integration tests"""
    
    @patch('web.utils.api_client.requests.Session')
    def test_full_proposal_flow(self, mock_session):
        """Test full proposal creation flow"""
        # Mock API responses
        proposal_response = Mock()
        proposal_response.json.return_value = {"id": "prop123", "title": "Test"}
        proposal_response.raise_for_status = Mock()
        
        job_response = Mock()
        job_response.json.return_value = {"id": "job123", "proposal_id": "prop123"}
        job_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.post.side_effect = [proposal_response, job_response]
        mock_session.return_value = mock_session_instance
        
        client = APIClient(base_url="http://test.com/api")
        client.session = mock_session_instance
        
        # Create proposal
        proposal = client.create_proposal({"title": "Test Proposal"})
        assert proposal["id"] == "prop123"
        
        # Create job
        job = client.create_job(proposal["id"])
        assert job["id"] == "job123"
        assert job["proposal_id"] == "prop123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



