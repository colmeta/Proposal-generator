"""Performance monitoring for response times, database queries, and resource usage"""
import time
import psutil
import os
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import deque, defaultdict
from threading import Lock
from dataclasses import dataclass, asdict


@dataclass
class PerformanceMetric:
    """Represents a performance metric"""
    metric_type: str
    component: str
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class PerformanceTracker:
    """Tracks performance metrics"""
    
    def __init__(self, max_metrics: int = 10000, window_size: int = 1000):
        self.max_metrics = max_metrics
        self.window_size = window_size
        self._metrics: List[PerformanceMetric] = []
        self._response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self._db_query_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self._llm_call_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self._lock = Lock()
        
    def record_response_time(self, endpoint: str, method: str, duration: float, status: int = 200) -> None:
        """Record HTTP response time"""
        with self._lock:
            key = f"{method}:{endpoint}"
            self._response_times[key].append(duration)
            
            metric = PerformanceMetric(
                metric_type='response_time',
                component=endpoint,
                value=duration,
                unit='seconds',
                timestamp=datetime.utcnow(),
                metadata={'method': method, 'status': status}
            )
            self._add_metric(metric)
    
    def record_db_query_time(self, operation: str, table: str, duration: float) -> None:
        """Record database query time"""
        with self._lock:
            key = f"{operation}:{table}"
            self._db_query_times[key].append(duration)
            
            metric = PerformanceMetric(
                metric_type='db_query',
                component=table,
                value=duration,
                unit='seconds',
                timestamp=datetime.utcnow(),
                metadata={'operation': operation}
            )
            self._add_metric(metric)
    
    def record_llm_call_time(self, provider: str, model: str, duration: float) -> None:
        """Record LLM API call time"""
        with self._lock:
            key = f"{provider}:{model}"
            self._llm_call_times[key].append(duration)
            
            metric = PerformanceMetric(
                metric_type='llm_call',
                component=provider,
                value=duration,
                unit='seconds',
                timestamp=datetime.utcnow(),
                metadata={'model': model}
            )
            self._add_metric(metric)
    
    def record_cache_performance(self, cache_type: str, hit: bool, duration: float) -> None:
        """Record cache performance"""
        metric = PerformanceMetric(
            metric_type='cache',
            component=cache_type,
            value=duration,
            unit='seconds',
            timestamp=datetime.utcnow(),
            metadata={'hit': hit}
        )
        self._add_metric(metric)
    
    def get_response_time_percentiles(self, endpoint: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """Get response time percentiles"""
        with self._lock:
            if endpoint:
                times = list(self._response_times.get(endpoint, deque()))
            else:
                # Aggregate all
                times = []
                for deq in self._response_times.values():
                    times.extend(deq)
        
        if not times:
            return {}
        
        sorted_times = sorted(times)
        n = len(sorted_times)
        
        percentiles = {
            'p50': sorted_times[n // 2] if n > 0 else 0,
            'p75': sorted_times[int(n * 0.75)] if n > 1 else sorted_times[0],
            'p95': sorted_times[int(n * 0.95)] if n > 1 else sorted_times[0],
            'p99': sorted_times[int(n * 0.99)] if n > 1 else sorted_times[0],
            'min': min(times),
            'max': max(times),
            'avg': sum(times) / n,
            'count': n
        }
        
        if endpoint:
            return {endpoint: percentiles}
        else:
            return {'all': percentiles}
    
    def get_db_query_percentiles(self) -> Dict[str, Dict[str, float]]:
        """Get database query time percentiles"""
        results = {}
        with self._lock:
            for key, deq in self._db_query_times.items():
                times = list(deq)
                if not times:
                    continue
                
                sorted_times = sorted(times)
                n = len(sorted_times)
                
                results[key] = {
                    'p50': sorted_times[n // 2] if n > 0 else 0,
                    'p95': sorted_times[int(n * 0.95)] if n > 1 else sorted_times[0],
                    'p99': sorted_times[int(n * 0.99)] if n > 1 else sorted_times[0],
                    'min': min(times),
                    'max': max(times),
                    'avg': sum(times) / n,
                    'count': n
                }
        
        return results
    
    def get_llm_call_percentiles(self) -> Dict[str, Dict[str, float]]:
        """Get LLM API call time percentiles"""
        results = {}
        with self._lock:
            for key, deq in self._llm_call_times.items():
                times = list(deq)
                if not times:
                    continue
                
                sorted_times = sorted(times)
                n = len(sorted_times)
                
                results[key] = {
                    'p50': sorted_times[n // 2] if n > 0 else 0,
                    'p95': sorted_times[int(n * 0.95)] if n > 1 else sorted_times[0],
                    'p99': sorted_times[int(n * 0.99)] if n > 1 else sorted_times[0],
                    'min': min(times),
                    'max': max(times),
                    'avg': sum(times) / n,
                    'count': n
                }
        
        return results
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        process = psutil.Process(os.getpid())
        
        # CPU
        cpu_percent = process.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        system_memory = psutil.virtual_memory()
        
        # Disk
        disk_usage = psutil.disk_usage('/')
        
        return {
            'cpu': {
                'process_percent': cpu_percent,
                'system_percent': psutil.cpu_percent(interval=0.1),
                'cores': cpu_count
            },
            'memory': {
                'process_rss_mb': memory_info.rss / 1024 / 1024,
                'process_vms_mb': memory_info.vms / 1024 / 1024,
                'process_percent': memory_percent,
                'system_total_gb': system_memory.total / 1024 / 1024 / 1024,
                'system_available_gb': system_memory.available / 1024 / 1024 / 1024,
                'system_percent': system_memory.percent
            },
            'disk': {
                'total_gb': disk_usage.total / 1024 / 1024 / 1024,
                'used_gb': disk_usage.used / 1024 / 1024 / 1024,
                'free_gb': disk_usage.free / 1024 / 1024 / 1024,
                'percent': disk_usage.percent
            }
        }
    
    def get_cache_hit_rate(self, cache_type: str, hours: int = 24) -> Optional[float]:
        """Calculate cache hit rate"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            cache_metrics = [
                m for m in self._metrics
                if m.metric_type == 'cache' and 
                   m.component == cache_type and
                   m.timestamp >= cutoff
            ]
        
        if not cache_metrics:
            return None
        
        hits = sum(1 for m in cache_metrics if m.metadata.get('hit', False))
        total = len(cache_metrics)
        
        return (hits / total * 100) if total > 0 else 0
    
    def get_throughput(self, component: str, hours: int = 1) -> float:
        """Calculate requests per second for a component"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            component_metrics = [
                m for m in self._metrics
                if m.component == component and m.timestamp >= cutoff
            ]
        
        if not component_metrics:
            return 0.0
        
        duration_hours = hours
        count = len(component_metrics)
        
        return count / (duration_hours * 3600)  # requests per second
    
    def _add_metric(self, metric: PerformanceMetric) -> None:
        """Add a metric to storage"""
        self._metrics.append(metric)
        if len(self._metrics) > self.max_metrics:
            self._metrics.pop(0)
    
    def time_function(self, component: str):
        """Decorator to time a function"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.record_response_time(component, 'function', duration)
            return wrapper
        return decorator


# Global performance tracker instance
_performance_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance"""
    global _performance_tracker
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    return _performance_tracker


