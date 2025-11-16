"""Logging helper functions with decorators and context managers"""
import time
import functools
from typing import Callable, Any, Optional, Dict
from contextlib import contextmanager
from monitoring.logging_config import get_logger


def log_function_call(logger_name: str = 'root', log_args: bool = False, log_result: bool = False):
    """Decorator to log function calls"""
    def decorator(func: Callable) -> Callable:
        logger = get_logger(logger_name)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Log entry
            if log_args:
                logger.info(
                    f"Calling {func_name}",
                    extra={'args': str(args)[:200], 'kwargs': str(kwargs)[:200]}
                )
            else:
                logger.debug(f"Calling {func_name}")
            
            # Execute function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                if log_result:
                    logger.info(
                        f"{func_name} completed in {duration:.3f}s",
                        extra={'result': str(result)[:200] if result else None}
                    )
                else:
                    logger.debug(f"{func_name} completed in {duration:.3f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{func_name} failed after {duration:.3f}s: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_performance(threshold_seconds: float = 1.0, logger_name: str = 'root'):
    """Decorator to log slow function calls"""
    def decorator(func: Callable) -> Callable:
        logger = get_logger(logger_name)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if duration > threshold_seconds:
                    logger.warning(
                        f"Slow function: {func.__name__} took {duration:.3f}s (threshold: {threshold_seconds}s)"
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator


@contextmanager
def log_context(operation: str, logger_name: str = 'root', **context: Any):
    """Context manager for logging operations with context"""
    logger = get_logger(logger_name)
    start_time = time.time()
    
    logger.info(f"Starting {operation}", extra={'context': context})
    
    try:
        yield
        duration = time.time() - start_time
        logger.info(f"Completed {operation} in {duration:.3f}s", extra={'context': context})
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Failed {operation} after {duration:.3f}s: {str(e)}",
            extra={'context': context},
            exc_info=True
        )
        raise


@contextmanager
def request_logger(request_id: str, user_id: Optional[str] = None, logger_name: str = 'root'):
    """Context manager for request logging"""
    logger = get_logger(logger_name)
    
    # Add request context
    import logging
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.request_id = request_id
        if user_id:
            record.user_id = user_id
        return record
    
    logging.setLogRecordFactory(record_factory)
    
    logger.info(f"Request started: {request_id}", extra={'user_id': user_id})
    
    try:
        yield logger
        logger.info(f"Request completed: {request_id}")
    except Exception as e:
        logger.error(f"Request failed: {request_id} - {str(e)}", exc_info=True)
        raise
    finally:
        logging.setLogRecordFactory(old_factory)


def log_exception(logger_name: str = 'root', reraise: bool = True):
    """Decorator to log exceptions"""
    def decorator(func: Callable) -> Callable:
        logger = get_logger(logger_name)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}: {str(e)}",
                    exc_info=True
                )
                if reraise:
                    raise
                return None
        
        return wrapper
    return decorator


class PerformanceLogger:
    """Context manager for detailed performance logging"""
    
    def __init__(self, operation: str, logger_name: str = 'root', log_args: bool = False):
        self.operation = operation
        self.logger = get_logger(logger_name)
        self.log_args = log_args
        self.start_time = None
        self.args = None
        self.kwargs = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"{self.operation} completed in {duration:.3f}s",
                extra={'duration': duration}
            )
        else:
            self.logger.error(
                f"{self.operation} failed after {duration:.3f}s: {str(exc_val)}",
                exc_info=(exc_type, exc_val, exc_tb)
            )
        
        return False  # Don't suppress exceptions
    
    def set_args(self, *args, **kwargs):
        """Set function arguments for logging"""
        if self.log_args:
            self.args = args
            self.kwargs = kwargs


def log_metric(metric_name: str, value: float, logger_name: str = 'root', **tags: str):
    """Log a metric value"""
    logger = get_logger(logger_name)
    logger.info(
        f"Metric: {metric_name} = {value}",
        extra={'metric_name': metric_name, 'metric_value': value, 'tags': tags}
    )

