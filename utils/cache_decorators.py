"""
Cache decorators for function and method result caching
"""

import hashlib
import json
import functools
import logging
from typing import Any, Callable, Optional, Dict
from services.cache import get_cache_manager

logger = logging.getLogger(__name__)


def cached(ttl: int = 3600, key_prefix: str = "", include_args: bool = True, 
          include_kwargs: bool = True):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
        include_args: Whether to include args in cache key
        include_kwargs: Whether to include kwargs in cache key
    
    Usage:
        @cached(ttl=300, key_prefix="my_function")
        def expensive_function(arg1, arg2):
            return expensive_computation(arg1, arg2)
    """
    def decorator(func: Callable) -> Callable:
        cache = get_cache_manager()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix or func.__name__]
            
            if include_args:
                # Serialize args (handle non-serializable types)
                try:
                    args_str = json.dumps(args, sort_keys=True, default=str)
                    cache_key_parts.append(f"args:{hashlib.md5(args_str.encode()).hexdigest()}")
                except (TypeError, ValueError):
                    cache_key_parts.append(f"args:{hash(args)}")
            
            if include_kwargs:
                # Serialize kwargs
                try:
                    kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
                    cache_key_parts.append(f"kwargs:{hashlib.md5(kwargs_str.encode()).hexdigest()}")
                except (TypeError, ValueError):
                    cache_key_parts.append(f"kwargs:{hash(frozenset(kwargs.items()))}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        # Add cache invalidation method
        def invalidate(*args, **kwargs):
            """Invalidate cache for specific arguments"""
            cache_key_parts = [key_prefix or func.__name__]
            
            if include_args:
                try:
                    args_str = json.dumps(args, sort_keys=True, default=str)
                    cache_key_parts.append(f"args:{hashlib.md5(args_str.encode()).hexdigest()}")
                except (TypeError, ValueError):
                    cache_key_parts.append(f"args:{hash(args)}")
            
            if include_kwargs:
                try:
                    kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
                    cache_key_parts.append(f"kwargs:{hashlib.md5(kwargs_str.encode()).hexdigest()}")
                except (TypeError, ValueError):
                    cache_key_parts.append(f"kwargs:{hash(frozenset(kwargs.items()))}")
            
            cache_key = ":".join(cache_key_parts)
            cache.delete(cache_key)
            logger.debug(f"Invalidated cache for {func.__name__}")
        
        wrapper.invalidate = invalidate
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


def cached_method(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache method results (includes self in key)
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
    
    Usage:
        class MyClass:
            @cached_method(ttl=300)
            def expensive_method(self, arg1):
                return expensive_computation(arg1)
    """
    def decorator(func: Callable) -> Callable:
        cache = get_cache_manager()
        
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key including self
            cache_key_parts = [
                key_prefix or f"{self.__class__.__name__}.{func.__name__}",
                f"instance:{id(self)}"
            ]
            
            # Include args
            try:
                args_str = json.dumps(args, sort_keys=True, default=str)
                cache_key_parts.append(f"args:{hashlib.md5(args_str.encode()).hexdigest()}")
            except (TypeError, ValueError):
                cache_key_parts.append(f"args:{hash(args)}")
            
            # Include kwargs
            try:
                kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
                cache_key_parts.append(f"kwargs:{hashlib.md5(kwargs_str.encode()).hexdigest()}")
            except (TypeError, ValueError):
                cache_key_parts.append(f"kwargs:{hash(frozenset(kwargs.items()))}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute method
            result = func(self, *args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        # Add cache invalidation method
        def invalidate(self, *args, **kwargs):
            """Invalidate cache for specific arguments"""
            cache_key_parts = [
                key_prefix or f"{self.__class__.__name__}.{func.__name__}",
                f"instance:{id(self)}"
            ]
            
            if args:
                try:
                    args_str = json.dumps(args, sort_keys=True, default=str)
                    cache_key_parts.append(f"args:{hashlib.md5(args_str.encode()).hexdigest()}")
                except (TypeError, ValueError):
                    cache_key_parts.append(f"args:{hash(args)}")
            
            if kwargs:
                try:
                    kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
                    cache_key_parts.append(f"kwargs:{hashlib.md5(kwargs_str.encode()).hexdigest()}")
                except (TypeError, ValueError):
                    cache_key_parts.append(f"kwargs:{hash(frozenset(kwargs.items()))}")
            
            cache_key = ":".join(cache_key_parts)
            cache.delete(cache_key)
            logger.debug(f"Invalidated cache for {func.__name__}")
        
        wrapper.invalidate = invalidate
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


async def async_cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache async function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
    
    Usage:
        @async_cached(ttl=300)
        async def expensive_async_function(arg1):
            return await expensive_computation(arg1)
    """
    def decorator(func: Callable) -> Callable:
        cache = get_cache_manager()
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix or func.__name__]
            
            try:
                args_str = json.dumps(args, sort_keys=True, default=str)
                cache_key_parts.append(f"args:{hashlib.md5(args_str.encode()).hexdigest()}")
            except (TypeError, ValueError):
                cache_key_parts.append(f"args:{hash(args)}")
            
            try:
                kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
                cache_key_parts.append(f"kwargs:{hashlib.md5(kwargs_str.encode()).hexdigest()}")
            except (TypeError, ValueError):
                cache_key_parts.append(f"kwargs:{hash(frozenset(kwargs.items()))}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute async function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


def cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Cache key string
    
    Usage:
        key = cache_key("user", user_id=123)
        value = cache.get(key)
    """
    key_parts = []
    
    for arg in args:
        try:
            key_parts.append(json.dumps(arg, sort_keys=True, default=str))
        except (TypeError, ValueError):
            key_parts.append(str(arg))
    
    if kwargs:
        try:
            key_parts.append(json.dumps(kwargs, sort_keys=True, default=str))
        except (TypeError, ValueError):
            key_parts.append(str(sorted(kwargs.items())))
    
    key_string = ":".join(key_parts)
    return hashlib.sha256(key_string.encode()).hexdigest()

