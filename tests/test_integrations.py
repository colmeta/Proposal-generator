"""Tests for API integrations, webhooks, rate limiting, and authentication"""
import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime

# Import modules to test
from api.integrations.webhooks import WebhookManager, WebhookEvent, WebhookEventType
from api.integrations.crm import SalesforceIntegration, HubSpotIntegration
from api.integrations.project_management import AsanaIntegration, TrelloIntegration, JiraIntegration
from api.middleware.rate_limiter import RateLimiter, TokenBucket
from api.middleware.auth import AuthMiddleware, require_auth, require_role
from api.middleware.logging import LoggingMiddleware
from api.schemas.requests import JobCreateSchema, ProjectCreateSchema, WebhookRegisterSchema
from api.schemas.responses import JobResponseSchema, ErrorResponseSchema


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def webhook_manager():
    """Create webhook manager for testing"""
    return WebhookManager(db_session=None)


@pytest.fixture
def rate_limiter():
    """Create rate limiter for testing"""
    return RateLimiter()


@pytest.fixture
def auth_middleware():
    """Create auth middleware for testing"""
    return AuthMiddleware('test-secret-key')


class TestWebhooks:
    """Test webhook functionality"""
    
    def test_webhook_event_creation(self):
        """Test creating a webhook event"""
        event = WebhookEvent(
            event_type=WebhookEventType.JOB_COMPLETED,
            data={"job_id": 1, "status": "completed"}
        )
        
        assert event.event_type == WebhookEventType.JOB_COMPLETED
        assert event.data["job_id"] == 1
        assert event.id is not None
    
    def test_webhook_event_to_dict(self):
        """Test converting webhook event to dictionary"""
        event = WebhookEvent(
            event_type=WebhookEventType.JOB_FAILED,
            data={"job_id": 1, "error": "Processing failed"}
        )
        
        event_dict = event.to_dict()
        assert event_dict["event_type"] == "job.failed"
        assert event_dict["data"]["job_id"] == 1
        assert "timestamp" in event_dict
    
    def test_webhook_signature_generation(self, webhook_manager):
        """Test webhook signature generation"""
        payload = '{"test": "data"}'
        secret = "test-secret"
        
        signature = webhook_manager._generate_signature(payload, secret)
        assert signature is not None
        assert len(signature) == 64  # SHA256 hex length
    
    def test_webhook_signature_verification(self, webhook_manager):
        """Test webhook signature verification"""
        payload = '{"test": "data"}'
        secret = "test-secret"
        
        signature = webhook_manager._generate_signature(payload, secret)
        assert webhook_manager.verify_signature(payload, signature, secret) is True
        assert webhook_manager.verify_signature(payload, "invalid", secret) is False


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_token_bucket_creation(self):
        """Test creating a token bucket"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.capacity == 10
        assert bucket.refill_rate == 1.0
        assert bucket.tokens == 10.0
    
    def test_token_bucket_consume(self):
        """Test consuming tokens from bucket"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        # Consume all tokens
        for _ in range(10):
            assert bucket.consume() is True
        
        # Should fail after all tokens consumed
        assert bucket.consume() is False
    
    def test_token_bucket_refill(self):
        """Test token bucket refill over time"""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens per second
        
        # Consume all tokens
        for _ in range(10):
            bucket.consume()
        
        # Wait for refill
        time.sleep(0.2)
        
        # Should have tokens again
        assert bucket.consume() is True
    
    def test_rate_limiter_user_limit(self, rate_limiter):
        """Test per-user rate limiting"""
        user_id = "user123"
        rate_limiter.set_user_limit(user_id, 5, 1.0)
        
        # Should allow 5 requests
        for _ in range(5):
            allowed, _ = rate_limiter.check_rate_limit(user_id=user_id, ip="127.0.0.1")
            assert allowed is True
        
        # Should block 6th request
        allowed, headers = rate_limiter.check_rate_limit(user_id=user_id, ip="127.0.0.1")
        assert allowed is False
        assert "X-RateLimit-Limit" in headers
    
    def test_rate_limiter_ip_limit(self, rate_limiter):
        """Test per-IP rate limiting"""
        ip = "192.168.1.1"
        rate_limiter.set_ip_limit(ip, 3, 1.0)
        
        # Should allow 3 requests
        for _ in range(3):
            allowed, _ = rate_limiter.check_rate_limit(ip=ip)
            assert allowed is True
        
        # Should block 4th request
        allowed, _ = rate_limiter.check_rate_limit(ip=ip)
        assert allowed is False


class TestAuthentication:
    """Test authentication functionality"""
    
    def test_api_key_generation(self, auth_middleware):
        """Test API key generation"""
        api_key = auth_middleware.generate_api_key(
            user_id=1,
            permissions=["read", "write"],
            roles=["user"]
        )
        
        assert api_key is not None
        assert len(api_key) > 0
        assert api_key in auth_middleware.api_keys
    
    def test_api_key_authentication(self, auth_middleware):
        """Test API key authentication"""
        api_key = auth_middleware.generate_api_key(user_id=1, roles=["admin"])
        
        # Mock request
        with patch('api.middleware.auth.request') as mock_request:
            mock_request.headers.get.return_value = api_key
            mock_request.args.get.return_value = None
            mock_request.headers.get.return_value = None
            
            user_data = auth_middleware.authenticate_request()
            assert user_data is not None
            assert user_data['user_id'] == 1
            assert 'admin' in user_data['roles']
    
    def test_jwt_token_generation(self, auth_middleware):
        """Test JWT token generation"""
        token = auth_middleware.generate_jwt_token(
            user_id=1,
            roles=["user"],
            permissions=["read"]
        )
        
        assert token is not None
        payload = auth_middleware.verify_jwt_token(token)
        assert payload is not None
        assert payload['user_id'] == 1
    
    def test_jwt_token_verification(self, auth_middleware):
        """Test JWT token verification"""
        token = auth_middleware.generate_jwt_token(user_id=1)
        
        # Valid token
        payload = auth_middleware.verify_jwt_token(token)
        assert payload is not None
        
        # Invalid token
        payload = auth_middleware.verify_jwt_token("invalid-token")
        assert payload is None
    
    def test_permission_check(self, auth_middleware):
        """Test permission checking"""
        user_data = {
            'user_id': 1,
            'permissions': ['read', 'write'],
            'roles': ['user']
        }
        
        assert auth_middleware.has_permission(user_data, 'read') is True
        assert auth_middleware.has_permission(user_data, 'admin') is False
    
    def test_role_check(self, auth_middleware):
        """Test role checking"""
        user_data = {
            'user_id': 1,
            'permissions': [],
            'roles': ['user', 'editor']
        }
        
        assert auth_middleware.has_role(user_data, 'user') is True
        assert auth_middleware.has_role(user_data, 'admin') is False


class TestCRMIntegrations:
    """Test CRM integration functionality"""
    
    @patch('api.integrations.crm.requests.post')
    def test_salesforce_authentication(self, mock_post):
        """Test Salesforce authentication"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test-token',
            'instance_url': 'https://test.salesforce.com'
        }
        mock_post.return_value = mock_response
        
        sf = SalesforceIntegration()
        credentials = {
            'client_id': 'test-client',
            'client_secret': 'test-secret',
            'username': 'test@example.com',
            'password': 'test-password'
        }
        
        result = sf.authenticate(credentials)
        assert result is True
        assert sf.access_token == 'test-token'
    
    @patch('api.integrations.crm.requests.post')
    def test_hubspot_authentication(self, mock_post):
        """Test HubSpot authentication"""
        hs = HubSpotIntegration()
        credentials = {'api_key': 'test-api-key'}
        
        result = hs.authenticate(credentials)
        assert result is True
        assert hs.api_key == 'test-api-key'


class TestProjectManagementIntegrations:
    """Test project management integration functionality"""
    
    def test_asana_authentication(self):
        """Test Asana authentication"""
        asana = AsanaIntegration()
        credentials = {'access_token': 'test-token'}
        
        result = asana.authenticate(credentials)
        assert result is True
        assert asana.access_token == 'test-token'
    
    def test_trello_authentication(self):
        """Test Trello authentication"""
        trello = TrelloIntegration()
        credentials = {
            'api_key': 'test-key',
            'api_token': 'test-token'
        }
        
        result = trello.authenticate(credentials)
        assert result is True
        assert trello.api_key == 'test-key'
        assert trello.api_token == 'test-token'
    
    def test_jira_authentication(self):
        """Test Jira authentication"""
        jira = JiraIntegration()
        credentials = {
            'base_url': 'https://test.atlassian.net',
            'username': 'test@example.com',
            'api_token': 'test-token'
        }
        
        result = jira.authenticate(credentials)
        assert result is True
        assert jira.base_url == 'https://test.atlassian.net'


class TestSchemas:
    """Test request/response schemas"""
    
    def test_job_create_schema(self):
        """Test job creation schema validation"""
        valid_data = {
            "project_id": 1,
            "name": "Test Job",
            "description": "Test description",
            "priority": 5
        }
        
        schema = JobCreateSchema(**valid_data)
        assert schema.project_id == 1
        assert schema.name == "Test Job"
    
    def test_project_create_schema(self):
        """Test project creation schema validation"""
        valid_data = {
            "name": "Test Project",
            "client_name": "Test Client",
            "client_email": "client@example.com"
        }
        
        schema = ProjectCreateSchema(**valid_data)
        assert schema.name == "Test Project"
        assert schema.client_email == "client@example.com"
    
    def test_webhook_register_schema(self):
        """Test webhook registration schema validation"""
        valid_data = {
            "url": "https://example.com/webhook",
            "event_types": ["job.completed", "job.failed"]
        }
        
        schema = WebhookRegisterSchema(**valid_data)
        assert str(schema.url) == "https://example.com/webhook"
        assert len(schema.event_types) == 2


class TestLogging:
    """Test logging middleware"""
    
    def test_logging_middleware_init(self, app):
        """Test logging middleware initialization"""
        from api.middleware.logging import setup_logging_middleware
        setup_logging_middleware(app)
        
        # Middleware should be set up
        assert app.before_request_funcs is not None
        assert app.after_request_funcs is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

