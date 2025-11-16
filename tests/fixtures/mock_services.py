"""Mock service fixtures for LLM APIs, external services, database, and file storage"""
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, List
import json
from datetime import datetime


class MockLLMService:
    """Mock LLM service for testing"""
    
    def __init__(self):
        self.responses = {}
        self.call_count = 0
    
    def generate_text(self, prompt: str, model: str = "gpt-4", **kwargs) -> Dict[str, Any]:
        """Mock text generation"""
        self.call_count += 1
        return {
            'content': f"Mock response for: {prompt[:50]}...",
            'model': model,
            'tokens_used': 100,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def generate_proposal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock proposal generation"""
        return {
            'content': "Mock proposal content",
            'sections': {
                'executive_summary': 'Mock executive summary',
                'introduction': 'Mock introduction',
                'objectives': ['Objective 1', 'Objective 2'],
                'methodology': 'Mock methodology',
                'budget': 'Mock budget',
                'timeline': 'Mock timeline'
            },
            'tokens_used': 500,
            'model': 'gpt-4'
        }
    
    def research_topic(self, topic: str) -> Dict[str, Any]:
        """Mock research"""
        return {
            'content': f"Mock research about {topic}",
            'sources': [
                {'title': 'Source 1', 'url': 'https://example.com/1', 'relevance': 0.9},
                {'title': 'Source 2', 'url': 'https://example.com/2', 'relevance': 0.8}
            ],
            'tokens_used': 300
        }


class MockDatabase:
    """Mock database for testing"""
    
    def __init__(self):
        self.data = {
            'users': [],
            'projects': [],
            'jobs': [],
            'proposals': [],
            'documents': []
        }
        self.transactions = []
    
    def add(self, table: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Add item to mock database"""
        if table not in self.data:
            self.data[table] = []
        item['id'] = len(self.data[table]) + 1
        self.data[table].append(item)
        return item
    
    def get(self, table: str, item_id: int) -> Dict[str, Any]:
        """Get item from mock database"""
        items = self.data.get(table, [])
        return next((item for item in items if item.get('id') == item_id), None)
    
    def query(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query mock database"""
        items = self.data.get(table, [])
        if not filters:
            return items
        
        results = []
        for item in items:
            match = all(item.get(k) == v for k, v in filters.items())
            if match:
                results.append(item)
        return results
    
    def update(self, table: str, item_id: int, updates: Dict[str, Any]) -> bool:
        """Update item in mock database"""
        item = self.get(table, item_id)
        if item:
            item.update(updates)
            return True
        return False
    
    def delete(self, table: str, item_id: int) -> bool:
        """Delete item from mock database"""
        items = self.data.get(table, [])
        for i, item in enumerate(items):
            if item.get('id') == item_id:
                items.pop(i)
                return True
        return False
    
    def commit(self):
        """Mock commit"""
        pass
    
    def rollback(self):
        """Mock rollback"""
        pass


class MockFileStorage:
    """Mock file storage service"""
    
    def __init__(self):
        self.files = {}
        self.upload_count = 0
        self.download_count = 0
    
    def upload_file(self, file_path: str, content: bytes, metadata: Dict[str, Any] = None) -> str:
        """Mock file upload"""
        self.upload_count += 1
        file_id = f"mock_file_{self.upload_count}"
        self.files[file_id] = {
            'path': file_path,
            'content': content,
            'metadata': metadata or {},
            'uploaded_at': datetime.utcnow().isoformat()
        }
        return file_id
    
    def download_file(self, file_id: str) -> bytes:
        """Mock file download"""
        self.download_count += 1
        file_data = self.files.get(file_id)
        return file_data['content'] if file_data else b''
    
    def delete_file(self, file_id: str) -> bool:
        """Mock file deletion"""
        if file_id in self.files:
            del self.files[file_id]
            return True
        return False
    
    def get_file_url(self, file_id: str) -> str:
        """Mock file URL generation"""
        return f"https://storage.example.com/files/{file_id}"


class MockExternalAPI:
    """Mock external API service"""
    
    def __init__(self):
        self.requests = []
        self.responses = {}
    
    def get(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Mock GET request"""
        self.requests.append({'method': 'GET', 'url': url, 'headers': headers})
        return self.responses.get(url, {'status': 200, 'data': {}})
    
    def post(self, url: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Mock POST request"""
        self.requests.append({'method': 'POST', 'url': url, 'data': data, 'headers': headers})
        return self.responses.get(url, {'status': 200, 'data': {}})
    
    def set_response(self, url: str, response: Dict[str, Any]):
        """Set mock response for URL"""
        self.responses[url] = response


class MockWebhookService:
    """Mock webhook service"""
    
    def __init__(self):
        self.webhooks = []
        self.deliveries = []
    
    def register_webhook(self, url: str, event_types: List[str]) -> str:
        """Mock webhook registration"""
        webhook_id = f"webhook_{len(self.webhooks) + 1}"
        self.webhooks.append({
            'id': webhook_id,
            'url': url,
            'event_types': event_types,
            'active': True
        })
        return webhook_id
    
    def send_event(self, event_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Mock webhook event delivery"""
        deliveries = []
        for webhook in self.webhooks:
            if webhook['active'] and event_type in webhook['event_types']:
                delivery = {
                    'webhook_id': webhook['id'],
                    'url': webhook['url'],
                    'event_type': event_type,
                    'data': data,
                    'status': 'delivered',
                    'timestamp': datetime.utcnow().isoformat()
                }
                self.deliveries.append(delivery)
                deliveries.append(delivery)
        return deliveries


# Pytest fixtures
def mock_llm_service():
    """Pytest fixture for mock LLM service"""
    return MockLLMService()


def mock_database():
    """Pytest fixture for mock database"""
    return MockDatabase()


def mock_file_storage():
    """Pytest fixture for mock file storage"""
    return MockFileStorage()


def mock_external_api():
    """Pytest fixture for mock external API"""
    return MockExternalAPI()


def mock_webhook_service():
    """Pytest fixture for mock webhook service"""
    return MockWebhookService()


# Context managers for patching
class MockLLMContext:
    """Context manager for mocking LLM services"""
    
    def __init__(self):
        self.mock_service = MockLLMService()
        self.patchers = []
    
    def __enter__(self):
        # Patch common LLM service imports
        patcher1 = patch('api.services.llm.LLMService', return_value=self.mock_service)
        patcher2 = patch('api.agents.llm_agent.LLMService', return_value=self.mock_service)
        self.patchers = [patcher1, patcher2]
        for p in self.patchers:
            p.start()
        return self.mock_service
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in self.patchers:
            p.stop()


class MockDatabaseContext:
    """Context manager for mocking database"""
    
    def __init__(self):
        self.mock_db = MockDatabase()
        self.patchers = []
    
    def __enter__(self):
        patcher = patch('api.database.db', self.mock_db)
        self.patchers = [patcher]
        for p in self.patchers:
            p.start()
        return self.mock_db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in self.patchers:
            p.stop()

