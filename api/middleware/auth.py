"""Authentication middleware for API key, OAuth 2.0, and JWT"""
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable
from functools import wraps
from flask import request, g, jsonify, current_app
import jwt
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Authentication middleware supporting multiple auth methods"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.api_keys: Dict[str, Dict] = {}  # key -> {user_id, permissions, roles}
        self.oauth_clients: Dict[str, Dict] = {}  # client_id -> {client_secret, redirect_uri}
        self.token_blacklist: set = set()
    
    def generate_api_key(self, user_id: int, permissions: List[str] = None, roles: List[str] = None) -> str:
        """Generate a new API key for a user"""
        api_key = secrets.token_urlsafe(32)
        self.api_keys[api_key] = {
            'user_id': user_id,
            'permissions': permissions or [],
            'roles': roles or ['user'],
            'created_at': datetime.utcnow()
        }
        logger.info(f"API key generated for user {user_id}")
        return api_key
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            logger.info(f"API key revoked: {api_key[:8]}...")
            return True
        return False
    
    def register_oauth_client(self, client_id: str, client_secret: str, redirect_uri: str) -> bool:
        """Register an OAuth 2.0 client"""
        self.oauth_clients[client_id] = {
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        logger.info(f"OAuth client registered: {client_id}")
        return True
    
    def generate_jwt_token(
        self,
        user_id: int,
        roles: List[str] = None,
        permissions: List[str] = None,
        expires_in: int = 3600
    ) -> str:
        """Generate a JWT token"""
        payload = {
            'user_id': user_id,
            'roles': roles or ['user'],
            'permissions': permissions or [],
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def generate_refresh_token(self, user_id: int, expires_in: int = 86400 * 7) -> str:
        """Generate a refresh token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify and decode a JWT token"""
        if token in self.token_blacklist:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def blacklist_token(self, token: str):
        """Add token to blacklist (for logout)"""
        self.token_blacklist.add(token)
    
    def authenticate_request(self) -> Optional[Dict]:
        """Authenticate request using various methods"""
        # Try API key authentication
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if api_key and api_key in self.api_keys:
            key_data = self.api_keys[api_key]
            return {
                'user_id': key_data['user_id'],
                'roles': key_data['roles'],
                'permissions': key_data['permissions'],
                'auth_method': 'api_key'
            }
        
        # Try Bearer token (JWT)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            payload = self.verify_jwt_token(token)
            if payload:
                return {
                    'user_id': payload['user_id'],
                    'roles': payload.get('roles', ['user']),
                    'permissions': payload.get('permissions', []),
                    'auth_method': 'jwt'
                }
        
        # Try OAuth 2.0 access token
        if auth_header.startswith('OAuth '):
            token = auth_header[6:]
            payload = self.verify_jwt_token(token)
            if payload:
                return {
                    'user_id': payload['user_id'],
                    'roles': payload.get('roles', ['user']),
                    'permissions': payload.get('permissions', []),
                    'auth_method': 'oauth'
                }
        
        return None
    
    def has_permission(self, user_data: Dict, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in user_data.get('permissions', [])
    
    def has_role(self, user_data: Dict, role: str) -> bool:
        """Check if user has a specific role"""
        return role in user_data.get('roles', [])


# Global auth middleware instance
_auth_middleware: Optional[AuthMiddleware] = None


def init_auth(secret_key: str) -> AuthMiddleware:
    """Initialize authentication middleware"""
    global _auth_middleware
    _auth_middleware = AuthMiddleware(secret_key)
    return _auth_middleware


def get_auth() -> AuthMiddleware:
    """Get the global auth middleware instance"""
    global _auth_middleware
    if _auth_middleware is None:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key-change-in-production')
        _auth_middleware = AuthMiddleware(secret_key)
    return _auth_middleware


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = get_auth()
        user_data = auth.authenticate_request()
        
        if not user_data:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required'
            }), 401
        
        g.user_id = user_data['user_id']
        g.user_roles = user_data['roles']
        g.user_permissions = user_data['permissions']
        g.auth_method = user_data['auth_method']
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*roles: str):
    """Decorator to require specific role(s)"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user_roles = getattr(g, 'user_roles', [])
            
            if not any(role in user_roles for role in roles):
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Required role: {", ".join(roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_permission(*permissions: str):
    """Decorator to require specific permission(s)"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user_permissions = getattr(g, 'user_permissions', [])
            
            if not any(perm in user_permissions for perm in permissions):
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Required permission: {", ".join(permissions)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def setup_auth_middleware(app):
    """Setup authentication middleware for Flask app"""
    secret_key = app.config.get('SECRET_KEY', 'default-secret-key-change-in-production')
    init_auth(secret_key)
    
    @app.before_request
    def authenticate():
        """Authenticate request and set user context"""
        auth = get_auth()
        user_data = auth.authenticate_request()
        
        if user_data:
            g.user_id = user_data['user_id']
            g.user_roles = user_data['roles']
            g.user_permissions = user_data['permissions']
            g.auth_method = user_data['auth_method']
    
    logger.info("Authentication middleware configured")

