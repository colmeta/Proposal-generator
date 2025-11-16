"""
LLM response caching service
Caches LLM responses to reduce API costs and improve response times
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

from services.cache import get_cache_manager
from config.llm_config import LLMProvider

logger = logging.getLogger(__name__)


class LLMCache:
    """
    LLM response caching with similarity-based lookup
    """
    
    def __init__(self, similarity_threshold: float = 0.95, default_ttl: int = 86400):
        """
        Initialize LLM cache
        
        Args:
            similarity_threshold: Similarity threshold for cache hits (0-1)
            default_ttl: Default cache TTL in seconds (24 hours)
        """
        self.similarity_threshold = similarity_threshold
        self.default_ttl = default_ttl
        self.cache = get_cache_manager()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0,
            'cost_saved': 0.0  # Estimated cost savings in USD
        }
    
    def _generate_cache_key(self, prompt: str, provider: Optional[str] = None, 
                           model: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Generate cache key from prompt and parameters
        
        Args:
            prompt: LLM prompt
            provider: LLM provider name
            model: Model name
            temperature: Temperature setting
            
        Returns:
            Cache key string
        """
        # Normalize prompt (lowercase, strip whitespace)
        normalized_prompt = prompt.lower().strip()
        
        # Create key components
        key_data = {
            'prompt': normalized_prompt,
            'provider': provider or 'default',
            'model': model or 'default',
            'temperature': round(temperature, 2)  # Round to avoid float precision issues
        }
        
        # Generate hash
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return f"llm_cache:{key_hash}"
    
    def _generate_similarity_key(self, prompt: str) -> str:
        """
        Generate a key for similarity lookup (simplified)
        Uses first 100 chars and length for quick filtering
        
        Args:
            prompt: LLM prompt
            
        Returns:
            Similarity key
        """
        normalized = prompt.lower().strip()
        prompt_hash = hashlib.md5(normalized.encode()).hexdigest()
        return f"llm_similarity:{prompt_hash}"
    
    def _simple_similarity(self, prompt1: str, prompt2: str) -> float:
        """
        Simple similarity calculation using word overlap
        For production, consider using sentence transformers
        
        Args:
            prompt1: First prompt
            prompt2: Second prompt
            
        Returns:
            Similarity score (0-1)
        """
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get(self, prompt: str, provider: Optional[str] = None, 
            model: Optional[str] = None, temperature: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        Get cached LLM response
        
        Args:
            prompt: LLM prompt
            provider: LLM provider name
            model: Model name
            temperature: Temperature setting
            
        Returns:
            Cached response dict or None
        """
        # Try exact match first
        cache_key = self._generate_cache_key(prompt, provider, model, temperature)
        cached_response = self.cache.get(cache_key)
        
        if cached_response:
            self._stats['hits'] += 1
            logger.debug(f"LLM cache hit for prompt: {prompt[:50]}...")
            return cached_response
        
        # Try similarity-based lookup (simplified - in production use vector search)
        # For now, we'll just do exact matching
        self._stats['misses'] += 1
        return None
    
    def set(self, prompt: str, response: Dict[str, Any], provider: Optional[str] = None,
            model: Optional[str] = None, temperature: float = 0.7, ttl: Optional[int] = None) -> bool:
        """
        Cache LLM response
        
        Args:
            prompt: LLM prompt
            response: LLM response dict (should contain 'content', 'provider', 'model', 'usage')
            provider: LLM provider name
            model: Model name
            temperature: Temperature setting
            ttl: Time-to-live in seconds
            
        Returns:
            True if cached successfully
        """
        cache_key = self._generate_cache_key(prompt, provider, model, temperature)
        
        # Enhance response with metadata
        cached_data = {
            'content': response.get('content'),
            'provider': response.get('provider', provider),
            'model': response.get('model', model),
            'usage': response.get('usage', {}),
            'cached_at': datetime.utcnow().isoformat(),
            'original_prompt': prompt[:200]  # Store first 200 chars for reference
        }
        
        ttl = ttl if ttl is not None else self.default_ttl
        success = self.cache.set(cache_key, cached_data, ttl)
        
        if success:
            self._stats['saves'] += 1
            # Estimate cost savings (rough estimate)
            usage = response.get('usage', {})
            total_tokens = usage.get('total_tokens', 0) or usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            # Rough estimate: $0.01 per 1000 tokens
            estimated_cost = (total_tokens / 1000) * 0.01
            self._stats['cost_saved'] += estimated_cost
            logger.debug(f"LLM response cached: {prompt[:50]}...")
        
        return success
    
    def invalidate(self, prompt_pattern: Optional[str] = None, provider: Optional[str] = None):
        """
        Invalidate cached responses
        
        Args:
            prompt_pattern: Pattern to match prompts (if None, invalidates all)
            provider: Provider to invalidate (if None, invalidates all)
        """
        if prompt_pattern is None and provider is None:
            # Clear all LLM cache
            pattern = "llm_cache:*"
            count = self.cache.invalidate_pattern(pattern)
            logger.info(f"Invalidated {count} LLM cache entries")
        else:
            # Pattern-based invalidation would require iteration
            # For now, log a warning
            logger.warning("Pattern-based LLM cache invalidation not fully implemented")
    
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
            'hit_rate': round(hit_rate, 2),
            'estimated_cost_saved_usd': round(self._stats['cost_saved'], 2),
            'total_requests': total_requests
        }
    
    def cache_llm_call(self, prompt: str, provider: Optional[str] = None,
                      model: Optional[str] = None, temperature: float = 0.7):
        """
        Decorator function for caching LLM calls
        
        Usage:
            @llm_cache.cache_llm_call(provider="openai", model="gpt-4")
            def call_llm(prompt):
                return llm_config.call_llm(prompt)
        
        Note: This is a helper that returns a decorator
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Extract prompt from args/kwargs
                prompt_arg = kwargs.get('prompt') or (args[0] if args else None)
                
                if prompt_arg:
                    # Try cache first
                    cached = self.get(prompt_arg, provider, model, temperature)
                    if cached:
                        return cached
                
                # Call function
                result = func(*args, **kwargs)
                
                # Cache result
                if prompt_arg and result:
                    self.set(prompt_arg, result, provider, model, temperature)
                
                return result
            return wrapper
        return decorator


# Global LLM cache instance
_llm_cache: Optional[LLMCache] = None


def get_llm_cache() -> LLMCache:
    """Get or create global LLM cache instance"""
    global _llm_cache
    if _llm_cache is None:
        _llm_cache = LLMCache()
    return _llm_cache

