"""Request logging middleware for performance metrics and audit logs"""
import logging
import time
import json
from typing import Dict, Optional
from datetime import datetime
from flask import request, g, current_app
from functools import wraps

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger('audit')
performance_logger = logging.getLogger('performance')


class LoggingMiddleware:
    """Middleware for request/response logging, performance metrics, and audit logs"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize logging middleware with Flask app"""
        @app.before_request
        def before_request():
            """Log request start and set start time"""
            g.start_time = time.time()
            g.request_id = self._generate_request_id()
            
            # Log request details
            if app.config.get('LOG_REQUESTS', True):
                logger.info(
                    f"Request started: {request.method} {request.path}",
                    extra={
                        'request_id': g.request_id,
                        'method': request.method,
                        'path': request.path,
                        'remote_addr': request.remote_addr,
                        'user_agent': request.headers.get('User-Agent'),
                        'user_id': getattr(g, 'user_id', None)
                    }
                )
        
        @app.after_request
        def after_request(response):
            """Log response and performance metrics"""
            # Calculate request duration
            duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0
            
            # Log performance metrics
            if app.config.get('LOG_PERFORMANCE', True):
                performance_logger.info(
                    f"Request completed: {request.method} {request.path}",
                    extra={
                        'request_id': getattr(g, 'request_id', None),
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'duration_ms': duration * 1000,
                        'response_size': len(response.get_data()),
                        'user_id': getattr(g, 'user_id', None)
                    }
                )
            
            # Log audit trail for important actions
            if app.config.get('LOG_AUDIT', True):
                if self._should_audit_log(request, response):
                    audit_logger.info(
                        f"Audit: {request.method} {request.path}",
                        extra={
                            'request_id': getattr(g, 'request_id', None),
                            'method': request.method,
                            'path': request.path,
                            'status_code': response.status_code,
                            'user_id': getattr(g, 'user_id', None),
                            'remote_addr': request.remote_addr,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    )
            
            # Add request ID to response headers
            if hasattr(g, 'request_id'):
                response.headers['X-Request-ID'] = g.request_id
            
            # Add performance headers
            if app.config.get('LOG_PERFORMANCE', True):
                response.headers['X-Response-Time'] = f"{duration * 1000:.2f}ms"
            
            return response
        
        @app.errorhandler(Exception)
        def handle_exception(e):
            """Log exceptions"""
            logger.error(
                f"Exception occurred: {str(e)}",
                exc_info=True,
                extra={
                    'request_id': getattr(g, 'request_id', None),
                    'method': request.method,
                    'path': request.path,
                    'user_id': getattr(g, 'user_id', None)
                }
            )
            raise
    
    def _should_audit_log(self, request, response) -> bool:
        """Determine if request should be audit logged"""
        # Log POST, PUT, DELETE, PATCH requests
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return True
        
        # Log sensitive GET requests
        sensitive_paths = ['/api/users', '/api/auth', '/api/admin']
        if request.method == 'GET' and any(path in request.path for path in sensitive_paths):
            return True
        
        # Log error responses
        if response.status_code >= 400:
            return True
        
        return False
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID"""
        import uuid
        return str(uuid.uuid4())


def log_performance(func):
    """Decorator to log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            performance_logger.debug(
                f"Function {func.__name__} completed",
                extra={
                    'function': func.__name__,
                    'duration_ms': duration * 1000
                }
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed",
                exc_info=True,
                extra={
                    'function': func.__name__,
                    'duration_ms': duration * 1000,
                    'error': str(e)
                }
            )
            raise
    return wrapper


def log_audit(action: str):
    """Decorator to log audit events"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = getattr(g, 'user_id', None)
            audit_logger.info(
                f"Audit: {action}",
                extra={
                    'action': action,
                    'function': func.__name__,
                    'user_id': user_id,
                    'request_id': getattr(g, 'request_id', None),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def setup_logging_middleware(app):
    """Setup logging middleware for Flask app"""
    # Configure loggers
    if not app.config.get('TESTING', False):
        # Request logger
        request_handler = logging.StreamHandler()
        request_handler.setLevel(logging.INFO)
        request_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(request_id)s'
        )
        request_handler.setFormatter(request_formatter)
        logger.addHandler(request_handler)
        
        # Performance logger
        perf_handler = logging.StreamHandler()
        perf_handler.setLevel(logging.INFO)
        perf_formatter = logging.Formatter(
            '%(asctime)s - PERFORMANCE - %(message)s - Duration: %(duration_ms).2fms'
        )
        perf_handler.setFormatter(perf_formatter)
        performance_logger.addHandler(perf_handler)
        
        # Audit logger
        audit_handler = logging.StreamHandler()
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s - User: %(user_id)s - %(request_id)s'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
    
    # Initialize middleware
    LoggingMiddleware(app)
    logger.info("Logging middleware configured")

