"""
Security and Compliance Tests
Tests for encryption, authentication, authorization, GDPR, audit logging, etc.
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

from security.encryption import EncryptionService
from security.authentication import AuthenticationService
from security.authorization import AuthorizationService, Role, Permission
from security.data_protection import DataProtectionService
from security.gdpr_compliance import GDPRComplianceService, GDPRRequestType
from security.audit_log import AuditLogService, AuditEventType
from security.input_validation import InputValidationService
from security.rate_limiting import SecurityRateLimiter
from security.vulnerability_scanner import VulnerabilityScanner
from security.compliance_reports import ComplianceReportsService


class TestEncryptionService:
    """Tests for encryption service"""
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        service = EncryptionService()
        original = "sensitive data"
        
        encrypted = service.encrypt(original)
        assert encrypted != original
        assert isinstance(encrypted, str)
        
        decrypted = service.decrypt(encrypted)
        assert decrypted == original
    
    def test_encrypt_field_none(self):
        """Test encrypting None value"""
        service = EncryptionService()
        assert service.encrypt_field(None) is None
    
    def test_decrypt_field_none(self):
        """Test decrypting None value"""
        service = EncryptionService()
        assert service.decrypt_field(None) is None
    
    def test_generate_key(self):
        """Test key generation"""
        service = EncryptionService()
        key = service.generate_key()
        assert isinstance(key, str)
        assert len(key) > 0


class TestAuthenticationService:
    """Tests for authentication service"""
    
    def test_hash_password(self):
        """Test password hashing"""
        service = AuthenticationService()
        password = "test_password"
        
        hashed = service.hash_password(password)
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_password(self):
        """Test password verification"""
        service = AuthenticationService()
        password = "test_password"
        hashed = service.hash_password(password)
        
        assert service.verify_password(password, hashed) is True
        assert service.verify_password("wrong_password", hashed) is False
    
    def test_create_verify_token(self):
        """Test JWT token creation and verification"""
        service = AuthenticationService()
        data = {"user_id": "123", "role": "user"}
        
        token = service.create_access_token(data)
        assert isinstance(token, str)
        
        decoded = service.verify_token(token)
        assert decoded is not None
        assert decoded["user_id"] == "123"
    
    def test_verify_invalid_token(self):
        """Test invalid token verification"""
        service = AuthenticationService()
        assert service.verify_token("invalid_token") is None
    
    def test_session_management(self):
        """Test session creation and retrieval"""
        service = AuthenticationService()
        user_id = "123"
        user_data = {"name": "Test User"}
        
        session_id = service.create_session(user_id, user_data)
        assert isinstance(session_id, str)
        
        session = service.get_session(session_id)
        assert session is not None
        assert session["user_id"] == user_id
        
        assert service.delete_session(session_id) is True
        assert service.get_session(session_id) is None


class TestAuthorizationService:
    """Tests for authorization service"""
    
    def test_has_permission(self):
        """Test permission checking"""
        service = AuthorizationService()
        
        assert service.has_permission([Role.ADMIN], Permission.CREATE_PROPOSAL) is True
        assert service.has_permission([Role.USER], Permission.CREATE_PROPOSAL) is True
        assert service.has_permission([Role.GUEST], Permission.CREATE_PROPOSAL) is False
    
    def test_has_any_permission(self):
        """Test any permission checking"""
        service = AuthorizationService()
        
        assert service.has_any_permission(
            [Role.USER],
            [Permission.CREATE_PROPOSAL, Permission.MANAGE_USERS]
        ) is True
        
        assert service.has_any_permission(
            [Role.GUEST],
            [Permission.CREATE_PROPOSAL, Permission.MANAGE_USERS]
        ) is False
    
    def test_resource_permission(self):
        """Test resource-level permissions"""
        service = AuthorizationService()
        
        service.grant_resource_permission("proposal", "123", Permission.READ_PROPOSAL)
        
        assert service.check_resource_permission(
            [Role.USER],
            "user1",
            "proposal",
            "123",
            Permission.READ_PROPOSAL
        ) is True


class TestDataProtectionService:
    """Tests for data protection service"""
    
    def test_detect_pii(self):
        """Test PII detection"""
        service = DataProtectionService()
        text = "Contact me at test@example.com or call 555-123-4567"
        
        detected = service.detect_pii(text)
        assert "email" in detected
        assert "phone" in detected
    
    def test_mask_pii(self):
        """Test PII masking"""
        service = DataProtectionService()
        text = "Email: test@example.com"
        
        masked = service.mask_pii(text)
        assert "test@example.com" not in masked
        assert "*" in masked
    
    def test_anonymize_data(self):
        """Test data anonymization"""
        service = DataProtectionService()
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
        
        anonymized = service.anonymize_data(data, ["email"])
        assert anonymized["email"] != data["email"]
        assert anonymized["name"] == data["name"]


class TestGDPRComplianceService:
    """Tests for GDPR compliance service"""
    
    def test_record_consent(self):
        """Test consent recording"""
        service = GDPRComplianceService()
        service.record_consent("user1", "data_processing", True, "Service improvement")
        
        assert service.has_consent("user1", "data_processing") is True
        assert service.has_consent("user1", "marketing") is False
    
    def test_withdraw_consent(self):
        """Test consent withdrawal"""
        service = GDPRComplianceService()
        service.record_consent("user1", "data_processing", True, "Service improvement")
        assert service.has_consent("user1", "data_processing") is True
        
        service.withdraw_consent("user1", "data_processing")
        assert service.has_consent("user1", "data_processing") is False
    
    def test_create_gdpr_request(self):
        """Test GDPR request creation"""
        service = GDPRComplianceService()
        request_id = service.create_gdpr_request("user1", GDPRRequestType.ACCESS)
        
        assert request_id in service.gdpr_requests
        assert service.gdpr_requests[request_id]["request_type"] == "access"


class TestAuditLogService:
    """Tests for audit log service"""
    
    def test_log_event(self, tmp_path):
        """Test audit event logging"""
        log_file = tmp_path / "audit.log"
        service = AuditLogService(log_file=log_file)
        
        service.log_event(
            AuditEventType.AUTHENTICATION,
            "user1",
            "login",
            success=True
        )
        
        assert log_file.exists()
        events = service.query_audit_log(user_id="user1")
        assert len(events) > 0
        assert events[0]["action"] == "login"
    
    def test_query_audit_log(self, tmp_path):
        """Test audit log querying"""
        log_file = tmp_path / "audit.log"
        service = AuditLogService(log_file=log_file)
        
        service.log_authentication("user1", True)
        service.log_authentication("user2", True)
        
        events = service.query_audit_log(user_id="user1")
        assert len(events) == 1
        assert events[0]["user_id"] == "user1"


class TestInputValidationService:
    """Tests for input validation service"""
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        service = InputValidationService()
        
        assert service.sanitize_string("  test  ") == "test"
        assert service.sanitize_string("test\x00null") == "testnull"
        assert len(service.sanitize_string("a" * 100, max_length=10)) == 10
    
    def test_validate_email(self):
        """Test email validation"""
        service = InputValidationService()
        
        assert service.validate_email("test@example.com") is True
        assert service.validate_email("invalid-email") is False
    
    def test_validate_url(self):
        """Test URL validation"""
        service = InputValidationService()
        
        assert service.validate_url("https://example.com") is True
        assert service.validate_url("http://example.com") is True
        assert service.validate_url("javascript:alert(1)") is False
    
    def test_validate_file_upload(self):
        """Test file upload validation"""
        service = InputValidationService()
        
        result = service.validate_file_upload("test.pdf")
        assert result["valid"] is True
        
        result = service.validate_file_upload("test.exe")
        assert result["valid"] is False


class TestSecurityRateLimiter:
    """Tests for security rate limiter"""
    
    def test_rate_limit_check(self):
        """Test rate limit checking"""
        limiter = SecurityRateLimiter()
        
        # First few attempts should be allowed
        for i in range(5):
            result = limiter.check_rate_limit("192.168.1.1", "ip")
            assert result["allowed"] is True
        
        # After max attempts, should be blocked
        for i in range(10):
            limiter.check_rate_limit("192.168.1.2", "ip")
        
        result = limiter.check_rate_limit("192.168.1.2", "ip")
        assert result["allowed"] is False
        assert result["blocked"] is True


class TestVulnerabilityScanner:
    """Tests for vulnerability scanner"""
    
    def test_check_security_best_practices(self):
        """Test security best practices check"""
        scanner = VulnerabilityScanner()
        result = scanner.check_security_best_practices()
        
        assert "status" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0


class TestComplianceReportsService:
    """Tests for compliance reports service"""
    
    def test_generate_access_control_report(self):
        """Test access control report generation"""
        service = ComplianceReportsService()
        report = service.generate_access_control_report()
        
        assert report["report_type"] == "access_control"
        assert "role_permissions" in report
        assert "generated_at" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

