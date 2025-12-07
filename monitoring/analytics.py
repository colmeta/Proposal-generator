"""Usage analytics and user activity tracking"""
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass, asdict
import json


@dataclass
class ActivityRecord:
    """Represents a user activity record"""
    user_id: Optional[str]
    activity_type: str
    component: str
    metadata: Dict[str, Any]
    timestamp: datetime
    duration: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ProposalMetrics:
    """Metrics for proposal generation"""
    funder: str
    status: str
    generation_time: float
    sections_count: int
    word_count: int
    timestamp: datetime


class AnalyticsCollector:
    """Collects usage analytics and statistics"""
    
    def __init__(self, max_records: int = 50000):
        self.max_records = max_records
        self._activities: List[ActivityRecord] = []
        self._proposal_metrics: List[ProposalMetrics] = []
        self._feature_usage: Dict[str, int] = defaultdict(int)
        self._user_activity: Dict[str, List[ActivityRecord]] = defaultdict(list)
        self._lock = Lock()
        
    def track_activity(self, 
                      activity_type: str,
                      component: str,
                      user_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None,
                      duration: Optional[float] = None) -> ActivityRecord:
        """Track a user activity"""
        record = ActivityRecord(
            user_id=user_id,
            activity_type=activity_type,
            component=component,
            metadata=metadata or {},
            timestamp=datetime.utcnow(),
            duration=duration
        )
        
        with self._lock:
            self._activities.append(record)
            
            # Track feature usage
            feature_key = f"{component}:{activity_type}"
            self._feature_usage[feature_key] += 1
            
            # Track user activity
            if user_id:
                self._user_activity[user_id].append(record)
            
            # Limit storage
            if len(self._activities) > self.max_records:
                removed = self._activities.pop(0)
                if removed.user_id and removed.user_id in self._user_activity:
                    if removed in self._user_activity[removed.user_id]:
                        self._user_activity[removed.user_id].remove(removed)
        
        return record
    
    def track_proposal_generation(self,
                                 funder: str,
                                 status: str,
                                 generation_time: float,
                                 sections_count: int = 0,
                                 word_count: int = 0) -> ProposalMetrics:
        """Track proposal generation metrics"""
        metrics = ProposalMetrics(
            funder=funder,
            status=status,
            generation_time=generation_time,
            sections_count=sections_count,
            word_count=word_count,
            timestamp=datetime.utcnow()
        )
        
        with self._lock:
            self._proposal_metrics.append(metrics)
            
            # Limit storage
            if len(self._proposal_metrics) > self.max_records:
                self._proposal_metrics.pop(0)
        
        return metrics
    
    def get_feature_usage_stats(self) -> Dict[str, Any]:
        """Get feature usage statistics"""
        with self._lock:
            total_usage = sum(self._feature_usage.values())
            top_features = sorted(
                self._feature_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]
        
        return {
            'total_activities': total_usage,
            'unique_features': len(self._feature_usage),
            'top_features': [
                {'feature': feature, 'count': count}
                for feature, count in top_features
            ]
        }
    
    def get_proposal_statistics(self) -> Dict[str, Any]:
        """Get proposal generation statistics"""
        with self._lock:
            metrics = self._proposal_metrics.copy()
        
        if not metrics:
            return {
                'total_proposals': 0,
                'success_rate': 0,
                'average_generation_time': 0,
                'by_funder': {},
                'by_status': {}
            }
        
        total = len(metrics)
        successful = len([m for m in metrics if m.status == 'success'])
        success_rate = (successful / total * 100) if total > 0 else 0
        
        avg_time = sum(m.generation_time for m in metrics) / total
        
        by_funder = defaultdict(lambda: {'count': 0, 'avg_time': 0, 'success': 0})
        by_status = defaultdict(int)
        
        for m in metrics:
            by_funder[m.funder]['count'] += 1
            by_funder[m.funder]['avg_time'] += m.generation_time
            if m.status == 'success':
                by_funder[m.funder]['success'] += 1
            by_status[m.status] += 1
        
        # Calculate averages
        for funder_data in by_funder.values():
            if funder_data['count'] > 0:
                funder_data['avg_time'] /= funder_data['count']
        
        return {
            'total_proposals': total,
            'success_rate': round(success_rate, 2),
            'average_generation_time': round(avg_time, 2),
            'by_funder': dict(by_funder),
            'by_status': dict(by_status)
        }
    
    def get_user_activity(self, user_id: str, hours: int = 24) -> List[ActivityRecord]:
        """Get user activity for the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            if user_id not in self._user_activity:
                return []
            return [a for a in self._user_activity[user_id] if a.timestamp >= cutoff]
    
    def get_recent_activities(self, hours: int = 24, limit: int = 100) -> List[ActivityRecord]:
        """Get recent activities"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            activities = [a for a in self._activities if a.timestamp >= cutoff]
            activities.sort(key=lambda x: x.timestamp, reverse=True)
            return activities[:limit]
    
    def get_popular_funders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular funders"""
        with self._lock:
            funder_counts = defaultdict(int)
            for m in self._proposal_metrics:
                funder_counts[m.funder] += 1
        
        popular = sorted(
            funder_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {'funder': funder, 'count': count}
            for funder, count in popular
        ]
    
    def get_time_to_completion_stats(self) -> Dict[str, float]:
        """Get time-to-completion statistics"""
        with self._lock:
            completion_times = [
                m.generation_time for m in self._proposal_metrics
                if m.status == 'success' and m.generation_time > 0
            ]
        
        if not completion_times:
            return {}
        
        sorted_times = sorted(completion_times)
        n = len(sorted_times)
        
        return {
            'min': min(completion_times),
            'max': max(completion_times),
            'avg': sum(completion_times) / n,
            'p50': sorted_times[n // 2] if n > 0 else 0,
            'p95': sorted_times[int(n * 0.95)] if n > 1 else sorted_times[0],
            'p99': sorted_times[int(n * 0.99)] if n > 1 else sorted_times[0],
        }
    
    def export_analytics(self, filepath: str) -> None:
        """Export analytics data to JSON"""
        with self._lock:
            data = {
                'activities': [a.to_dict() for a in self._activities[-1000:]],  # Last 1000
                'proposal_metrics': [
                    asdict(m) for m in self._proposal_metrics[-1000:]
                ],
                'feature_usage': dict(self._feature_usage),
                'statistics': {
                    'feature_usage': self.get_feature_usage_stats(),
                    'proposal_stats': self.get_proposal_statistics(),
                }
            }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)


# Global analytics collector instance
_analytics_collector: Optional[AnalyticsCollector] = None


def get_analytics_collector() -> AnalyticsCollector:
    """Get the global analytics collector instance"""
    global _analytics_collector
    if _analytics_collector is None:
        _analytics_collector = AnalyticsCollector()
    return _analytics_collector


def track_activity(activity_type: str, component: str):
    """Decorator to track function activity"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                collector = get_analytics_collector()
                collector.track_activity(
                    activity_type=activity_type,
                    component=component,
                    duration=duration
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                collector = get_analytics_collector()
                collector.track_activity(
                    activity_type=f"{activity_type}_error",
                    component=component,
                    duration=duration,
                    metadata={'error': str(e)}
                )
                raise
        return wrapper
    return decorator



