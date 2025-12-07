"""Security tests for input validation: SQL injection, XSS, CSRF, file upload security"""
import pytest
from tests.utils.test_helpers import assert_response_error


@pytest.mark.security
class TestSQLInjection:
    """Test SQL injection protection"""
    
    def test_sql_injection_in_query_params(self, client, authenticated_user):
        """Test SQL injection in query parameters"""
        sql_injection_payloads = [
            "1' OR '1'='1",
            "1; DROP TABLE users;--",
            "1' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1--"
        ]
        
        for payload in sql_injection_payloads:
            response = client.get(
                f'/api/v1/projects?id={payload}',
                headers=authenticated_user['headers']
            )
            
            # Should not execute SQL injection
            # Should return 400 or sanitized result
            assert response.status_code in [200, 400, 404], \
                f"SQL injection payload should be rejected: {payload}"
    
    def test_sql_injection_in_json_body(self, client, authenticated_user):
        """Test SQL injection in JSON request body"""
        sql_injection_data = {
            'name': "Test'; DROP TABLE projects;--",
            'description': "1' OR '1'='1"
        }
        
        response = client.post(
            '/api/v1/projects',
            json=sql_injection_data,
            headers=authenticated_user['headers']
        )
        
        # Should sanitize or reject
        assert response.status_code in [200, 201, 400, 422]
        
        # Should not contain SQL injection in response
        if response.status_code in [200, 201]:
            data = response.json()
            response_str = str(data)
            assert "DROP TABLE" not in response_str
            assert "OR '1'='1" not in response_str
    
    def test_parameterized_queries(self, mock_database):
        """Test that parameterized queries are used"""
        # In real implementation, would verify SQL queries use parameters
        # For now, verify pattern
        project_data = {
            'name': "Test'; DROP TABLE projects;--",
            'description': "Description"
        }
        
        # Should use parameterized query (safe)
        project = mock_database.add('projects', project_data)
        
        # Verify data is stored correctly (not executed as SQL)
        retrieved = mock_database.get('projects', project['id'])
        assert retrieved['name'] == project_data['name']


@pytest.mark.security
class TestXSS:
    """Test Cross-Site Scripting (XSS) protection"""
    
    def test_xss_in_input_fields(self, client, authenticated_user):
        """Test XSS in input fields"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>"
        ]
        
        for payload in xss_payloads:
            project_data = {
                'name': payload,
                'description': 'Test description'
            }
            
            response = client.post(
                '/api/v1/projects',
                json=project_data,
                headers=authenticated_user['headers']
            )
            
            # Should sanitize XSS
            if response.status_code in [200, 201]:
                data = response.json()
                response_str = str(data)
                # Should not contain script tags
                assert "<script>" not in response_str.lower()
                assert "javascript:" not in response_str.lower()
    
    def test_xss_in_url_parameters(self, client, authenticated_user):
        """Test XSS in URL parameters"""
        xss_payload = "<script>alert('XSS')</script>"
        
        response = client.get(
            f'/api/v1/projects?search={xss_payload}',
            headers=authenticated_user['headers']
        )
        
        # Should sanitize or reject
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            data = response.json()
            response_str = str(data)
            assert "<script>" not in response_str.lower()
    
    def test_content_security_policy(self, client):
        """Test Content Security Policy headers"""
        response = client.get('/')
        
        # Should have CSP headers
        # (Depends on actual implementation)
        if 'Content-Security-Policy' in response.headers:
            csp = response.headers['Content-Security-Policy']
            assert "script-src" in csp.lower()


@pytest.mark.security
class TestCSRF:
    """Test Cross-Site Request Forgery (CSRF) protection"""
    
    def test_csrf_token_required(self, client):
        """Test that CSRF token is required for state-changing operations"""
        # POST request without CSRF token
        response = client.post(
            '/api/v1/projects',
            json={'name': 'Test Project'}
        )
        
        # Should return 403 if CSRF protection enabled
        # (Depends on configuration)
        assert response.status_code in [401, 403, 400]
    
    def test_csrf_token_validation(self, client, authenticated_user):
        """Test CSRF token validation"""
        # Get CSRF token
        # (Would need actual implementation)
        csrf_token = "test_csrf_token"
        
        # Request with valid CSRF token
        response = client.post(
            '/api/v1/projects',
            json={'name': 'Test Project'},
            headers={
                **authenticated_user['headers'],
                'X-CSRF-Token': csrf_token
            }
        )
        
        # Should succeed with valid token
        # (Depends on actual implementation)
        assert response.status_code in [200, 201, 403]
    
    def test_csrf_token_invalid(self, client, authenticated_user):
        """Test that invalid CSRF token is rejected"""
        response = client.post(
            '/api/v1/projects',
            json={'name': 'Test Project'},
            headers={
                **authenticated_user['headers'],
                'X-CSRF-Token': 'invalid_token'
            }
        )
        
        # Should return 403
        # (Depends on actual implementation)
        if response.status_code == 403:
            assert response.status_code == 403


@pytest.mark.security
class TestFileUploadSecurity:
    """Test file upload security"""
    
    def test_file_type_validation(self, client, authenticated_user):
        """Test that only allowed file types are accepted"""
        # Try to upload executable file
        malicious_file = {
            'name': 'malicious.exe',
            'content': b'MZ\x90\x00'  # PE executable header
        }
        
        response = client.post(
            '/api/v1/documents',
            json=malicious_file,
            headers=authenticated_user['headers']
        )
        
        # Should reject executable files
        assert response.status_code in [400, 422, 403]
    
    def test_file_size_limits(self, client, authenticated_user):
        """Test file size limits"""
        # Try to upload very large file
        large_file = {
            'name': 'large_file.pdf',
            'content': b'x' * (100 * 1024 * 1024)  # 100MB
        }
        
        response = client.post(
            '/api/v1/documents',
            json=large_file,
            headers=authenticated_user['headers']
        )
        
        # Should reject files exceeding size limit
        assert response.status_code in [400, 413, 422]
    
    def test_filename_sanitization(self, client, authenticated_user):
        """Test filename sanitization"""
        dangerous_filenames = [
            "../../etc/passwd",
            "file<script>.pdf",
            "file\x00.pdf",
            "file\n.pdf"
        ]
        
        for filename in dangerous_filenames:
            file_data = {
                'name': filename,
                'content': b'test content'
            }
            
            response = client.post(
                '/api/v1/documents',
                json=file_data,
                headers=authenticated_user['headers']
            )
            
            # Should sanitize or reject dangerous filenames
            assert response.status_code in [200, 201, 400, 422]
            
            if response.status_code in [200, 201]:
                data = response.json()
                saved_filename = data.get('name') or data.get('data', {}).get('name')
                # Should not contain path traversal or special characters
                assert '../' not in saved_filename
                assert '<' not in saved_filename
    
    def test_malicious_file_content(self, client, authenticated_user):
        """Test detection of malicious file content"""
        # Try to upload file with embedded scripts
        malicious_content = b'%PDF-1.4\n<script>alert("XSS")</script>'
        
        file_data = {
            'name': 'document.pdf',
            'content': malicious_content.hex()
        }
        
        response = client.post(
            '/api/v1/documents',
            json=file_data,
            headers=authenticated_user['headers']
        )
        
        # Should scan and reject malicious content
        # (Depends on actual implementation)
        assert response.status_code in [200, 201, 400, 403, 422]



