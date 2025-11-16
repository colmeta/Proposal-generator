"""
Performance and caching tests
Tests cache functionality, query optimization, and performance monitoring
"""

import pytest
import time
from unittest.mock import Mock, patch
from services.cache import MemoryCache, RedisCache, CacheManager, get_cache_manager
from services.optimization import QueryOptimizer, LLMCache, ResponseCache, DatabaseIndexer
from services.optimization.query_optimizer import get_query_optimizer
from services.optimization.llm_cache import get_llm_cache
from services.optimization.response_cache import get_response_cache
from core.performance_monitor import PerformanceMonitor, get_performance_monitor
from utils.cache_decorators import cached, cached_method, async_cached, cache_key
from flask import Flask, Request


class TestMemoryCache:
    """Test memory cache implementation"""
    
    def test_cache_set_get(self):
        """Test basic cache set and get"""
        cache = MemoryCache(max_size=10, default_ttl=60)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = MemoryCache(max_size=10, default_ttl=1)
        
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"
        
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_cache_delete(self):
        """Test cache deletion"""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = MemoryCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # All should be present
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        
        # Add one more, should evict key1 (oldest)
        cache.set("key4", "value4")
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['sets'] == 1
        assert stats['hit_rate'] > 0
    
    def test_cache_get_many(self):
        """Test getting multiple values"""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        results = cache.get_many(["key1", "key2", "key4"])
        assert "key1" in results
        assert "key2" in results
        assert "key4" not in results
    
    def test_cache_set_many(self):
        """Test setting multiple values"""
        cache = MemoryCache(max_size=10)
        
        mapping = {"key1": "value1", "key2": "value2", "key3": "value3"}
        count = cache.set_many(mapping)
        
        assert count == 3
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"


class TestCacheManager:
    """Test cache manager with fallback"""
    
    def test_cache_manager_memory_fallback(self):
        """Test cache manager falls back to memory cache"""
        manager = CacheManager(use_redis=False)
        
        manager.set("key1", "value1")
        assert manager.get("key1") == "value1"
    
    def test_cache_manager_stats(self):
        """Test cache manager statistics"""
        manager = CacheManager(use_redis=False)
        
        manager.set("key1", "value1")
        manager.get("key1")
        manager.get("key2")  # Miss
        
        stats = manager.get_stats()
        assert 'primary' in stats or 'memory' in stats


class TestQueryOptimizer:
    """Test query optimization"""
    
    def test_track_query(self):
        """Test query tracking"""
        optimizer = QueryOptimizer(slow_query_threshold=0.5)
        
        optimizer.track_query("SELECT * FROM users", 0.1)
        optimizer.track_query("SELECT * FROM users", 0.2)
        
        stats = optimizer.get_query_stats()
        assert stats['total_queries'] == 2
    
    def test_slow_query_detection(self):
        """Test slow query detection"""
        optimizer = QueryOptimizer(slow_query_threshold=0.5)
        
        optimizer.track_query("SELECT * FROM users", 1.0)  # Slow query
        
        slow_queries = optimizer.get_slow_queries()
        assert len(slow_queries) > 0
        assert slow_queries[0]['duration'] > 0.5
    
    def test_query_normalization(self):
        """Test query normalization"""
        optimizer = QueryOptimizer()
        
        query1 = "SELECT * FROM users WHERE id = 1"
        query2 = "SELECT * FROM users WHERE id = 2"
        
        normalized1 = optimizer._normalize_query(query1)
        normalized2 = optimizer._normalize_query(query2)
        
        # Should normalize to same query
        assert normalized1 == normalized2


class TestLLMCache:
    """Test LLM response caching"""
    
    def test_llm_cache_set_get(self):
        """Test LLM cache set and get"""
        cache = LLMCache()
        
        response = {
            'content': 'Test response',
            'provider': 'openai',
            'model': 'gpt-4',
            'usage': {'total_tokens': 100}
        }
        
        cache.set("test prompt", response)
        cached = cache.get("test prompt")
        
        assert cached is not None
        assert cached['content'] == 'Test response'
    
    def test_llm_cache_stats(self):
        """Test LLM cache statistics"""
        cache = LLMCache()
        
        response = {
            'content': 'Test',
            'provider': 'openai',
            'usage': {'total_tokens': 100}
        }
        
        cache.set("prompt1", response)
        cache.get("prompt1")  # Hit
        cache.get("prompt2")  # Miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1


class TestResponseCache:
    """Test API response caching"""
    
    def test_response_cache_key_generation(self):
        """Test response cache key generation"""
        cache = ResponseCache()
        
        # Create mock request
        app = Flask(__name__)
        with app.test_request_context('/api/test?param=value'):
            from flask import request
            key = cache._generate_cache_key(request)
            assert key.startswith("api_cache:")
    
    def test_response_cache_etag(self):
        """Test ETag generation"""
        cache = ResponseCache()
        
        data = {'test': 'data'}
        etag = cache._generate_etag(data)
        
        assert etag.startswith('"')
        assert etag.endswith('"')


class TestPerformanceMonitor:
    """Test performance monitoring"""
    
    def test_track_response_time(self):
        """Test response time tracking"""
        monitor = PerformanceMonitor()
        
        monitor.track_response_time("/api/test", "GET", 0.5)
        monitor.track_response_time("/api/test", "GET", 0.3)
        
        stats = monitor.get_response_time_stats(endpoint="GET /api/test")
        assert stats['count'] == 2
        assert stats['avg'] > 0
    
    def test_track_query_time(self):
        """Test query time tracking"""
        monitor = PerformanceMonitor()
        
        monitor.track_query_time("SELECT * FROM users", 0.2)
        monitor.track_query_time("SELECT * FROM users", 0.1)
        
        stats = monitor.get_query_performance_stats()
        assert stats['total_queries'] == 2
    
    def test_track_cache_hit_miss(self):
        """Test cache hit/miss tracking"""
        monitor = PerformanceMonitor()
        
        monitor.track_cache_hit()
        monitor.track_cache_hit()
        monitor.track_cache_miss()
        
        stats = monitor.get_cache_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] > 0
    
    def test_track_error(self):
        """Test error tracking"""
        monitor = PerformanceMonitor()
        
        monitor.track_error("ValueError", "Test error", "/api/test")
        
        error_stats = monitor.get_error_stats()
        assert error_stats['total_errors'] == 1
    
    def test_resource_snapshot(self):
        """Test resource snapshot capture"""
        monitor = PerformanceMonitor()
        
        snapshot = monitor.capture_resource_snapshot()
        assert snapshot is not None
        assert 'cpu_percent' in snapshot
        assert 'memory_mb' in snapshot
    
    def test_get_all_metrics(self):
        """Test getting all metrics"""
        monitor = PerformanceMonitor()
        
        monitor.track_response_time("/api/test", "GET", 0.5)
        monitor.track_query_time("SELECT * FROM users", 0.2)
        monitor.track_cache_hit()
        
        metrics = monitor.get_all_metrics()
        assert 'response_times' in metrics
        assert 'query_performance' in metrics
        assert 'cache_stats' in metrics
        assert 'resource_stats' in metrics


class TestCacheDecorators:
    """Test cache decorators"""
    
    def test_cached_decorator(self):
        """Test @cached decorator"""
        call_count = [0]
        
        @cached(ttl=60)
        def expensive_function(x):
            call_count[0] += 1
            return x * 2
        
        # First call - should execute
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count[0] == 1
        
        # Second call - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count[0] == 1  # Should not increment
    
    def test_cached_method_decorator(self):
        """Test @cached_method decorator"""
        call_count = [0]
        
        class TestClass:
            @cached_method(ttl=60)
            def expensive_method(self, x):
                call_count[0] += 1
                return x * 2
        
        obj = TestClass()
        
        # First call
        result1 = obj.expensive_method(5)
        assert result1 == 10
        assert call_count[0] == 1
        
        # Second call - should use cache
        result2 = obj.expensive_method(5)
        assert result2 == 10
        assert call_count[0] == 1
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        key1 = cache_key("test", arg1=1, arg2=2)
        key2 = cache_key("test", arg1=1, arg2=2)
        key3 = cache_key("test", arg1=2, arg2=1)
        
        # Same args should generate same key
        assert key1 == key2
        
        # Different args should generate different key
        assert key1 != key3


class TestDatabaseIndexer:
    """Test database indexing"""
    
    def test_get_existing_indexes(self):
        """Test getting existing indexes"""
        from database.db import engine
        indexer = DatabaseIndexer(engine)
        
        # Should not raise error
        indexes = indexer.get_existing_indexes("projects")
        assert isinstance(indexes, list)


class TestIntegration:
    """Integration tests"""
    
    def test_cache_integration(self):
        """Test cache integration with multiple layers"""
        manager = CacheManager(use_redis=False)
        
        # Set in cache
        manager.set("test_key", "test_value", ttl=60)
        
        # Get from cache
        value = manager.get("test_key")
        assert value == "test_value"
        
        # Get stats
        stats = manager.get_stats()
        assert stats is not None
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration"""
        monitor = PerformanceMonitor()
        
        # Simulate some activity
        monitor.track_response_time("/api/jobs", "GET", 0.1)
        monitor.track_query_time("SELECT * FROM jobs", 0.05)
        monitor.track_cache_hit()
        
        # Get all metrics
        metrics = monitor.get_all_metrics()
        assert metrics['response_times']['count'] > 0
        assert metrics['query_performance']['total_queries'] > 0
        assert metrics['cache_stats']['hits'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

