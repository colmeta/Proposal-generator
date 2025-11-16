"""Rate limiting middleware using token bucket algorithm"""
import time
import logging
from typing import Dict, Optional, Tuple
from collections import defaultdict
from flask import request, g, jsonify, current_app
from functools import wraps
from threading import Lock

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket implementation for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket"""
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_remaining(self) -> int:
        """Get remaining tokens"""
        with self.lock:
            self._refill()
            return int(self.tokens)
    
    def get_reset_time(self) -> float:
        """Get time until bucket is full"""
        with self.lock:
            if self.tokens >= self.capacity:
                return 0
            tokens_needed = self.capacity - self.tokens
            return tokens_needed / self.refill_rate


class RateLimiter:
    """Rate limiter with per-user and per-IP limits"""
    
    def __init__(self):
        self.user_buckets: Dict[str, TokenBucket] = {}
        self.ip_buckets: Dict[str, TokenBucket] = {}
        self.lock = Lock()
        
        # Default limits (can be configured)
        self.default_user_limit = (100, 1.0)  # 100 requests, 1 per second
        self.default_ip_limit = (200, 2.0)  # 200 requests, 2 per second
        
        # Per-endpoint limits
        self.endpoint_limits: Dict[str, Tuple[int, float]] = {}
    
    def set_user_limit(self, user_id: str, limit: int, refill_rate: float):
        """Set rate limit for a specific user"""
        with self.lock:
            self.user_buckets[user_id] = TokenBucket(limit, refill_rate)
    
    def set_ip_limit(self, ip: str, limit: int, refill_rate: float):
        """Set rate limit for a specific IP"""
        with self.lock:
            self.ip_buckets[ip] = TokenBucket(limit, refill_rate)
    
    def set_endpoint_limit(self, endpoint: str, limit: int, refill_rate: float):
        """Set rate limit for a specific endpoint"""
        self.endpoint_limits[endpoint] = (limit, refill_rate)
    
    def _get_user_bucket(self, user_id: Optional[str]) -> Optional[TokenBucket]:
        """Get or create token bucket for user"""
        if not user_id:
            return None
        
        if user_id not in self.user_buckets:
            limit, refill = self.default_user_limit
            self.user_buckets[user_id] = TokenBucket(limit, refill)
        
        return self.user_buckets[user_id]
    
    def _get_ip_bucket(self, ip: str) -> TokenBucket:
        """Get or create token bucket for IP"""
        if ip not in self.ip_buckets:
            limit, refill = self.default_ip_limit
            self.ip_buckets[ip] = TokenBucket(limit, refill)
        
        return self.ip_buckets[ip]
    
    def check_rate_limit(
        self,
        user_id: Optional[str] = None,
        ip: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limits
        
        Returns:
            (allowed, headers_dict)
        """
        if ip is None:
            ip = request.remote_addr or 'unknown'
        
        headers = {}
        allowed = True
        
        # Check endpoint-specific limit
        if endpoint and endpoint in self.endpoint_limits:
            limit, refill = self.endpoint_limits[endpoint]
            bucket_key = f"{endpoint}:{ip}:{user_id or 'anonymous'}"
            if bucket_key not in self.ip_buckets:
                with self.lock:
                    self.ip_buckets[bucket_key] = TokenBucket(limit, refill)
            bucket = self.ip_buckets[bucket_key]
            
            if not bucket.consume():
                allowed = False
                headers['X-RateLimit-Limit'] = str(limit)
                headers['X-RateLimit-Remaining'] = '0'
                headers['X-RateLimit-Reset'] = str(int(time.time() + bucket.get_reset_time()))
                return False, headers
        
        # Check user limit
        if user_id:
            user_bucket = self._get_user_bucket(user_id)
            if user_bucket and not user_bucket.consume():
                allowed = False
                limit, _ = self.default_user_limit
                headers['X-RateLimit-Limit'] = str(limit)
                headers['X-RateLimit-Remaining'] = '0'
                headers['X-RateLimit-Reset'] = str(int(time.time() + user_bucket.get_reset_time()))
                return False, headers
        
        # Check IP limit
        ip_bucket = self._get_ip_bucket(ip)
        if not ip_bucket.consume():
            allowed = False
            limit, _ = self.default_ip_limit
            headers['X-RateLimit-Limit'] = str(limit)
            headers['X-RateLimit-Remaining'] = '0'
            headers['X-RateLimit-Reset'] = str(int(time.time() + ip_bucket.get_reset_time()))
            return False, headers
        
        # Set remaining headers
        if user_id and user_id in self.user_buckets:
            user_bucket = self.user_buckets[user_id]
            limit, _ = self.default_user_limit
            headers['X-RateLimit-Limit'] = str(limit)
            headers['X-RateLimit-Remaining'] = str(user_bucket.get_remaining())
            headers['X-RateLimit-Reset'] = str(int(time.time() + user_bucket.get_reset_time()))
        
        if ip in self.ip_buckets:
            ip_bucket = self.ip_buckets[ip]
            limit, _ = self.default_ip_limit
            if 'X-RateLimit-Limit' not in headers:
                headers['X-RateLimit-Limit'] = str(limit)
            if 'X-RateLimit-Remaining' not in headers:
                headers['X-RateLimit-Remaining'] = str(ip_bucket.get_remaining())
            if 'X-RateLimit-Reset' not in headers:
                headers['X-RateLimit-Reset'] = str(int(time.time() + ip_bucket.get_reset_time()))
        
        return allowed, headers


# Global rate limiter instance
_rate_limiter = RateLimiter()


def setup_rate_limiter(app, config: Optional[Dict] = None):
    """Setup rate limiter for Flask app"""
    global _rate_limiter
    
    if config:
        if 'default_user_limit' in config:
            _rate_limiter.default_user_limit = tuple(config['default_user_limit'])
        if 'default_ip_limit' in config:
            _rate_limiter.default_ip_limit = tuple(config['default_ip_limit'])
        if 'endpoint_limits' in config:
            for endpoint, (limit, refill) in config['endpoint_limits'].items():
                _rate_limiter.set_endpoint_limit(endpoint, limit, refill)
    
    @app.before_request
    def rate_limit_check():
        """Check rate limits before each request"""
        # Skip rate limiting for certain endpoints
        if request.endpoint in ['static', 'docs', 'swagger']:
            return
        
        user_id = getattr(g, 'user_id', None)
        ip = request.remote_addr
        endpoint = request.endpoint
        
        allowed, headers = _rate_limiter.check_rate_limit(
            user_id=user_id,
            ip=ip,
            endpoint=endpoint
        )
        
        # Add headers to response
        for key, value in headers.items():
            g.setdefault('rate_limit_headers', {})[key] = value
        
        if not allowed:
            response = jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': headers.get('X-RateLimit-Reset', 60)
            })
            response.status_code = 429
            
            # Add rate limit headers
            for key, value in headers.items():
                response.headers[key] = value
            
            return response
    
    @app.after_request
    def add_rate_limit_headers(response):
        """Add rate limit headers to response"""
        if hasattr(g, 'rate_limit_headers'):
            for key, value in g.rate_limit_headers.items():
                response.headers[key] = value
        return response
    
    logger.info("Rate limiter middleware configured")


def rate_limit(limit: int, per: float = 1.0):
    """Decorator for endpoint-specific rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint = f"{request.endpoint}:{request.method}"
            _rate_limiter.set_endpoint_limit(endpoint, limit, limit / per)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

