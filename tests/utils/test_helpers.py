"""Test helper functions for assertions, data generation, mocking, and utilities"""
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from functools import wraps


def assert_response_success(response, status_code: int = 200):
    """Assert that response is successful"""
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}"
    if hasattr(response, 'json'):
        data = response.json()
        assert 'error' not in data or data.get('error') is None, f"Response contains error: {data}"


def assert_response_error(response, status_code: int, error_type: str = None):
    """Assert that response is an error"""
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}"
    if hasattr(response, 'json'):
        data = response.json()
        assert 'error' in data, "Response should contain error field"
        if error_type:
            assert data['error'] == error_type, f"Expected error type {error_type}, got {data['error']}"


def assert_dict_contains(dict1: Dict, dict2: Dict):
    """Assert that dict1 contains all keys and values from dict2"""
    for key, value in dict2.items():
        assert key in dict1, f"Key {key} not found in dict1"
        assert dict1[key] == value, f"Value mismatch for key {key}: expected {value}, got {dict1[key]}"


def assert_list_contains(items: List[Any], item: Any):
    """Assert that list contains item"""
    assert item in items, f"Item {item} not found in list"


def assert_valid_uuid(uuid_string: str):
    """Assert that string is a valid UUID"""
    import uuid
    try:
        uuid.UUID(uuid_string)
    except ValueError:
        assert False, f"{uuid_string} is not a valid UUID"


def assert_valid_datetime(datetime_string: str):
    """Assert that string is a valid ISO datetime"""
    try:
        datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
    except ValueError:
        assert False, f"{datetime_string} is not a valid ISO datetime"


def assert_valid_email(email: str):
    """Assert that string is a valid email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    assert re.match(pattern, email), f"{email} is not a valid email address"


def assert_valid_url(url: str):
    """Assert that string is a valid URL"""
    from urllib.parse import urlparse
    result = urlparse(url)
    assert all([result.scheme, result.netloc]), f"{url} is not a valid URL"


def generate_random_string(length: int = 10) -> str:
    """Generate random string"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email() -> str:
    """Generate random email address"""
    return f"{generate_random_string(8)}@{generate_random_string(6)}.com"


def generate_random_url() -> str:
    """Generate random URL"""
    return f"https://{generate_random_string(10)}.example.com"


def wait_for_condition(condition_func, timeout: int = 10, interval: float = 0.5):
    """Wait for a condition to be true"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def mock_time(monkeypatch, timestamp: datetime):
    """Mock current time for testing"""
    def mock_now():
        return timestamp
    monkeypatch.setattr('datetime.datetime.utcnow', mock_now)


def create_test_file(content: str = "test content", filename: str = None) -> str:
    """Create a temporary test file"""
    import tempfile
    import os
    
    if filename is None:
        filename = f"test_{generate_random_string(8)}.txt"
    
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return file_path


def cleanup_test_file(file_path: str):
    """Clean up test file"""
    import os
    if os.path.exists(file_path):
        os.remove(file_path)


def assert_performance(execution_time: float, max_time: float):
    """Assert that execution time is within limits"""
    assert execution_time <= max_time, f"Execution took {execution_time}s, expected <= {max_time}s"


def measure_execution_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        wrapper.execution_time = execution_time
        return result
    wrapper.execution_time = 0
    return wrapper


def assert_json_structure(data: Dict, schema: Dict):
    """Assert that data matches JSON schema structure"""
    for key, expected_type in schema.items():
        assert key in data, f"Key {key} not found in data"
        actual_type = type(data[key]).__name__
        if isinstance(expected_type, type):
            assert isinstance(data[key], expected_type), \
                f"Key {key} has type {actual_type}, expected {expected_type.__name__}"
        elif isinstance(expected_type, dict):
            assert isinstance(data[key], dict), f"Key {key} should be a dict"
            assert_json_structure(data[key], expected_type)
        elif isinstance(expected_type, list):
            assert isinstance(data[key], list), f"Key {key} should be a list"
            if expected_type and isinstance(expected_type[0], dict):
                for item in data[key]:
                    assert isinstance(item, dict), f"Items in {key} should be dicts"


def compare_dicts_ignore_keys(dict1: Dict, dict2: Dict, ignore_keys: List[str]):
    """Compare two dicts ignoring specified keys"""
    dict1_filtered = {k: v for k, v in dict1.items() if k not in ignore_keys}
    dict2_filtered = {k: v for k, v in dict2.items() if k not in ignore_keys}
    assert dict1_filtered == dict2_filtered, f"Dicts differ: {dict1_filtered} != {dict2_filtered}"


def assert_rate_limit_headers(response, limit: int = None, remaining: int = None):
    """Assert rate limit headers in response"""
    assert 'X-RateLimit-Limit' in response.headers, "Missing X-RateLimit-Limit header"
    if limit:
        assert int(response.headers['X-RateLimit-Limit']) == limit
    assert 'X-RateLimit-Remaining' in response.headers, "Missing X-RateLimit-Remaining header"
    if remaining is not None:
        assert int(response.headers['X-RateLimit-Remaining']) == remaining
    assert 'X-RateLimit-Reset' in response.headers, "Missing X-RateLimit-Reset header"


def assert_auth_headers(response, token_type: str = "Bearer"):
    """Assert authentication headers in response"""
    if 'Authorization' in response.headers:
        auth_header = response.headers['Authorization']
        assert auth_header.startswith(token_type), \
            f"Authorization header should start with {token_type}"


def create_mock_request(method: str = "GET", path: str = "/", headers: Dict = None, json_data: Dict = None):
    """Create a mock request object"""
    from unittest.mock import Mock
    request = Mock()
    request.method = method
    request.path = path
    request.headers = headers or {}
    request.json = json_data
    request.args = {}
    request.form = {}
    request.remote_addr = "127.0.0.1"
    return request


def assert_database_record(db_session, model_class, filters: Dict, expected_count: int = 1):
    """Assert database record exists"""
    query = db_session.query(model_class)
    for key, value in filters.items():
        query = query.filter(getattr(model_class, key) == value)
    count = query.count()
    assert count == expected_count, \
        f"Expected {expected_count} records, found {count}"


def assert_no_database_record(db_session, model_class, filters: Dict):
    """Assert database record does not exist"""
    assert_database_record(db_session, model_class, filters, expected_count=0)

