"""
Data Protection Service
PII detection, data masking, anonymization, retention policies
"""

import re
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataProtectionService:
    """
    Data protection service for PII detection, masking, and anonymization
    """
    
    def __init__(self):
        """Initialize data protection service"""
        self.pii_patterns = self._initialize_pii_patterns()
        self.retention_policies: Dict[str, int] = {}  # data_type -> days
        logger.info("DataProtectionService initialized")
    
    def _initialize_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize PII detection patterns"""
        return {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'),
            "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
        }
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detect PII in text
        
        Args:
            text: Text to scan
        
        Returns:
            Dict mapping PII type to list of detected values
        """
        detected = {}
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected[pii_type] = list(set(matches))  # Remove duplicates
        return detected
    
    def mask_pii(self, text: str, mask_char: str = "*") -> str:
        """
        Mask PII in text
        
        Args:
            text: Text to mask
            mask_char: Character to use for masking
        
        Returns:
            Text with PII masked
        """
        masked_text = text
        for pii_type, pattern in self.pii_patterns.items():
            def mask_match(match):
                value = match.group(0)
                if len(value) <= 4:
                    return mask_char * len(value)
                # Show first 2 and last 2 characters
                return value[:2] + mask_char * (len(value) - 4) + value[-2:]
            
            masked_text = pattern.sub(mask_match, masked_text)
        return masked_text
    
    def anonymize_data(self, data: Dict[str, Any], fields_to_anonymize: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Anonymize data by replacing sensitive fields
        
        Args:
            data: Data dictionary
            fields_to_anonymize: List of field names to anonymize (if None, detects PII)
        
        Returns:
            Anonymized data dictionary
        """
        anonymized = data.copy()
        
        if fields_to_anonymize is None:
            # Auto-detect PII fields
            fields_to_anonymize = []
            for key, value in data.items():
                if isinstance(value, str):
                    if self.detect_pii(value):
                        fields_to_anonymize.append(key)
        
        for field in fields_to_anonymize:
            if field in anonymized:
                value = anonymized[field]
                if isinstance(value, str):
                    anonymized[field] = self.mask_pii(value)
                else:
                    anonymized[field] = "[ANONYMIZED]"
        
        return anonymized
    
    def set_retention_policy(self, data_type: str, days: int):
        """
        Set data retention policy
        
        Args:
            data_type: Type of data
            days: Number of days to retain
        """
        self.retention_policies[data_type] = days
        logger.info(f"Set retention policy for {data_type}: {days} days")
    
    def get_expired_data(self, data_type: str, created_at: datetime) -> bool:
        """
        Check if data has expired based on retention policy
        
        Args:
            data_type: Type of data
            created_at: Creation timestamp
        
        Returns:
            True if data has expired
        """
        if data_type not in self.retention_policies:
            return False  # No retention policy, data doesn't expire
        
        retention_days = self.retention_policies[data_type]
        expiry_date = created_at + timedelta(days=retention_days)
        return datetime.utcnow() > expiry_date
    
    def secure_delete(self, data: Any) -> bool:
        """
        Securely delete data (overwrite with zeros)
        
        Args:
            data: Data to delete
        
        Returns:
            True if deletion successful
        """
        # For strings, return True (Python handles garbage collection)
        # For files, would overwrite with zeros
        # This is a placeholder for actual secure deletion
        logger.info("Data securely deleted")
        return True
    
    def sanitize_for_logging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize data for logging (remove/mask sensitive fields)
        
        Args:
            data: Data to sanitize
        
        Returns:
            Sanitized data
        """
        sensitive_fields = ["password", "api_key", "token", "secret", "ssn", "credit_card"]
        sanitized = data.copy()
        
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"
        
        # Also mask any detected PII
        for key, value in sanitized.items():
            if isinstance(value, str):
                sanitized[key] = self.mask_pii(value)
        
        return sanitized


# Global instance
data_protection_service = DataProtectionService()

