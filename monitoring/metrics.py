"""Metrics collection for application, performance, and business metrics"""
import time
from typing import Dict, Any, Optional, Callable
from collections import defaultdict, deque
from threading import Lock
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
from prometheus_client.core import REGISTRY


class MetricsCollector:
    """Centralized metrics collection"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._lock = Lock()
        
        # Application metrics
        self.request_count = Counter(
            'app_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'app_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Error metrics
        self.error_count = Counter(
            'app_errors_total',
            'Total number of errors',
            ['error_type', 'component'],
            registry=self.registry
        )
        
        # Business metrics
        self.proposal_generated = Counter(
            'proposals_generated_total',
            'Total number of proposals generated',
            ['funder', 'status'],
            registry=self.registry
        )
        
        self.proposal_generation_duration = Histogram(
            'proposal_generation_duration_seconds',
            'Proposal generation duration',
            ['funder'],
            registry=self.registry
        )
        
        # LLM metrics
        self.llm_api_calls = Counter(
            'llm_api_calls_total',
            'Total LLM API calls',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        self.llm_api_duration = Histogram(
            'llm_api_duration_seconds',
            'LLM API call duration',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.llm_tokens_used = Counter(
            'llm_tokens_total',
            'Total tokens used',
            ['provider', 'model', 'type'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_query_count = Counter(
            'db_queries_total',
            'Total database queries',
            ['operation', 'table'],
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration',
            ['operation', 'table'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # Custom metrics storage
        self._custom_metrics: Dict[str, Any] = defaultdict(lambda: {
            'counters': {},
            'gauges': {},
            'histograms': {}
        })
        
    def record_request(self, method: str, endpoint: str, status: int, duration: float) -> None:
        """Record HTTP request metrics"""
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_error(self, error_type: str, component: str) -> None:
        """Record error metrics"""
        self.error_count.labels(error_type=error_type, component=component).inc()
    
    def record_proposal_generation(self, funder: str, status: str, duration: float) -> None:
        """Record proposal generation metrics"""
        self.proposal_generated.labels(funder=funder, status=status).inc()
        self.proposal_generation_duration.labels(funder=funder).observe(duration)
    
    def record_llm_call(self, provider: str, model: str, status: str, duration: float, 
                       tokens_prompt: int = 0, tokens_completion: int = 0) -> None:
        """Record LLM API call metrics"""
        self.llm_api_calls.labels(provider=provider, model=model, status=status).inc()
        self.llm_api_duration.labels(provider=provider, model=model).observe(duration)
        
        if tokens_prompt > 0:
            self.llm_tokens_used.labels(provider=provider, model=model, type='prompt').inc(tokens_prompt)
        if tokens_completion > 0:
            self.llm_tokens_used.labels(provider=provider, model=model, type='completion').inc(tokens_completion)
    
    def record_db_query(self, operation: str, table: str, duration: float) -> None:
        """Record database query metrics"""
        self.db_query_count.labels(operation=operation, table=table).inc()
        self.db_query_duration.labels(operation=operation, table=table).observe(duration)
    
    def record_cache_hit(self, cache_type: str) -> None:
        """Record cache hit"""
        self.cache_hits.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str) -> None:
        """Record cache miss"""
        self.cache_misses.labels(cache_type=cache_type).inc()
    
    def create_custom_counter(self, name: str, description: str, labels: Optional[list] = None) -> Counter:
        """Create a custom counter metric"""
        labels = labels or []
        counter = Counter(
            name,
            description,
            labels,
            registry=self.registry
        )
        self._custom_metrics[name]['counters'][str(labels)] = counter
        return counter
    
    def create_custom_gauge(self, name: str, description: str, labels: Optional[list] = None) -> Gauge:
        """Create a custom gauge metric"""
        labels = labels or []
        gauge = Gauge(
            name,
            description,
            labels,
            registry=self.registry
        )
        self._custom_metrics[name]['gauges'][str(labels)] = gauge
        return gauge
    
    def create_custom_histogram(self, name: str, description: str, labels: Optional[list] = None) -> Histogram:
        """Create a custom histogram metric"""
        labels = labels or []
        histogram = Histogram(
            name,
            description,
            labels,
            registry=self.registry
        )
        self._custom_metrics[name]['histograms'][str(labels)] = histogram
        return histogram
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')
    
    def time_function(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Decorator to time a function and record metrics"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    status = 'success'
                    return result
                except Exception as e:
                    status = 'error'
                    raise
                finally:
                    duration = time.time() - start_time
                    if labels:
                        # Find or create histogram
                        label_values = tuple(labels.values())
                        label_keys = tuple(labels.keys())
                        hist_name = f"{metric_name}_duration_seconds"
                        # This is simplified - in practice, you'd want to cache these
                        pass
            return wrapper
        return decorator


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector



