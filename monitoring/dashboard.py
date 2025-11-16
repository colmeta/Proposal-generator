"""Monitoring dashboard for real-time metrics display"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, render_template_string
from .metrics import get_metrics_collector
from .error_tracker import get_error_tracker
from .analytics import get_analytics_collector
from .performance_tracker import get_performance_tracker
from .health_check import get_health_checker


# Dashboard HTML template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #2c3e50; }
        .metric { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
        .metric:last-child { border-bottom: none; }
        .metric-label { font-weight: bold; }
        .metric-value { color: #3498db; }
        .status-healthy { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-error { color: #e74c3c; }
        .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #2980b9; }
    </style>
    <script>
        function refreshDashboard() {
            location.reload();
        }
        setInterval(refreshDashboard, 30000); // Auto-refresh every 30 seconds
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Monitoring Dashboard</h1>
            <button class="refresh-btn" onclick="refreshDashboard()">Refresh</button>
        </div>
        <div class="grid">
            <div class="card">
                <h3>System Health</h3>
                <div id="health-status">Loading...</div>
            </div>
            <div class="card">
                <h3>Performance Metrics</h3>
                <div id="performance-metrics">Loading...</div>
            </div>
            <div class="card">
                <h3>Error Statistics</h3>
                <div id="error-stats">Loading...</div>
            </div>
            <div class="card">
                <h3>Usage Analytics</h3>
                <div id="analytics">Loading...</div>
            </div>
        </div>
    </div>
    <script>
        // Load data via API endpoints
        fetch('/api/monitoring/health')
            .then(r => r.json())
            .then(data => {
                const status = data.status === 'healthy' ? 'status-healthy' : 'status-error';
                document.getElementById('health-status').innerHTML = 
                    `<div class="metric"><span class="metric-label">Status:</span><span class="metric-value ${status}">${data.status}</span></div>`;
            });
        
        fetch('/api/monitoring/performance')
            .then(r => r.json())
            .then(data => {
                let html = '';
                if (data.response_times) {
                    const rt = data.response_times.all || {};
                    html += `<div class="metric"><span class="metric-label">Avg Response Time:</span><span class="metric-value">${(rt.avg || 0).toFixed(3)}s</span></div>`;
                    html += `<div class="metric"><span class="metric-label">P95 Response Time:</span><span class="metric-value">${(rt.p95 || 0).toFixed(3)}s</span></div>`;
                }
                document.getElementById('performance-metrics').innerHTML = html;
            });
        
        fetch('/api/monitoring/errors')
            .then(r => r.json())
            .then(data => {
                let html = '';
                html += `<div class="metric"><span class="metric-label">Total Errors:</span><span class="metric-value">${data.total_errors || 0}</span></div>`;
                html += `<div class="metric"><span class="metric-label">Unique Errors:</span><span class="metric-value">${data.unique_errors || 0}</span></div>`;
                document.getElementById('error-stats').innerHTML = html;
            });
        
        fetch('/api/monitoring/analytics')
            .then(r => r.json())
            .then(data => {
                let html = '';
                if (data.proposal_stats) {
                    html += `<div class="metric"><span class="metric-label">Total Proposals:</span><span class="metric-value">${data.proposal_stats.total_proposals || 0}</span></div>`;
                    html += `<div class="metric"><span class="metric-label">Success Rate:</span><span class="metric-value">${(data.proposal_stats.success_rate || 0).toFixed(1)}%</span></div>`;
                }
                document.getElementById('analytics').innerHTML = html;
            });
    </script>
</body>
</html>
"""


class MonitoringDashboard:
    """Monitoring dashboard manager"""
    
    def __init__(self):
        self.blueprint = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup dashboard API routes"""
        
        @self.blueprint.route('/dashboard')
        def dashboard():
            """Render dashboard HTML"""
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.blueprint.route('/health')
        def health():
            """Get health status"""
            checker = get_health_checker()
            status = checker.check_health()
            return jsonify(status)
        
        @self.blueprint.route('/metrics')
        def metrics():
            """Get Prometheus metrics"""
            collector = get_metrics_collector()
            return collector.get_metrics(), 200, {'Content-Type': 'text/plain'}
        
        @self.blueprint.route('/performance')
        def performance():
            """Get performance metrics"""
            tracker = get_performance_tracker()
            return jsonify({
                'response_times': tracker.get_response_time_percentiles(),
                'db_queries': tracker.get_db_query_percentiles(),
                'llm_calls': tracker.get_llm_call_percentiles(),
                'resource_usage': tracker.get_resource_usage()
            })
        
        @self.blueprint.route('/errors')
        def errors():
            """Get error statistics"""
            tracker = get_error_tracker()
            return jsonify(tracker.get_error_statistics())
        
        @self.blueprint.route('/analytics')
        def analytics():
            """Get analytics data"""
            collector = get_analytics_collector()
            return jsonify({
                'feature_usage': collector.get_feature_usage_stats(),
                'proposal_stats': collector.get_proposal_statistics(),
                'popular_funders': collector.get_popular_funders(),
                'time_to_completion': collector.get_time_to_completion_stats()
            })
        
        @self.blueprint.route('/summary')
        def summary():
            """Get summary of all metrics"""
            metrics_collector = get_metrics_collector()
            error_tracker = get_error_tracker()
            analytics_collector = get_analytics_collector()
            performance_tracker = get_performance_tracker()
            health_checker = get_health_checker()
            
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'health': health_checker.check_health(),
                'performance': {
                    'response_times': performance_tracker.get_response_time_percentiles(),
                    'resource_usage': performance_tracker.get_resource_usage()
                },
                'errors': error_tracker.get_error_statistics(),
                'analytics': {
                    'feature_usage': analytics_collector.get_feature_usage_stats(),
                    'proposal_stats': analytics_collector.get_proposal_statistics()
                }
            })


def get_dashboard() -> MonitoringDashboard:
    """Get the monitoring dashboard instance"""
    return MonitoringDashboard()

