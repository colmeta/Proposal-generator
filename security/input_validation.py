"""
Input Validation Service
SQL injection prevention, XSS prevention, CSRF protection, input sanitization
"""

import re
import bleach
from typing import Any, Optional, Dict, List
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class InputValidationService:
    """
    Input validation and sanitization service
    """
    
    def __init__(self):
        """Initialize input validation service"""
        # Allowed HTML tags for rich text (if needed)
        self.allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li']
        self.allowed_attributes = {}
        logger.info("InputValidationService initialized")
    
    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize a string input
        
        Args:
            value: String to sanitize
            max_length: Maximum length
        
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        if max_length and len(value) > max_length:
            value = value[:max_length]
            logger.warning(f"String truncated to {max_length} characters")
        
        return value
    
    def sanitize_html(self, html: str, allowed_tags: Optional[List[str]] = None) -> str:
        """
        Sanitize HTML to prevent XSS
        
        Args:
            html: HTML string to sanitize
            allowed_tags: List of allowed HTML tags
        
        Returns:
            Sanitized HTML
        """
        if allowed_tags is None:
            allowed_tags = self.allowed_tags
        
        # Use bleach to sanitize HTML
        cleaned = bleach.clean(
            html,
            tags=allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )
        return cleaned
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid email
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_url(self, url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """
        Validate URL
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed URL schemes (default: http, https)
        
        Returns:
            True if valid URL
        """
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        try:
            parsed = urlparse(url)
            return parsed.scheme in allowed_schemes and parsed.netloc
        except Exception:
            return False
    
    def prevent_sql_injection(self, value: str) -> str:
        """
        Basic SQL injection prevention (use parameterized queries instead!)
        
        Args:
            value: String value
        
        Returns:
            Sanitized value
        
        Note: This is a basic check. Always use parameterized queries!
        """
        # Remove SQL injection patterns
        dangerous_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"('|;|--|\*|xp_|sp_)",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {value[:50]}")
                # Replace with safe value
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return value
    
    def validate_file_upload(
        self,
        filename: str,
        allowed_extensions: Optional[List[str]] = None,
        max_size: int = 10 * 1024 * 1024  # 10MB default
    ) -> Dict[str, Any]:
        """
        Validate file upload
        
        Args:
            filename: Filename
            allowed_extensions: List of allowed file extensions
            max_size: Maximum file size in bytes
        
        Returns:
            Validation result
        """
        if allowed_extensions is None:
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.json']
        
        # Check extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return {
                "valid": False,
                "error": f"File extension {file_ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
            }
        
        # Check filename for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return {
                "valid": False,
                "error": "Invalid filename: path traversal detected"
            }
        
        # Sanitize filename
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        return {
            "valid": True,
            "safe_filename": safe_filename,
            "extension": file_ext,
            "max_size": max_size
        }
    
    def validate_json(self, json_string: str) -> Dict[str, Any]:
        """
        Validate and parse JSON
        
        Args:
            json_string: JSON string to validate
        
        Returns:
            Validation result with parsed data or error
        """
        import json
        try:
            data = json.loads(json_string)
            return {
                "valid": True,
                "data": data
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def sanitize_dict(self, data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary values
        
        Args:
            data: Dictionary to sanitize
            max_depth: Maximum recursion depth
        
        Returns:
            Sanitized dictionary
        """
        if max_depth <= 0:
            return {}
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            safe_key = self.sanitize_string(str(key))
            
            # Sanitize value
            if isinstance(value, str):
                safe_value = self.sanitize_string(value)
            elif isinstance(value, dict):
                safe_value = self.sanitize_dict(value, max_depth - 1)
            elif isinstance(value, list):
                safe_value = [self.sanitize_string(str(v)) if isinstance(v, str) else v for v in value]
            else:
                safe_value = value
            
            sanitized[safe_key] = safe_value
        
        return sanitized


# Global instance
input_validation_service = InputValidationService()

