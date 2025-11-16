"""
Redis caching implementation
Optional upgrade for distributed caching
"""

import os
import json
import time
import logging
from typing import Any, Optional, Dict
import hashlib

logger = logging.getLogger(__name__)

# Try to import redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available. Install with: pip install redis")


class RedisCache:
    """
    Redis caching layer
    Falls back gracefully if Redis is not available
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 3600,
        decode_responses: bool = True
    ):
        """
        Initialize Redis cache
        
        Args:
            host: Redis host (defaults to REDIS_HOST env var or localhost)
            port: Redis port
            db: Redis database number
            password: Redis password
            default_ttl: Default time-to-live in seconds
            decode_responses: Whether to decode responses as strings
        """
        self.default_ttl = default_ttl
        self._client: Optional[Any] = None
        self._available = False
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        
        if not REDIS_AVAILABLE:
            logger.warning("Redis library not installed. Redis cache unavailable.")
            return
        
        # Get connection parameters
        host = host or os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', port))
        db = int(os.getenv('REDIS_DB', db))
        password = password or os.getenv('REDIS_PASSWORD')
        
        try:
            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self._client.ping()
            self._available = True
            logger.info(f"Redis cache connected to {host}:{port}/{db}")
        except Exception as e:
            logger.warning(f"Redis cache unavailable: {e}. Falling back to memory cache.")
            self._available = False
            if self._client:
                try:
                    self._client.close()
                except:
                    pass
                self._client = None
    
    def _generate_key(self, key: str) -> str:
        """Generate a normalized cache key with prefix"""
        prefix = "proposal_cache:"
        if isinstance(key, str):
            return f"{prefix}{key}"
        # Convert non-string keys to string
        return f"{prefix}{hashlib.md5(json.dumps(key, sort_keys=True).encode()).hexdigest()}"
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage"""
        try:
            return json.dumps(value)
        except (TypeError, ValueError):
            # Fallback for non-serializable types
            return str(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self._available or not self._client:
            return False
        try:
            self._client.ping()
            return True
        except:
            self._available = False
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.is_available():
            self._stats['misses'] += 1
            return None
        
        try:
            normalized_key = self._generate_key(key)
            value = self._client.get(normalized_key)
            
            if value is None:
                self._stats['misses'] += 1
                return None
            
            self._stats['hits'] += 1
            return self._deserialize(value)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self._stats['misses'] += 1
            self._stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful
        """
        if not self.is_available():
            return False
        
        try:
            normalized_key = self._generate_key(key)
            serialized_value = self._serialize(value)
            ttl = ttl if ttl is not None else self.default_ttl
            
            if ttl > 0:
                self._client.setex(normalized_key, ttl, serialized_value)
            else:
                self._client.set(normalized_key, serialized_value)
            
            self._stats['sets'] += 1
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            self._stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted
        """
        if not self.is_available():
            return False
        
        try:
            normalized_key = self._generate_key(key)
            result = self._client.delete(normalized_key)
            if result:
                self._stats['deletes'] += 1
            return bool(result)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            self._stats['errors'] += 1
            return False
    
    def clear(self, pattern: str = "proposal_cache:*") -> int:
        """
        Clear cache entries matching pattern
        
        Args:
            pattern: Redis key pattern (default: all proposal cache keys)
            
        Returns:
            Number of keys deleted
        """
        if not self.is_available():
            return 0
        
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            self._stats['errors'] += 1
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        if not self.is_available():
            return False
        
        try:
            normalized_key = self._generate_key(key)
            return bool(self._client.exists(normalized_key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'sets': self._stats['sets'],
            'deletes': self._stats['deletes'],
            'errors': self._stats['errors'],
            'available': self.is_available()
        }
        
        if self.is_available():
            total_requests = stats['hits'] + stats['misses']
            stats['hit_rate'] = round((stats['hits'] / total_requests * 100) if total_requests > 0 else 0, 2)
            
            try:
                info = self._client.info('memory')
                stats['redis_memory_used'] = info.get('used_memory_human', 'N/A')
            except:
                pass
        
        return stats
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """
        Get multiple values from cache
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary mapping keys to values
        """
        if not self.is_available():
            return {}
        
        try:
            normalized_keys = [self._generate_key(key) for key in keys]
            values = self._client.mget(normalized_keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)
            return result
        except Exception as e:
            logger.error(f"Redis get_many error: {e}")
            return {}
    
    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> int:
        """
        Set multiple values in cache
        
        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds
            
        Returns:
            Number of items set
        """
        if not self.is_available():
            return 0
        
        try:
            ttl = ttl if ttl is not None else self.default_ttl
            pipe = self._client.pipeline()
            
            for key, value in mapping.items():
                normalized_key = self._generate_key(key)
                serialized_value = self._serialize(value)
                if ttl > 0:
                    pipe.setex(normalized_key, ttl, serialized_value)
                else:
                    pipe.set(normalized_key, serialized_value)
            
            pipe.execute()
            return len(mapping)
        except Exception as e:
            logger.error(f"Redis set_many error: {e}")
            return 0

