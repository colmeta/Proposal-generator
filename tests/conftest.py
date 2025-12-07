"""Pytest configuration with fixtures, setup/teardown, and test configuration"""
import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch
from flask import Flask
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.fixtures.test_data import (
    get_sample_user, get_sample_project, get_sample_proposal,
    get_sample_job, get_sample_funder, get_sample_document
)
from tests.fixtures.mock_services import (
    MockLLMService, MockDatabase, MockFileStorage,
    MockExternalAPI, MockWebhookService
)


@pytest.fixture(scope="session")
def app():
    """Create Flask application for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Disable logging during tests
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    return app


@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session():
    """Create database session for testing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture(scope="function")
def mock_llm_service():
    """Mock LLM service fixture"""
    return MockLLMService()


@pytest.fixture(scope="function")
def mock_database():
    """Mock database fixture"""
    return MockDatabase()


@pytest.fixture(scope="function")
def mock_file_storage():
    """Mock file storage fixture"""
    return MockFileStorage()


@pytest.fixture(scope="function")
def mock_external_api():
    """Mock external API fixture"""
    return MockExternalAPI()


@pytest.fixture(scope="function")
def mock_webhook_service():
    """Mock webhook service fixture"""
    return MockWebhookService()


@pytest.fixture(scope="function")
def sample_user():
    """Sample user fixture"""
    return get_sample_user()


@pytest.fixture(scope="function")
def sample_project():
    """Sample project fixture"""
    return get_sample_project()


@pytest.fixture(scope="function")
def sample_proposal():
    """Sample proposal fixture"""
    return get_sample_proposal()


@pytest.fixture(scope="function")
def sample_job():
    """Sample job fixture"""
    return get_sample_job()


@pytest.fixture(scope="function")
def sample_funder():
    """Sample funder fixture"""
    return get_sample_funder()


@pytest.fixture(scope="function")
def sample_document():
    """Sample document fixture"""
    return get_sample_document()


@pytest.fixture(scope="function")
def authenticated_user(client, app):
    """Create authenticated user for testing"""
    from api.middleware.auth import get_auth
    
    auth = get_auth()
    api_key = auth.generate_api_key(
        user_id=1,
        roles=['user'],
        permissions=['read', 'write']
    )
    
    return {
        'user_id': 1,
        'api_key': api_key,
        'headers': {'X-API-Key': api_key}
    }


@pytest.fixture(scope="function")
def admin_user(client, app):
    """Create admin user for testing"""
    from api.middleware.auth import get_auth
    
    auth = get_auth()
    api_key = auth.generate_api_key(
        user_id=2,
        roles=['admin'],
        permissions=['read', 'write', 'admin']
    )
    
    return {
        'user_id': 2,
        'api_key': api_key,
        'headers': {'X-API-Key': api_key}
    }


@pytest.fixture(scope="function", autouse=True)
def reset_mocks():
    """Reset all mocks before each test"""
    yield
    # Cleanup after test
    pass


@pytest.fixture(scope="function")
def mock_env_vars(monkeypatch):
    """Mock environment variables"""
    env_vars = {
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'DATABASE_URL': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture(scope="function")
def temp_file():
    """Create temporary file for testing"""
    import tempfile
    import os
    
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture(scope="function")
def mock_time_now(monkeypatch):
    """Mock current time"""
    fixed_time = datetime(2024, 1, 1, 12, 0, 0)
    
    def mock_now():
        return fixed_time
    
    monkeypatch.setattr('datetime.datetime.utcnow', mock_now)
    return fixed_time


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "load: Load and performance tests"
    )
    config.addinivalue_line(
        "markers", "security: Security tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add markers based on test path
        if 'integration' in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif 'e2e' in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif 'load' in str(item.fspath):
            item.add_marker(pytest.mark.load)
        elif 'security' in str(item.fspath):
            item.add_marker(pytest.mark.security)
        else:
            item.add_marker(pytest.mark.unit)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before all tests"""
    # Setup code here
    yield
    # Teardown code here
    pass



