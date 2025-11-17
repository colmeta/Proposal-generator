"""Load and performance tests for response time, throughput, and scalability"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tests.utils.test_helpers import measure_execution_time, assert_performance


@pytest.mark.load
@pytest.mark.slow
class TestResponseTime:
    """Test API response times"""
    
    def test_single_request_response_time(self, client, authenticated_user):
        """Test response time for single request"""
        start_time = time.time()
        response = client.get(
            '/api/v1/projects',
            headers=authenticated_user['headers']
        )
        response_time = time.time() - start_time
        
        # Response should be fast (< 500ms for simple endpoint)
        assert response_time < 0.5, f"Response time {response_time}s exceeds 500ms"
    
    def test_endpoint_response_times(self, client, authenticated_user):
        """Test response times for different endpoints"""
        endpoints = [
            '/api/v1/projects',
            '/api/v1/proposals',
            '/api/v1/jobs'
        ]
        
        max_response_time = 1.0  # 1 second max
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(
                endpoint,
                headers=authenticated_user['headers']
            )
            response_time = time.time() - start_time
            
            assert response_time < max_response_time, \
                f"Endpoint {endpoint} response time {response_time}s exceeds {max_response_time}s"
    
    @measure_execution_time
    def test_complex_operation_performance(self, mock_database, mock_llm_service):
        """Test performance of complex operations"""
        # Create project
        project = mock_database.add('projects', get_sample_project())
        
        # Generate proposal (complex operation)
        proposal_data = get_sample_proposal(project_id=project['id'])
        result = mock_llm_service.generate_proposal(proposal_data)
        
        # Execution time is stored in function attribute
        assert self.test_complex_operation_performance.execution_time < 5.0


@pytest.mark.load
@pytest.mark.slow
class TestThroughput:
    """Test system throughput"""
    
    def test_concurrent_requests(self, client, authenticated_user):
        """Test handling concurrent requests"""
        num_requests = 10
        max_time = 5.0  # All requests should complete within 5 seconds
        
        def make_request():
            return client.get(
                '/api/v1/projects',
                headers=authenticated_user['headers']
            )
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # All requests should complete
        assert len(results) == num_requests
        # Should complete within reasonable time
        assert total_time < max_time, f"Concurrent requests took {total_time}s, expected < {max_time}s"
    
    def test_requests_per_second(self, client, authenticated_user):
        """Test requests per second throughput"""
        num_requests = 20
        min_rps = 5  # Minimum requests per second
        
        start_time = time.time()
        for _ in range(num_requests):
            client.get(
                '/api/v1/projects',
                headers=authenticated_user['headers']
            )
        total_time = time.time() - start_time
        
        rps = num_requests / total_time
        assert rps >= min_rps, f"Throughput {rps} RPS is below minimum {min_rps} RPS"


@pytest.mark.load
@pytest.mark.slow
class TestConcurrentUsers:
    """Test system under concurrent user load"""
    
    def test_multiple_users_simultaneous(self, client, app):
        """Test multiple users making simultaneous requests"""
        from api.middleware.auth import get_auth
        
        auth = get_auth()
        num_users = 5
        
        # Create API keys for multiple users
        users = []
        for i in range(num_users):
            api_key = auth.generate_api_key(user_id=i+1, roles=['user'])
            users.append({
                'user_id': i+1,
                'headers': {'X-API-Key': api_key}
            })
        
        def user_request(user_data):
            return client.get(
                '/api/v1/projects',
                headers=user_data['headers']
            )
        
        # All users make requests simultaneously
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_request, user) for user in users]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should succeed
        assert len(results) == num_users
        # Most should return 200 (or 404 if no data)
        success_count = sum(1 for r in results if r.status_code in [200, 404])
        assert success_count >= num_users * 0.8  # At least 80% success rate


@pytest.mark.load
@pytest.mark.slow
class TestStress:
    """Stress tests for system limits"""
    
    def test_high_load_stress(self, client, authenticated_user):
        """Test system under high load"""
        num_requests = 100
        max_failure_rate = 0.1  # 10% failure rate acceptable
        
        results = []
        for _ in range(num_requests):
            response = client.get(
                '/api/v1/projects',
                headers=authenticated_user['headers']
            )
            results.append(response.status_code)
        
        # Calculate failure rate
        failures = sum(1 for code in results if code >= 500)
        failure_rate = failures / num_requests
        
        assert failure_rate <= max_failure_rate, \
            f"Failure rate {failure_rate} exceeds maximum {max_failure_rate}"
    
    def test_sustained_load(self, client, authenticated_user):
        """Test system under sustained load"""
        duration = 10  # seconds
        requests_per_second = 5
        total_requests = duration * requests_per_second
        
        start_time = time.time()
        results = []
        
        while time.time() - start_time < duration:
            response = client.get(
                '/api/v1/projects',
                headers=authenticated_user['headers']
            )
            results.append(response.status_code)
            time.sleep(1.0 / requests_per_second)
        
        # Should handle sustained load
        assert len(results) >= total_requests * 0.8  # At least 80% of target


@pytest.mark.load
@pytest.mark.slow
class TestScalability:
    """Test system scalability"""
    
    def test_large_dataset_handling(self, mock_database):
        """Test handling large datasets"""
        # Create large dataset
        num_records = 1000
        start_time = time.time()
        
        for i in range(num_records):
            mock_database.add('projects', get_sample_project())
        
        creation_time = time.time() - start_time
        
        # Should create records efficiently
        assert creation_time < 10.0, f"Creating {num_records} records took {creation_time}s"
        
        # Query large dataset
        start_time = time.time()
        results = mock_database.query('projects', {})
        query_time = time.time() - start_time
        
        assert len(results) == num_records
        assert query_time < 2.0, f"Querying {num_records} records took {query_time}s"
    
    def test_memory_usage(self, mock_database):
        """Test memory usage with large datasets"""
        import sys
        
        # Create many records
        projects = []
        for i in range(100):
            project = mock_database.add('projects', get_sample_project())
            projects.append(project)
        
        # Check memory usage (rough estimate)
        size = sys.getsizeof(projects)
        # Should not exceed reasonable limit (e.g., 10MB for 100 records)
        max_size = 10 * 1024 * 1024  # 10MB
        assert size < max_size, f"Memory usage {size} bytes exceeds {max_size} bytes"


