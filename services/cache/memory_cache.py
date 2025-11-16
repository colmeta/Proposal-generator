"""
In-memory caching implementation using LRU cache
Fallback when Redis is not available
"""

import time
import threading
from typing import Any, Optional, Dict
from collections import OrderedDict
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class MemoryCache:
    """
    Thread-safe in-memory LRU cache with TTL support
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize memory cache
        
        Args:
            max_size: Maximum number of items in cache
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
    
    def _generate_key(self, key: str) -> str:
        """Generate a normalized cache key"""
        if isinstance(key, str):
            return key
        # Convert non-string keys to string
        return hashlib.md5(json.dumps(key, sort_keys=True).encode()).hexdigest()
    
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Check if cache item is expired"""
        if 'expires_at' not in item:
            return False
        return time.time() > item['expires_at']
    
    def _cleanup_expired(self):
        """Remove expired items from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if 'expires_at' in item and current_time > item['expires_at']
        ]
        for key in expired_keys:
            del self._cache[key]
            self._stats['evictions'] += 1
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            normalized_key = self._generate_key(key)
            
            if normalized_key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            item = self._cache[normalized_key]
            
            # Check expiration
            if self._is_expired(item):
                del self._cache[normalized_key]
                self._stats['misses'] += 1
                self._stats['evictions'] += 1
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(normalized_key)
            self._stats['hits'] += 1
            return item['value']
    
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
        with self._lock:
            normalized_key = self._generate_key(key)
            ttl = ttl if ttl is not None else self.default_ttl
            
            # Remove if exists
            if normalized_key in self._cache:
                del self._cache[normalized_key]
            
            # Check if we need to evict
            if len(self._cache) >= self.max_size:
                # Remove oldest item (LRU)
                self._cache.popitem(last=False)
                self._stats['evictions'] += 1
            
            # Add new item
            expires_at = time.time() + ttl if ttl > 0 else None
            self._cache[normalized_key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
            self._stats['sets'] += 1
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            normalized_key = self._generate_key(key)
            if normalized_key in self._cache:
                del self._cache[normalized_key]
                self._stats['deletes'] += 1
                return True
            return False
    
    def clear(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of items cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists and is not expired
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is valid
        """
        with self._lock:
            normalized_key = self._generate_key(key)
            if normalized_key not in self._cache:
                return False
            return not self._is_expired(self._cache[normalized_key])
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            self._cleanup_expired()
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'sets': self._stats['sets'],
                'deletes': self._stats['deletes'],
                'evictions': self._stats['evictions'],
                'hit_rate': round(hit_rate, 2),
                'size': len(self._cache),
                'max_size': self.max_size
            }
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """
        Get multiple values from cache
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary mapping keys to values (only includes found keys)
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
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
        for key, value in mapping.items():
            if self.set(key, value, ttl):
                count += 1
        return count

