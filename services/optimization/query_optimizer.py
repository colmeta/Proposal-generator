"""
Database query optimization service
Analyzes queries, recommends indexes, detects slow queries
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """
    Database query optimization and monitoring
    """
    
    def __init__(self, slow_query_threshold: float = 1.0):
        """
        Initialize query optimizer
        
        Args:
            slow_query_threshold: Threshold in seconds for slow query detection
        """
        self.slow_query_threshold = slow_query_threshold
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        self.slow_queries: deque = deque(maxlen=100)  # Keep last 100 slow queries
        self._query_cache: Dict[str, Any] = {}
        self._enabled = True
    
    def enable(self):
        """Enable query optimization"""
        self._enabled = True
    
    def disable(self):
        """Disable query optimization"""
        self._enabled = False
    
    def track_query(self, query: str, duration: float, params: Optional[Dict] = None):
        """
        Track a query execution
        
        Args:
            query: SQL query string
            duration: Execution time in seconds
            params: Query parameters
        """
        if not self._enabled:
            return
        
        # Normalize query (remove parameters for grouping)
        normalized_query = self._normalize_query(query)
        
        # Update statistics
        if normalized_query not in self.query_stats:
            self.query_stats[normalized_query] = {
                'count': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'avg_time': 0.0,
                'last_executed': None
            }
        
        stats = self.query_stats[normalized_query]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['last_executed'] = time.time()
        
        # Track slow queries
        if duration > self.slow_query_threshold:
            self.slow_queries.append({
                'query': query,
                'normalized_query': normalized_query,
                'duration': duration,
                'params': params,
                'timestamp': time.time()
            })
            logger.warning(f"Slow query detected ({duration:.2f}s): {normalized_query[:100]}")
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for grouping (remove specific values)
        
        Args:
            query: SQL query string
            
        Returns:
            Normalized query string
        """
        # Simple normalization - remove quoted strings and numbers
        import re
        # Remove string literals
        query = re.sub(r"'[^']*'", "'?'", query)
        # Remove numeric literals
        query = re.sub(r'\b\d+\b', '?', query)
        # Normalize whitespace
        query = ' '.join(query.split())
        return query
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get slow queries
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of slow query records
        """
        return list(self.slow_queries)[-limit:]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """
        Get query statistics
        
        Returns:
            Dictionary with query statistics
        """
        total_queries = sum(stats['count'] for stats in self.query_stats.values())
        total_time = sum(stats['total_time'] for stats in self.query_stats.values())
        
        # Sort by average time (descending)
        sorted_queries = sorted(
            self.query_stats.items(),
            key=lambda x: x[1]['avg_time'],
            reverse=True
        )
        
        return {
            'total_queries': total_queries,
            'total_time': total_time,
            'unique_queries': len(self.query_stats),
            'slow_query_count': len(self.slow_queries),
            'top_queries': [
                {
                    'query': query,
                    'stats': stats
                }
                for query, stats in sorted_queries[:10]
            ]
        }
    
    def recommend_indexes(self, table_name: str, columns: List[str]) -> List[str]:
        """
        Recommend indexes for a table
        
        Args:
            table_name: Name of the table
            columns: List of column names
            
        Returns:
            List of index creation SQL statements
        """
        recommendations = []
        
        # Analyze query patterns for this table
        table_queries = [
            (query, stats) for query, stats in self.query_stats.items()
            if table_name.lower() in query.lower()
        ]
        
        # Recommend indexes for frequently queried columns
        column_usage = defaultdict(int)
        for query, stats in table_queries:
            for col in columns:
                if col.lower() in query.lower():
                    column_usage[col] += stats['count']
        
        # Recommend indexes for most frequently used columns
        sorted_columns = sorted(column_usage.items(), key=lambda x: x[1], reverse=True)
        
        for col, usage_count in sorted_columns[:5]:  # Top 5 columns
            if usage_count > 10:  # Only if used frequently
                index_name = f"idx_{table_name}_{col}"
                recommendations.append(
                    f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({col});"
                )
        
        return recommendations
    
    def analyze_query_plan(self, session: Session, query: str) -> Dict[str, Any]:
        """
        Analyze query execution plan
        
        Args:
            session: Database session
            query: SQL query to analyze
            
        Returns:
            Query plan information
        """
        try:
            # Use EXPLAIN for query plan
            if 'sqlite' in str(session.bind.url).lower():
                explain_query = f"EXPLAIN QUERY PLAN {query}"
            else:
                explain_query = f"EXPLAIN {query}"
            
            result = session.execute(text(explain_query))
            plan = [dict(row._mapping) for row in result]
            
            return {
                'query': query,
                'plan': plan,
                'analyzed_at': time.time()
            }
        except Exception as e:
            logger.error(f"Error analyzing query plan: {e}")
            return {
                'query': query,
                'error': str(e),
                'analyzed_at': time.time()
            }
    
    def optimize_connection_pool(self, engine: Engine) -> Dict[str, Any]:
        """
        Analyze and recommend connection pool settings
        
        Args:
            engine: SQLAlchemy engine
            
        Returns:
            Recommendations for connection pool optimization
        """
        pool = engine.pool
        
        recommendations = []
        current_settings = {
            'pool_size': getattr(pool, 'size', None),
            'max_overflow': getattr(pool, 'max_overflow', None),
            'pool_timeout': getattr(pool, '_timeout', None)
        }
        
        # Analyze query patterns
        stats = self.get_query_stats()
        concurrent_queries = stats.get('total_queries', 0) / max(stats.get('unique_queries', 1), 1)
        
        # Recommend pool size based on concurrent queries
        if concurrent_queries > 10:
            recommended_pool_size = min(int(concurrent_queries * 1.5), 20)
            if current_settings['pool_size'] and current_settings['pool_size'] < recommended_pool_size:
                recommendations.append({
                    'setting': 'pool_size',
                    'current': current_settings['pool_size'],
                    'recommended': recommended_pool_size,
                    'reason': f'High concurrent query load ({concurrent_queries:.1f} queries/unique query)'
                })
        
        return {
            'current_settings': current_settings,
            'recommendations': recommendations,
            'query_stats': {
                'total_queries': stats.get('total_queries', 0),
                'unique_queries': stats.get('unique_queries', 0),
                'concurrent_ratio': concurrent_queries
            }
        }


# Global query optimizer instance
_query_optimizer: Optional[QueryOptimizer] = None


def get_query_optimizer() -> QueryOptimizer:
    """Get or create global query optimizer instance"""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer


def track_query_execution(func: Callable) -> Callable:
    """
    Decorator to track query execution time
    
    Usage:
        @track_query_execution
        def my_query_function(session):
            return session.query(Model).all()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        optimizer = get_query_optimizer()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Try to extract query from result if it's a SQLAlchemy query
            query_str = str(func.__name__)
            optimizer.track_query(query_str, duration)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            optimizer.track_query(f"{func.__name__} (ERROR)", duration)
            raise
    
    return wrapper

