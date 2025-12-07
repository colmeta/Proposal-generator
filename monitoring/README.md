# Monitoring & Analytics System

Comprehensive monitoring, logging, metrics, and analytics for the proposal generator application.

## Features

- **Structured Logging**: JSON-formatted logs with rotation and multiple handlers
- **Metrics Collection**: Prometheus-compatible metrics for application, performance, and business metrics
- **Error Tracking**: Automatic error capture, categorization, and frequency analysis
- **Usage Analytics**: User activity tracking, feature usage statistics, and proposal generation metrics
- **Performance Monitoring**: Response time tracking, database query performance, LLM API latency
- **Health Checks**: System and component health monitoring with readiness/liveness probes
- **Alert System**: Configurable alert rules with email and webhook notifications
- **Dashboard**: Real-time monitoring dashboard with metrics visualization

## Quick Start

### 1. Setup Logging

```python
from monitoring import setup_logging, get_logger

# Initialize logging
setup_logging(log_level='INFO', log_dir='logs')

# Get a logger
logger = get_logger('my_module')
logger.info("Application started")
```

### 2. Track Metrics

```python
from monitoring import get_metrics_collector

metrics = get_metrics_collector()

# Record HTTP request
metrics.record_request('GET', '/api/proposals', 200, 0.5)

# Record proposal generation
metrics.record_proposal_generation('gates_foundation', 'success', 10.5)

# Record LLM API call
metrics.record_llm_call('openai', 'gpt-4', 'success', 2.5, tokens_prompt=100, tokens_completion=50)
```

### 3. Track Errors

```python
from monitoring import get_error_tracker

error_tracker = get_error_tracker()

try:
    # Your code here
    pass
except Exception as e:
    error_tracker.capture_error(e, 'proposal_service', {'proposal_id': '123'})
    raise
```

Or use the decorator:

```python
from monitoring.error_tracker import track_error

@track_error('proposal_service')
def generate_proposal():
    # Your code here
    pass
```

### 4. Track Analytics

```python
from monitoring import get_analytics_collector

analytics = get_analytics_collector()

# Track user activity
analytics.track_activity(
    'proposal_view',
    'proposal_service',
    user_id='user123',
    metadata={'proposal_id': 'prop1'}
)

# Track proposal generation
analytics.track_proposal_generation(
    'gates_foundation',
    'success',
    generation_time=15.5,
    sections_count=10,
    word_count=5000
)
```

### 5. Monitor Performance

```python
from monitoring import get_performance_tracker

perf = get_performance_tracker()

# Record response time
perf.record_response_time('/api/proposals', 'GET', 0.5, 200)

# Get percentiles
percentiles = perf.get_response_time_percentiles()
print(f"P95 response time: {percentiles['all']['p95']}s")

# Get resource usage
usage = perf.get_resource_usage()
print(f"CPU: {usage['cpu']['process_percent']}%")
print(f"Memory: {usage['memory']['process_rss_mb']}MB")
```

### 6. Health Checks

```python
from monitoring import get_health_checker

health = get_health_checker()

# Check overall health
status = health.check_health()
print(f"System status: {status['status']}")

# Check specific component
component_health = health.check_component('memory')
print(f"Memory status: {component_health.status}")

# Readiness/liveness probes
if health.is_ready():
    print("System is ready")
```

### 7. Using Logging Helpers

```python
from utils.logging_helpers import log_function_call, log_performance, log_context

# Log function calls
@log_function_call('my_module', log_args=True)
def my_function(x, y):
    return x + y

# Log slow functions
@log_performance(threshold_seconds=1.0)
def slow_operation():
    time.sleep(2)

# Context manager for operations
with log_context('proposal_generation', 'proposal_service', proposal_id='123'):
    # Your code here
    pass
```

## Flask Integration

### Register Dashboard Blueprint

```python
from flask import Flask
from monitoring.dashboard import get_dashboard

app = Flask(__name__)
dashboard = get_dashboard()
app.register_blueprint(dashboard.blueprint)

# Access dashboard at /api/monitoring/dashboard
# Metrics endpoint at /api/monitoring/metrics
```

### Request Logging Middleware

```python
from flask import request, g
from monitoring import get_logger, get_metrics_collector, get_performance_tracker
import time

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    
    # Log request
    logger = get_logger('flask')
    logger.info(f"{request.method} {request.path} - {response.status_code}")
    
    # Record metrics
    metrics = get_metrics_collector()
    metrics.record_request(request.method, request.path, response.status_code, duration)
    
    # Record performance
    perf = get_performance_tracker()
    perf.record_response_time(request.path, request.method, duration, response.status_code)
    
    return response
```

## Environment Variables

```bash
# Logging
LOG_DIR=logs
LOG_LEVEL=INFO
ENABLE_JSON_LOGGING=true
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Alerts
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_password
ALERT_FROM_EMAIL=alerts@yourapp.com
ALERT_TO_EMAILS=admin@yourapp.com
ALERT_WEBHOOK_URL=https://your-webhook-url.com/alerts
```

## API Endpoints

When the dashboard blueprint is registered:

- `GET /api/monitoring/dashboard` - Monitoring dashboard HTML
- `GET /api/monitoring/health` - System health status
- `GET /api/monitoring/metrics` - Prometheus metrics
- `GET /api/monitoring/performance` - Performance metrics
- `GET /api/monitoring/errors` - Error statistics
- `GET /api/monitoring/analytics` - Analytics data
- `GET /api/monitoring/summary` - Summary of all metrics

## Testing

Run the monitoring tests:

```bash
pytest tests/test_monitoring.py -v
```

## Dependencies

- `prometheus-client` - Metrics collection
- `python-json-logger` - Structured JSON logging
- `psutil` - System resource monitoring
- `sentry-sdk` - Error tracking (optional)

Install with:

```bash
pip install -r requirements.txt
```



