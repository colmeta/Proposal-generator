"""Error tracking and reporting with categorization and alerting"""
import traceback
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass, asdict
import json


@dataclass
class ErrorRecord:
    """Represents an error record"""
    error_type: str
    error_message: str
    component: str
    stack_trace: str
    context: Dict[str, Any]
    timestamp: datetime
    frequency: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ErrorTracker:
    """Error tracking and analysis"""
    
    def __init__(self, max_errors: int = 10000):
        self.max_errors = max_errors
        self._errors: List[ErrorRecord] = []
        self._error_frequency: Dict[str, int] = defaultdict(int)
        self._error_by_type: Dict[str, List[ErrorRecord]] = defaultdict(list)
        self._error_by_component: Dict[str, List[ErrorRecord]] = defaultdict(list)
        self._lock = Lock()
        
    def capture_error(self, error: Exception, component: str, context: Optional[Dict[str, Any]] = None) -> ErrorRecord:
        """Capture an error with context"""
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        
        context = context or {}
        
        # Create error record
        error_record = ErrorRecord(
            error_type=error_type,
            error_message=error_message,
            component=component,
            stack_trace=stack_trace,
            context=context,
            timestamp=datetime.utcnow()
        )
        
        with self._lock:
            # Check if similar error exists
            error_key = f"{error_type}:{component}:{error_message[:100]}"
            
            if error_key in self._error_frequency:
                # Update frequency
                self._error_frequency[error_key] += 1
                # Find and update existing record
                for existing in self._errors:
                    if (existing.error_type == error_type and 
                        existing.component == component and
                        existing.error_message == error_message):
                        existing.frequency = self._error_frequency[error_key]
                        break
            else:
                # New error
                self._error_frequency[error_key] = 1
                self._errors.append(error_record)
                
                # Categorize
                self._error_by_type[error_type].append(error_record)
                self._error_by_component[component].append(error_record)
                
                # Limit storage
                if len(self._errors) > self.max_errors:
                    oldest = self._errors.pop(0)
                    self._error_by_type[oldest.error_type].remove(oldest)
                    self._error_by_component[oldest.component].remove(oldest)
        
        return error_record
    
    def get_errors(self, 
                   error_type: Optional[str] = None,
                   component: Optional[str] = None,
                   limit: int = 100) -> List[ErrorRecord]:
        """Get errors with optional filtering"""
        with self._lock:
            errors = self._errors.copy()
        
        if error_type:
            errors = [e for e in errors if e.error_type == error_type]
        
        if component:
            errors = [e for e in errors if e.component == component]
        
        # Sort by frequency and timestamp
        errors.sort(key=lambda x: (x.frequency, x.timestamp), reverse=True)
        
        return errors[:limit]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self._lock:
            total_errors = sum(self._error_frequency.values())
            unique_errors = len(self._error_frequency)
            
            errors_by_type = {
                error_type: len(errors) 
                for error_type, errors in self._error_by_type.items()
            }
            
            errors_by_component = {
                component: len(errors)
                for component, errors in self._error_by_component.items()
            }
            
            top_errors = sorted(
                self._error_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        
        return {
            'total_errors': total_errors,
            'unique_errors': unique_errors,
            'errors_by_type': errors_by_type,
            'errors_by_component': errors_by_component,
            'top_errors': [
                {'key': key, 'frequency': freq}
                for key, freq in top_errors
            ]
        }
    
    def get_errors_by_type(self, error_type: str) -> List[ErrorRecord]:
        """Get all errors of a specific type"""
        with self._lock:
            return self._error_by_type.get(error_type, []).copy()
    
    def get_errors_by_component(self, component: str) -> List[ErrorRecord]:
        """Get all errors from a specific component"""
        with self._lock:
            return self._error_by_component.get(component, []).copy()
    
    def get_recent_errors(self, hours: int = 24) -> List[ErrorRecord]:
        """Get errors from the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            return [e for e in self._errors if e.timestamp >= cutoff]
    
    def clear_errors(self) -> None:
        """Clear all error records"""
        with self._lock:
            self._errors.clear()
            self._error_frequency.clear()
            self._error_by_type.clear()
            self._error_by_component.clear()
    
    def export_errors(self, filepath: str) -> None:
        """Export errors to JSON file"""
        with self._lock:
            errors_data = [e.to_dict() for e in self._errors]
        
        with open(filepath, 'w') as f:
            json.dump(errors_data, f, indent=2, default=str)


# Global error tracker instance
_error_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker instance"""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


def track_error(component: str, context: Optional[Dict[str, Any]] = None):
    """Decorator to automatically track errors"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                tracker = get_error_tracker()
                tracker.capture_error(e, component, context)
                raise
        return wrapper
    return decorator

