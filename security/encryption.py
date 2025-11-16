"""
Data Encryption Service
Field-level encryption, encryption at rest, key management
"""

import os
import base64
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Encryption service for data at rest and field-level encryption
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption service
        
        Args:
            key: Encryption key (if None, generates from environment or creates new)
        """
        self.key = key or self._get_or_create_key()
        self.cipher = Fernet(self.key)
        logger.info("EncryptionService initialized")
    
    def _get_or_create_key(self) -> bytes:
        """Get encryption key from environment or create new one"""
        # Try to get from environment
        key_str = os.getenv("ENCRYPTION_KEY")
        if key_str:
            try:
                return base64.urlsafe_b64decode(key_str.encode())
            except Exception as e:
                logger.warning(f"Failed to decode ENCRYPTION_KEY: {e}")
        
        # Generate new key from password
        password = os.getenv("ENCRYPTION_PASSWORD", "default-password-change-in-production")
        salt = os.getenv("ENCRYPTION_SALT", "default-salt-change-in-production").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        logger.warning("Using generated encryption key. Set ENCRYPTION_KEY in production!")
        return key
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data
        
        Args:
            data: Data to encrypt (string or bytes)
        
        Returns:
            Encrypted data as base64 string
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            encrypted = self.cipher.encrypt(data)
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data
        
        Args:
            encrypted_data: Encrypted data as base64 string
        
        Returns:
            Decrypted data as string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_field(self, value: Optional[str]) -> Optional[str]:
        """
        Encrypt a field value (handles None)
        
        Args:
            value: Field value to encrypt
        
        Returns:
            Encrypted value or None
        """
        if value is None:
            return None
        return self.encrypt(value)
    
    def decrypt_field(self, encrypted_value: Optional[str]) -> Optional[str]:
        """
        Decrypt a field value (handles None)
        
        Args:
            encrypted_value: Encrypted field value
        
        Returns:
            Decrypted value or None
        """
        if encrypted_value is None:
            return None
        return self.decrypt(encrypted_value)
    
    def generate_key(self) -> str:
        """
        Generate a new encryption key
        
        Returns:
            Base64-encoded key string
        """
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode('utf-8')
    
    def rotate_key(self, old_key: bytes, new_key: bytes) -> callable:
        """
        Create a key rotation function
        
        Args:
            old_key: Old encryption key
            new_key: New encryption key
        
        Returns:
            Function to re-encrypt data with new key
        """
        old_cipher = Fernet(old_key)
        new_cipher = Fernet(new_key)
        
        def re_encrypt(encrypted_data: str) -> str:
            """Re-encrypt data with new key"""
            try:
                # Decrypt with old key
                encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
                decrypted = old_cipher.decrypt(encrypted_bytes)
                # Encrypt with new key
                re_encrypted = new_cipher.encrypt(decrypted)
                return base64.urlsafe_b64encode(re_encrypted).decode('utf-8')
            except Exception as e:
                logger.error(f"Key rotation failed: {e}")
                raise
        
        return re_encrypt


# Global instance
encryption_service = EncryptionService()

