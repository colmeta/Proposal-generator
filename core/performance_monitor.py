"""
Performance monitoring service
Tracks response times, query performance, cache hit rates, and resource usage
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from collections import deque, defaultdict
from datetime import datetime, timedelta
import psutil
import os

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Performance monitoring and metrics collection
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self._lock = threading.RLock()
        
        # Response time tracking
        self.response_times: deque = deque(maxlen=max_history)
        self.endpoint_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        
        # Query performance
        self.query_times: deque = deque(maxlen=max_history)
        self.slow_queries: deque = deque(maxlen=100)
        
        # Cache statistics
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0
        }
        
        # Resource usage
        self.resource_snapshots: deque = deque(maxlen=100)
        
        # Error tracking
        self.errors: deque = deque(maxlen=100)
        
        # Start time
        self.start_time = time.time()
    
    def track_response_time(self, endpoint: str, method: str, duration: float, 
                           status_code: int = 200):
        """
        Track API response time
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            duration: Response time in seconds
            status_code: HTTP status code
        """
        with self._lock:
            metric = {
                'endpoint': endpoint,
                'method': method,
                'duration': duration,
                'status_code': status_code,
                'timestamp': time.time()
            }
            
            self.response_times.append(metric)
            endpoint_key = f"{method} {endpoint}"
            self.endpoint_times[endpoint_key].append(metric)
            
            # Track slow responses (> 1 second)
            if duration > 1.0:
                logger.warning(f"Slow response: {endpoint_key} took {duration:.2f}s")
    
    def track_query_time(self, query: str, duration: float):
        """
        Track database query execution time
        
        Args:
            query: Query identifier or SQL
            duration: Execution time in seconds
        """
        with self._lock:
            metric = {
                'query': query[:100],  # Truncate long queries
                'duration': duration,
                'timestamp': time.time()
            }
            
            self.query_times.append(metric)
            
            # Track slow queries (> 0.5 seconds)
            if duration > 0.5:
                self.slow_queries.append(metric)
                logger.warning(f"Slow query detected: {duration:.2f}s - {query[:50]}...")
    
    def track_cache_hit(self):
        """Track cache hit"""
        with self._lock:
            self.cache_stats['hits'] += 1
            self.cache_stats['total_requests'] += 1
    
    def track_cache_miss(self):
        """Track cache miss"""
        with self._lock:
            self.cache_stats['misses'] += 1
            self.cache_stats['total_requests'] += 1
    
    def track_error(self, error_type: str, error_message: str, endpoint: Optional[str] = None):
        """
        Track error occurrence
        
        Args:
            error_type: Type of error
            error_message: Error message
            endpoint: Optional endpoint where error occurred
        """
        with self._lock:
            error_record = {
                'type': error_type,
                'message': error_message[:200],  # Truncate long messages
                'endpoint': endpoint,
                'timestamp': time.time()
            }
            self.errors.append(error_record)
            logger.error(f"Error tracked: {error_type} - {error_message[:100]}")
    
    def capture_resource_snapshot(self):
        """Capture current resource usage snapshot"""
        try:
            process = psutil.Process(os.getpid())
            
            snapshot = {
                'timestamp': time.time(),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'memory_percent': process.memory_percent(),
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections()) if hasattr(process, 'connections') else 0
            }
            
            # System-wide metrics
            try:
                snapshot['system_cpu_percent'] = psutil.cpu_percent(interval=0.1)
                snapshot['system_memory_percent'] = psutil.virtual_memory().percent
                snapshot['system_memory_available_mb'] = psutil.virtual_memory().available / 1024 / 1024
            except:
                pass
            
            with self._lock:
                self.resource_snapshots.append(snapshot)
            
            return snapshot
        except Exception as e:
            logger.error(f"Error capturing resource snapshot: {e}")
            return None
    
    def get_response_time_stats(self, endpoint: Optional[str] = None, 
                               time_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get response time statistics
        
        Args:
            endpoint: Optional endpoint to filter by
            time_window: Optional time window in seconds
            
        Returns:
            Dictionary with response time statistics
        """
        with self._lock:
            if endpoint:
                times = list(self.endpoint_times.get(endpoint, []))
            else:
                times = list(self.response_times)
            
            # Filter by time window
            if time_window:
                cutoff = time.time() - time_window
                times = [t for t in times if t['timestamp'] > cutoff]
            
            if not times:
                return {
                    'count': 0,
                    'avg': 0,
                    'min': 0,
                    'max': 0,
                    'p50': 0,
                    'p95': 0,
                    'p99': 0
                }
            
            durations = [t['duration'] for t in times]
            durations.sort()
            
            count = len(durations)
            avg = sum(durations) / count
            min_duration = durations[0]
            max_duration = durations[-1]
            
            # Percentiles
            p50 = durations[int(count * 0.50)]
            p95 = durations[int(count * 0.95)] if count > 1 else durations[0]
            p99 = durations[int(count * 0.99)] if count > 1 else durations[0]
            
            return {
                'count': count,
                'avg': round(avg, 3),
                'min': round(min_duration, 3),
                'max': round(max_duration, 3),
                'p50': round(p50, 3),
                'p95': round(p95, 3),
                'p99': round(p99, 3)
            }
    
    def get_query_performance_stats(self, time_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get query performance statistics
        
        Args:
            time_window: Optional time window in seconds
            
        Returns:
            Dictionary with query performance statistics
        """
        with self._lock:
            queries = list(self.query_times)
            
            # Filter by time window
            if time_window:
                cutoff = time.time() - time_window
                queries = [q for q in queries if q['timestamp'] > cutoff]
            
            if not queries:
                return {
                    'total_queries': 0,
                    'avg_time': 0,
                    'slow_queries': 0
                }
            
            durations = [q['duration'] for q in queries]
            avg_time = sum(durations) / len(durations)
            slow_count = len([d for d in durations if d > 0.5])
            
            return {
                'total_queries': len(queries),
                'avg_time': round(avg_time, 3),
                'min_time': round(min(durations), 3),
                'max_time': round(max(durations), 3),
                'slow_queries': slow_count,
                'slow_query_percent': round(slow_count / len(queries) * 100, 2)
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = self.cache_stats['total_requests']
            hits = self.cache_stats['hits']
            misses = self.cache_stats['misses']
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            return {
                'hits': hits,
                'misses': misses,
                'total_requests': total,
                'hit_rate': round(hit_rate, 2)
            }
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get current resource usage statistics"""
        snapshot = self.capture_resource_snapshot()
        if not snapshot:
            return {}
        
        # Calculate averages from recent snapshots
        with self._lock:
            recent_snapshots = list(self.resource_snapshots)[-10:]  # Last 10 snapshots
            
            if recent_snapshots:
                avg_cpu = sum(s.get('cpu_percent', 0) for s in recent_snapshots) / len(recent_snapshots)
                avg_memory = sum(s.get('memory_mb', 0) for s in recent_snapshots) / len(recent_snapshots)
            else:
                avg_cpu = snapshot.get('cpu_percent', 0)
                avg_memory = snapshot.get('memory_mb', 0)
        
        return {
            'current': snapshot,
            'averages': {
                'cpu_percent': round(avg_cpu, 2),
                'memory_mb': round(avg_memory, 2)
            }
        }
    
    def get_error_stats(self, time_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get error statistics
        
        Args:
            time_window: Optional time window in seconds
            
        Returns:
            Dictionary with error statistics
        """
        with self._lock:
            errors = list(self.errors)
            
            # Filter by time window
            if time_window:
                cutoff = time.time() - time_window
                errors = [e for e in errors if e['timestamp'] > cutoff]
            
            error_counts = defaultdict(int)
            for error in errors:
                error_counts[error['type']] += 1
            
            return {
                'total_errors': len(errors),
                'error_types': dict(error_counts),
                'recent_errors': errors[-10:]  # Last 10 errors
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all performance metrics
        
        Returns:
            Dictionary with all metrics
        """
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': round(uptime, 2),
            'uptime_hours': round(uptime / 3600, 2),
            'response_times': self.get_response_time_stats(),
            'query_performance': self.get_query_performance_stats(),
            'cache_stats': self.get_cache_stats(),
            'resource_stats': self.get_resource_stats(),
            'error_stats': self.get_error_stats(),
            'endpoint_stats': {
                endpoint: self.get_response_time_stats(endpoint=endpoint)
                for endpoint in list(self.endpoint_times.keys())[:10]  # Top 10 endpoints
            }
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        with self._lock:
            self.response_times.clear()
            self.endpoint_times.clear()
            self.query_times.clear()
            self.slow_queries.clear()
            self.cache_stats = {'hits': 0, 'misses': 0, 'total_requests': 0}
            self.resource_snapshots.clear()
            self.errors.clear()
            self.start_time = time.time()
            logger.info("Performance monitor statistics reset")


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def track_performance(endpoint: Optional[str] = None):
    """
    Decorator to track function performance
    
    Usage:
        @track_performance(endpoint="/api/data")
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Track response time
                func_endpoint = endpoint or func.__name__
                monitor.track_response_time(func_endpoint, "FUNCTION", duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.track_error(type(e).__name__, str(e), endpoint or func.__name__)
                raise
        
        return wrapper
    return decorator

