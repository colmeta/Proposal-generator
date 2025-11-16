"""
API response caching service
Caches API responses with ETag support and conditional requests
"""

import hashlib
import json
import gzip
import logging
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
from flask import Request, Response, make_response

from services.cache import get_cache_manager

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    API response caching with ETag and compression support
    """
    
    def __init__(self, default_ttl: int = 300, enable_compression: bool = True):
        """
        Initialize response cache
        
        Args:
            default_ttl: Default cache TTL in seconds (5 minutes)
            enable_compression: Whether to compress cached responses
        """
        self.default_ttl = default_ttl
        self.enable_compression = enable_compression
        self.cache = get_cache_manager()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0,
            'not_modified': 0
        }
    
    def _generate_cache_key(self, request: Request, include_query: bool = True) -> str:
        """
        Generate cache key from request
        
        Args:
            request: Flask request object
            include_query: Whether to include query parameters in key
            
        Returns:
            Cache key string
        """
        # Build key components
        key_parts = [
            request.method,
            request.path
        ]
        
        if include_query and request.args:
            # Sort query params for consistent keys
            sorted_params = sorted(request.args.items())
            key_parts.append(json.dumps(sorted_params, sort_keys=True))
        
        # Include headers that affect response (optional)
        # For now, keep it simple
        
        key_string = '|'.join(str(p) for p in key_parts)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return f"api_cache:{key_hash}"
    
    def _generate_etag(self, content: Any) -> str:
        """
        Generate ETag from content
        
        Args:
            content: Response content
            
        Returns:
            ETag string
        """
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        
        etag_hash = hashlib.md5(content_str.encode()).hexdigest()
        return f'"{etag_hash}"'
    
    def _compress_content(self, content: str) -> bytes:
        """
        Compress content using gzip
        
        Args:
            content: Content to compress
            
        Returns:
            Compressed bytes
        """
        return gzip.compress(content.encode('utf-8'))
    
    def _decompress_content(self, compressed: bytes) -> str:
        """
        Decompress content
        
        Args:
            compressed: Compressed bytes
            
        Returns:
            Decompressed string
        """
        return gzip.decompress(compressed).decode('utf-8')
    
    def get(self, request: Request) -> Optional[Tuple[Dict[str, Any], str]]:
        """
        Get cached response
        
        Args:
            request: Flask request object
            
        Returns:
            Tuple of (cached_data, etag) or None
        """
        # Only cache GET requests
        if request.method != 'GET':
            return None
        
        cache_key = self._generate_cache_key(request)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            # Check ETag match (conditional request)
            if_none_match = request.headers.get('If-None-Match')
            if if_none_match and if_none_match == cached_data.get('etag'):
                self._stats['not_modified'] += 1
                return None  # Signal 304 Not Modified
            
            self._stats['hits'] += 1
            return cached_data, cached_data.get('etag', '')
        
        self._stats['misses'] += 1
        return None
    
    def set(self, request: Request, response_data: Any, ttl: Optional[int] = None,
            etag: Optional[str] = None) -> bool:
        """
        Cache API response
        
        Args:
            request: Flask request object
            response_data: Response data to cache
            ttl: Time-to-live in seconds
            etag: Optional ETag (generated if not provided)
            
        Returns:
            True if cached successfully
        """
        # Only cache GET requests
        if request.method != 'GET':
            return False
        
        cache_key = self._generate_cache_key(request)
        
        # Serialize response data
        if isinstance(response_data, Response):
            # Extract data from Flask Response
            try:
                data = response_data.get_json() if response_data.is_json else response_data.data.decode('utf-8')
            except:
                data = str(response_data.data)
        else:
            data = response_data
        
        # Generate ETag
        if etag is None:
            etag = self._generate_etag(data)
        
        # Prepare cache entry
        cache_entry = {
            'data': data,
            'etag': etag,
            'content_type': 'application/json',
            'cached_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=ttl or self.default_ttl)).isoformat()
        }
        
        # Compress if enabled
        if self.enable_compression:
            try:
                data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
                cache_entry['compressed'] = True
                cache_entry['data'] = self._compress_content(data_str)
            except Exception as e:
                logger.warning(f"Failed to compress cache entry: {e}")
                cache_entry['compressed'] = False
        
        ttl = ttl if ttl is not None else self.default_ttl
        success = self.cache.set(cache_key, cache_entry, ttl)
        
        if success:
            self._stats['saves'] += 1
        
        return success
    
    def make_cached_response(self, cached_data: Dict[str, Any], etag: str) -> Response:
        """
        Create Flask response from cached data
        
        Args:
            cached_data: Cached response data
            etag: ETag value
            
        Returns:
            Flask Response object
        """
        data = cached_data.get('data')
        
        # Decompress if needed
        if cached_data.get('compressed'):
            try:
                data = self._decompress_content(data)
                data = json.loads(data)
            except Exception as e:
                logger.error(f"Failed to decompress cached data: {e}")
                return make_response({'error': 'Cache corruption'}, 500)
        
        # Create response
        response = make_response(data)
        response.headers['ETag'] = etag
        response.headers['Cache-Control'] = f'public, max-age={self.default_ttl}'
        response.headers['X-Cache'] = 'HIT'
        
        return response
    
    def make_not_modified_response(self, etag: str) -> Response:
        """
        Create 304 Not Modified response
        
        Args:
            etag: ETag value
            
        Returns:
            Flask Response with 304 status
        """
        response = make_response('', 304)
        response.headers['ETag'] = etag
        response.headers['X-Cache'] = 'HIT'
        return response
    
    def invalidate(self, path_pattern: Optional[str] = None):
        """
        Invalidate cached responses
        
        Args:
            path_pattern: Path pattern to match (e.g., "/api/jobs/*")
        """
        if path_pattern:
            # Pattern-based invalidation
            pattern = f"api_cache:{path_pattern}"
            count = self.cache.invalidate_pattern(pattern)
            logger.info(f"Invalidated {count} API cache entries matching {path_pattern}")
        else:
            # Clear all API cache
            pattern = "api_cache:*"
            count = self.cache.invalidate_pattern(pattern)
            logger.info(f"Invalidated {count} API cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'saves': self._stats['saves'],
            'not_modified': self._stats['not_modified'],
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }


# Global response cache instance
_response_cache: Optional[ResponseCache] = None


def get_response_cache() -> ResponseCache:
    """Get or create global response cache instance"""
    global _response_cache
    if _response_cache is None:
        _response_cache = ResponseCache()
    return _response_cache


def cache_response(ttl: Optional[int] = None):
    """
    Decorator for caching Flask route responses
    
    Usage:
        @app.route('/api/data')
        @cache_response(ttl=300)
        def get_data():
            return jsonify({'data': 'value'})
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            cache = get_response_cache()
            
            # Try to get from cache
            cached = cache.get(request)
            if cached:
                cached_data, etag = cached
                return cache.make_cached_response(cached_data, etag)
            
            # Execute function
            response = func(*args, **kwargs)
            
            # Cache response
            cache.set(request, response, ttl=ttl)
            
            # Add cache headers
            if isinstance(response, Response):
                response.headers['X-Cache'] = 'MISS'
            else:
                response = make_response(response)
                response.headers['X-Cache'] = 'MISS'
            
            return response
        return wrapper
    return decorator

