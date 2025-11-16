"""
Unified cache manager with automatic fallback
Provides a single interface for Redis and memory caching
"""

import logging
from typing import Any, Optional, Dict
from .redis_cache import RedisCache
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)

# Global cache manager instance
_cache_manager: Optional['CacheManager'] = None


class CacheManager:
    """
    Unified cache manager with automatic fallback
    Tries Redis first, falls back to memory cache
    """
    
    def __init__(
        self,
        use_redis: bool = True,
        redis_config: Optional[Dict[str, Any]] = None,
        memory_max_size: int = 1000,
        memory_default_ttl: int = 3600
    ):
        """
        Initialize cache manager
        
        Args:
            use_redis: Whether to try Redis first
            redis_config: Redis configuration dictionary
            memory_max_size: Maximum size for memory cache
            memory_default_ttl: Default TTL for memory cache
        """
        self.redis_cache: Optional[RedisCache] = None
        self.memory_cache: MemoryCache = MemoryCache(
            max_size=memory_max_size,
            default_ttl=memory_default_ttl
        )
        self.use_redis = use_redis
        self._primary_cache: Optional[Any] = None
        
        # Initialize Redis if requested
        if use_redis:
            redis_config = redis_config or {}
            self.redis_cache = RedisCache(**redis_config)
            if self.redis_cache.is_available():
                self._primary_cache = self.redis_cache
                logger.info("Using Redis as primary cache")
            else:
                logger.info("Redis unavailable, using memory cache")
                self._primary_cache = self.memory_cache
        else:
            self._primary_cache = self.memory_cache
            logger.info("Using memory cache only")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        # Try primary cache first
        if self._primary_cache:
            value = self._primary_cache.get(key)
            if value is not None:
                return value
        
        # If using Redis and it failed, try memory cache
        if self.use_redis and self._primary_cache == self.redis_cache:
            return self.memory_cache.get(key)
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful
        """
        # Set in primary cache
        primary_success = False
        if self._primary_cache:
            primary_success = self._primary_cache.set(key, value, ttl)
        
        # Also set in memory cache as backup if using Redis
        if self.use_redis and self._primary_cache == self.redis_cache:
            self.memory_cache.set(key, value, ttl)
        
        return primary_success
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted
        """
        deleted = False
        
        # Delete from primary cache
        if self._primary_cache:
            deleted = self._primary_cache.delete(key)
        
        # Also delete from memory cache
        deleted = self.memory_cache.delete(key) or deleted
        
        return deleted
    
    def clear(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of items cleared
        """
        count = 0
        
        if self._primary_cache:
            count += self._primary_cache.clear()
        
        count += self.memory_cache.clear()
        
        return count
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        if self._primary_cache and self._primary_cache.exists(key):
            return True
        return self.memory_cache.exists(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get combined cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'primary_type': 'redis' if (self.use_redis and self._primary_cache == self.redis_cache) else 'memory',
            'redis_available': self.redis_cache.is_available() if self.redis_cache else False
        }
        
        # Get primary cache stats
        if self._primary_cache:
            primary_stats = self._primary_cache.get_stats()
            stats['primary'] = primary_stats
        
        # Get memory cache stats
        memory_stats = self.memory_cache.get_stats()
        stats['memory'] = memory_stats
        
        return stats
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """
        Get multiple values from cache
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary mapping keys to values
        """
        result = {}
        
        # Try primary cache first
        if self._primary_cache:
            result.update(self._primary_cache.get_many(keys))
        
        # Fill in missing from memory cache
        missing_keys = [k for k in keys if k not in result]
        if missing_keys:
            memory_results = self.memory_cache.get_many(missing_keys)
            result.update(memory_results)
        
        return result
    
    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> int:
        """
        Set multiple values in cache
        
        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds
            
        Returns:
            Number of items set
        """
        count = 0
        
        # Set in primary cache
        if self._primary_cache:
            count = self._primary_cache.set_many(mapping, ttl)
        
        # Also set in memory cache
        self.memory_cache.set_many(mapping, ttl)
        
        return count
    
    def warm_cache(self, items: Dict[str, Any], ttl: Optional[int] = None):
        """
        Warm cache with initial data
        
        Args:
            items: Dictionary of key-value pairs to preload
            ttl: Time-to-live in seconds
        """
        self.set_many(items, ttl)
        logger.info(f"Cache warmed with {len(items)} items")
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern
        Note: Pattern matching only works with Redis
        
        Args:
            pattern: Pattern to match (e.g., "user:*")
            
        Returns:
            Number of keys invalidated
        """
        count = 0
        
        if self.redis_cache and self.redis_cache.is_available():
            # Redis supports pattern matching
            redis_pattern = f"proposal_cache:{pattern}"
            count = self.redis_cache.clear(redis_pattern)
        
        # For memory cache, we'd need to iterate (not implemented for performance)
        # In practice, use specific keys or clear all
        
        return count


def get_cache_manager() -> CacheManager:
    """
    Get or create global cache manager instance
    
    Returns:
        CacheManager instance
    """
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = CacheManager()
    
    return _cache_manager

