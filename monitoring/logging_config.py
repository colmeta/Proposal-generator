"""Advanced logging configuration with structured logging, rotation, and aggregation"""
import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from pythonjsonlogger import jsonlogger


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add module and function info
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add process and thread info
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        # Add any extra context
        if hasattr(record, 'context'):
            log_record['context'] = record.context


class LoggingConfig:
    """Centralized logging configuration"""
    
    def __init__(self):
        self.log_dir = Path(os.getenv('LOG_DIR', 'logs'))
        self.log_dir.mkdir(exist_ok=True)
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.enable_json = os.getenv('ENABLE_JSON_LOGGING', 'true').lower() == 'true'
        self.max_bytes = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
        self.backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
    def setup_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """Setup a logger with configured handlers"""
        logger = logging.getLogger(name)
        
        if logger.handlers:
            return logger  # Already configured
        
        logger.setLevel(getattr(logging, level or self.log_level))
        logger.propagate = False
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        if self.enable_json:
            console_formatter = StructuredFormatter()
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = self.log_dir / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        
        if self.enable_json:
            file_formatter = StructuredFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
            )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_log_file = self.log_dir / f"{name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        return logger


# Global configuration instance
_config = LoggingConfig()


def setup_logging(log_level: Optional[str] = None, log_dir: Optional[str] = None) -> None:
    """Setup root logging configuration"""
    if log_dir:
        _config.log_dir = Path(log_dir)
        _config.log_dir.mkdir(exist_ok=True)
    if log_level:
        _config.log_level = log_level.upper()
    
    root_logger = _config.setup_logger('root')
    logging.root = root_logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance"""
    return _config.setup_logger(name, level)


def add_context(logger: logging.Logger, **context: Any) -> logging.Logger:
    """Add context to logger for structured logging"""
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.context = context
        return record
    
    logging.setLogRecordFactory(record_factory)
    return logger



