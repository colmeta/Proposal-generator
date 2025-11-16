"""Tests for monitoring and analytics system"""
import pytest
import time
import os
from datetime import datetime, timedelta
from monitoring.logging_config import setup_logging, get_logger, LoggingConfig
from monitoring.metrics import MetricsCollector, get_metrics_collector
from monitoring.error_tracker import ErrorTracker, get_error_tracker, track_error
from monitoring.analytics import AnalyticsCollector, get_analytics_collector, track_activity
from monitoring.performance_tracker import PerformanceTracker, get_performance_tracker
from monitoring.health_check import HealthChecker, get_health_checker, HealthStatus
from monitoring.alerts import AlertManager, get_alert_manager, AlertSeverity, AlertChannel
from utils.logging_helpers import log_function_call, log_performance, log_context, PerformanceLogger


class TestLoggingConfig:
    """Tests for logging configuration"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        setup_logging(log_level='INFO')
        logger = get_logger('test')
        assert logger is not None
        assert logger.level == 20  # INFO level
    
    def test_get_logger(self):
        """Test getting a logger"""
        logger = get_logger('test_logger')
        assert logger.name == 'test_logger'
        assert len(logger.handlers) > 0
    
    def test_logging_config(self):
        """Test logging configuration"""
        config = LoggingConfig()
        assert config.log_dir.exists()
        assert config.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


class TestMetricsCollector:
    """Tests for metrics collection"""
    
    def test_metrics_collector_creation(self):
        """Test metrics collector creation"""
        collector = MetricsCollector()
        assert collector is not None
    
    def test_record_request(self):
        """Test recording HTTP requests"""
        collector = MetricsCollector()
        collector.record_request('GET', '/api/test', 200, 0.5)
        metrics = collector.get_metrics()
        assert 'app_requests_total' in metrics
    
    def test_record_error(self):
        """Test recording errors"""
        collector = MetricsCollector()
        collector.record_error('ValueError', 'test_component')
        metrics = collector.get_metrics()
        assert 'app_errors_total' in metrics
    
    def test_record_proposal_generation(self):
        """Test recording proposal generation"""
        collector = MetricsCollector()
        collector.record_proposal_generation('gates_foundation', 'success', 10.5)
        metrics = collector.get_metrics()
        assert 'proposals_generated_total' in metrics
    
    def test_record_llm_call(self):
        """Test recording LLM API calls"""
        collector = MetricsCollector()
        collector.record_llm_call('openai', 'gpt-4', 'success', 2.5, 100, 50)
        metrics = collector.get_metrics()
        assert 'llm_api_calls_total' in metrics
        assert 'llm_tokens_total' in metrics
    
    def test_record_db_query(self):
        """Test recording database queries"""
        collector = MetricsCollector()
        collector.record_db_query('SELECT', 'proposals', 0.1)
        metrics = collector.get_metrics()
        assert 'db_queries_total' in metrics
    
    def test_cache_metrics(self):
        """Test cache metrics"""
        collector = MetricsCollector()
        collector.record_cache_hit('redis')
        collector.record_cache_miss('redis')
        metrics = collector.get_metrics()
        assert 'cache_hits_total' in metrics
        assert 'cache_misses_total' in metrics
    
    def test_get_metrics_collector(self):
        """Test getting global metrics collector"""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        assert collector1 is collector2  # Should be singleton


class TestErrorTracker:
    """Tests for error tracking"""
    
    def test_error_tracker_creation(self):
        """Test error tracker creation"""
        tracker = ErrorTracker()
        assert tracker is not None
    
    def test_capture_error(self):
        """Test capturing errors"""
        tracker = ErrorTracker()
        try:
            raise ValueError("Test error")
        except ValueError as e:
            record = tracker.capture_error(e, 'test_component', {'test': 'data'})
            assert record.error_type == 'ValueError'
            assert record.component == 'test_component'
            assert record.error_message == 'Test error'
            assert 'test' in record.context
    
    def test_get_errors(self):
        """Test getting errors"""
        tracker = ErrorTracker()
        try:
            raise ValueError("Test error")
        except ValueError as e:
            tracker.capture_error(e, 'test_component')
        
        errors = tracker.get_errors()
        assert len(errors) > 0
        assert errors[0].error_type == 'ValueError'
    
    def test_get_error_statistics(self):
        """Test getting error statistics"""
        tracker = ErrorTracker()
        try:
            raise ValueError("Test error")
        except ValueError as e:
            tracker.capture_error(e, 'test_component')
        
        stats = tracker.get_error_statistics()
        assert 'total_errors' in stats
        assert 'unique_errors' in stats
        assert stats['total_errors'] > 0
    
    def test_error_frequency(self):
        """Test error frequency tracking"""
        tracker = ErrorTracker()
        try:
            raise ValueError("Test error")
        except ValueError as e:
            tracker.capture_error(e, 'test_component')
            tracker.capture_error(e, 'test_component')
        
        errors = tracker.get_errors()
        assert errors[0].frequency >= 2
    
    def test_track_error_decorator(self):
        """Test error tracking decorator"""
        tracker = ErrorTracker()
        
        @track_error('test_component')
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        errors = tracker.get_errors()
        assert len(errors) > 0


class TestAnalyticsCollector:
    """Tests for analytics collection"""
    
    def test_analytics_collector_creation(self):
        """Test analytics collector creation"""
        collector = AnalyticsCollector()
        assert collector is not None
    
    def test_track_activity(self):
        """Test tracking activities"""
        collector = AnalyticsCollector()
        record = collector.track_activity(
            'proposal_view',
            'proposal_service',
            user_id='user123',
            metadata={'proposal_id': 'prop1'}
        )
        assert record.activity_type == 'proposal_view'
        assert record.user_id == 'user123'
    
    def test_track_proposal_generation(self):
        """Test tracking proposal generation"""
        collector = AnalyticsCollector()
        metrics = collector.track_proposal_generation(
            'gates_foundation',
            'success',
            15.5,
            sections_count=10,
            word_count=5000
        )
        assert metrics.funder == 'gates_foundation'
        assert metrics.status == 'success'
        assert metrics.generation_time == 15.5
    
    def test_get_feature_usage_stats(self):
        """Test getting feature usage statistics"""
        collector = AnalyticsCollector()
        collector.track_activity('proposal_view', 'proposal_service')
        collector.track_activity('proposal_view', 'proposal_service')
        
        stats = collector.get_feature_usage_stats()
        assert stats['total_activities'] >= 2
        assert 'proposal_service:proposal_view' in [f['feature'] for f in stats['top_features']]
    
    def test_get_proposal_statistics(self):
        """Test getting proposal statistics"""
        collector = AnalyticsCollector()
        collector.track_proposal_generation('gates_foundation', 'success', 10.0)
        collector.track_proposal_generation('gates_foundation', 'success', 12.0)
        collector.track_proposal_generation('world_bank', 'failed', 5.0)
        
        stats = collector.get_proposal_statistics()
        assert stats['total_proposals'] == 3
        assert stats['success_rate'] > 0
        assert 'gates_foundation' in stats['by_funder']
    
    def test_get_popular_funders(self):
        """Test getting popular funders"""
        collector = AnalyticsCollector()
        collector.track_proposal_generation('gates_foundation', 'success', 10.0)
        collector.track_proposal_generation('gates_foundation', 'success', 12.0)
        collector.track_proposal_generation('world_bank', 'success', 8.0)
        
        popular = collector.get_popular_funders()
        assert len(popular) > 0
        assert popular[0]['funder'] == 'gates_foundation'
    
    def test_track_activity_decorator(self):
        """Test activity tracking decorator"""
        collector = AnalyticsCollector()
        
        @track_activity('test_activity', 'test_component')
        def test_function():
            time.sleep(0.1)
            return "result"
        
        result = test_function()
        assert result == "result"
        
        stats = collector.get_feature_usage_stats()
        assert stats['total_activities'] > 0


class TestPerformanceTracker:
    """Tests for performance tracking"""
    
    def test_performance_tracker_creation(self):
        """Test performance tracker creation"""
        tracker = PerformanceTracker()
        assert tracker is not None
    
    def test_record_response_time(self):
        """Test recording response times"""
        tracker = PerformanceTracker()
        tracker.record_response_time('/api/test', 'GET', 0.5, 200)
        
        percentiles = tracker.get_response_time_percentiles()
        assert len(percentiles) > 0
    
    def test_record_db_query_time(self):
        """Test recording database query times"""
        tracker = PerformanceTracker()
        tracker.record_db_query_time('SELECT', 'proposals', 0.1)
        
        percentiles = tracker.get_db_query_percentiles()
        assert len(percentiles) > 0
    
    def test_record_llm_call_time(self):
        """Test recording LLM call times"""
        tracker = PerformanceTracker()
        tracker.record_llm_call_time('openai', 'gpt-4', 2.5)
        
        percentiles = tracker.get_llm_call_percentiles()
        assert len(percentiles) > 0
    
    def test_get_response_time_percentiles(self):
        """Test getting response time percentiles"""
        tracker = PerformanceTracker()
        for i in range(100):
            tracker.record_response_time('/api/test', 'GET', 0.1 + i * 0.01, 200)
        
        percentiles = tracker.get_response_time_percentiles('/api/test')
        assert 'GET:/api/test' in percentiles or 'all' in percentiles
    
    def test_get_resource_usage(self):
        """Test getting resource usage"""
        tracker = PerformanceTracker()
        usage = tracker.get_resource_usage()
        
        assert 'cpu' in usage
        assert 'memory' in usage
        assert 'disk' in usage
        assert 'process_percent' in usage['cpu'] or 'system_percent' in usage['cpu']


class TestHealthChecker:
    """Tests for health checking"""
    
    def test_health_checker_creation(self):
        """Test health checker creation"""
        checker = HealthChecker()
        assert checker is not None
    
    def test_check_health(self):
        """Test checking system health"""
        checker = HealthChecker()
        health = checker.check_health()
        
        assert 'status' in health
        assert 'timestamp' in health
        assert 'components' in health
        assert health['status'] in ['healthy', 'degraded', 'unhealthy', 'unknown']
    
    def test_check_component(self):
        """Test checking individual component"""
        checker = HealthChecker()
        health = checker.check_component('system')
        
        assert health is not None
        assert health.name == 'system'
        assert health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, 
                                 HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]
    
    def test_is_ready(self):
        """Test readiness check"""
        checker = HealthChecker()
        assert checker.is_ready() in [True, False]
    
    def test_is_alive(self):
        """Test liveness check"""
        checker = HealthChecker()
        assert checker.is_alive() is True


class TestAlertManager:
    """Tests for alert management"""
    
    def test_alert_manager_creation(self):
        """Test alert manager creation"""
        manager = AlertManager()
        assert manager is not None
        assert len(manager.get_rules()) > 0  # Should have default rules
    
    def test_add_rule(self):
        """Test adding alert rules"""
        manager = AlertManager()
        from monitoring.alerts import AlertRule
        
        rule = AlertRule(
            name='test_rule',
            condition='error_count > 5',
            severity=AlertSeverity.WARNING,
            channels=[AlertChannel.EMAIL]
        )
        manager.add_rule(rule)
        
        rules = manager.get_rules()
        assert any(r.name == 'test_rule' for r in rules)
    
    def test_get_alert_statistics(self):
        """Test getting alert statistics"""
        manager = AlertManager()
        stats = manager.get_alert_statistics()
        
        assert 'total_alerts' in stats
        assert 'by_severity' in stats
        assert 'unacknowledged' in stats


class TestLoggingHelpers:
    """Tests for logging helper functions"""
    
    def test_log_function_call_decorator(self):
        """Test function call logging decorator"""
        @log_function_call('test', log_args=False, log_result=False)
        def test_function(x, y):
            return x + y
        
        result = test_function(1, 2)
        assert result == 3
    
    def test_log_performance_decorator(self):
        """Test performance logging decorator"""
        @log_performance(threshold_seconds=0.1)
        def slow_function():
            time.sleep(0.2)
            return "done"
        
        result = slow_function()
        assert result == "done"
    
    def test_log_context(self):
        """Test logging context manager"""
        with log_context('test_operation', 'test', test_key='test_value'):
            pass  # Operation completes successfully
    
    def test_performance_logger(self):
        """Test performance logger context manager"""
        with PerformanceLogger('test_operation', 'test') as logger:
            time.sleep(0.1)
        # Should complete without error


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

