"""
Authentication Service
Password hashing, session management, token validation
"""

import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError
from jose import jwt as jose_jwt
import logging

logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Authentication service for user authentication and session management
    """
    
    def __init__(self):
        """Initialize authentication service"""
        self.secret_key = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.token_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours
        self.sessions: Dict[str, Dict[str, Any]] = {}  # In-memory session store
        logger.info("AuthenticationService initialized")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against a hash
        
        Args:
            password: Plain text password
            hashed: Hashed password
        
        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Optional expiration time
        
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jose_jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jose_jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """
        Create a user session
        
        Args:
            user_id: User ID
            user_data: User data to store in session
        
        Returns:
            Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        logger.info(f"Session created for user {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data or None
        """
        session = self.sessions.get(session_id)
        if session:
            session["last_activity"] = datetime.utcnow()
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session ID
        
        Returns:
            True if session was deleted
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session {session_id} deleted")
            return True
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """
        Clean up expired sessions
        
        Args:
            max_age_hours: Maximum session age in hours
        """
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self.sessions.items()
            if (now - session["last_activity"]).total_seconds() > max_age_hours * 3600
        ]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
    
    def authenticate_user(self, username: str, password: str, user_store: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user
        
        Args:
            username: Username
            password: Plain text password
            user_store: User store (dict of username -> user data with 'password_hash')
        
        Returns:
            User data if authenticated, None otherwise
        """
        user = user_store.get(username)
        if not user:
            logger.warning(f"Authentication failed: user {username} not found")
            return None
        
        if not self.verify_password(password, user.get("password_hash", "")):
            logger.warning(f"Authentication failed: invalid password for {username}")
            return None
        
        logger.info(f"User {username} authenticated successfully")
        return user


# Global instance
authentication_service = AuthenticationService()

