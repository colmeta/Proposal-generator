"""
Audit Log Service
Security event logging, user action tracking, data access logging
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Audit event types"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"
    PERMISSION_CHANGE = "permission_change"
    USER_ACTION = "user_action"


class AuditLogService:
    """
    Audit logging service for security and compliance
    """
    
    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize audit log service
        
        Args:
            log_file: Path to audit log file (optional)
        """
        if log_file is None:
            from config.settings import LOGS_DIR
            log_file = LOGS_DIR / "audit.log"
        
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.retention_days = 365  # Keep audit logs for 1 year
        logger.info(f"AuditLogService initialized: {log_file}")
    
    def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ):
        """
        Log an audit event
        
        Args:
            event_type: Type of audit event
            user_id: User ID (None for system events)
            action: Action performed
            resource_type: Type of resource accessed
            resource_id: ID of resource accessed
            details: Additional details
            ip_address: IP address of requester
            user_agent: User agent string
            success: Whether action was successful
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "details": details or {}
        }
        
        # Write to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
        
        # Also log to application logger
        log_level = logging.INFO if success else logging.WARNING
        logger.log(
            log_level,
            f"Audit: {event_type.value} | User: {user_id} | Action: {action} | Success: {success}"
        )
    
    def log_authentication(self, user_id: str, success: bool, ip_address: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log authentication event"""
        self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            user_id=user_id,
            action="login" if success else "login_failed",
            ip_address=ip_address,
            success=success,
            details=details
        )
    
    def log_authorization(self, user_id: str, action: str, resource_type: str, resource_id: str, success: bool):
        """Log authorization event"""
        self.log_event(
            event_type=AuditEventType.AUTHORIZATION,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success
        )
    
    def log_data_access(self, user_id: str, resource_type: str, resource_id: str, ip_address: Optional[str] = None):
        """Log data access event"""
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            user_id=user_id,
            action="read",
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            success=True
        )
    
    def log_data_modification(self, user_id: str, resource_type: str, resource_id: str, changes: Dict[str, Any]):
        """Log data modification event"""
        self.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            user_id=user_id,
            action="update",
            resource_type=resource_type,
            resource_id=resource_id,
            details={"changes": changes},
            success=True
        )
    
    def log_data_deletion(self, user_id: str, resource_type: str, resource_id: str):
        """Log data deletion event"""
        self.log_event(
            event_type=AuditEventType.DATA_DELETION,
            user_id=user_id,
            action="delete",
            resource_type=resource_type,
            resource_id=resource_id,
            success=True
        )
    
    def log_configuration_change(self, user_id: str, config_key: str, old_value: Any, new_value: Any):
        """Log configuration change"""
        self.log_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            user_id=user_id,
            action="config_change",
            resource_type="configuration",
            resource_id=config_key,
            details={"old_value": str(old_value), "new_value": str(new_value)},
            success=True
        )
    
    def log_security_event(self, event_description: str, severity: str = "medium", details: Optional[Dict[str, Any]] = None):
        """Log security event"""
        self.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            user_id=None,  # System event
            action=event_description,
            details={"severity": severity, **(details or {})},
            success=False  # Security events are typically negative
        )
    
    def query_audit_log(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit log
        
        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of results
        
        Returns:
            List of audit log entries
        """
        if not self.log_file.exists():
            return []
        
        results = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        
                        # Apply filters
                        if user_id and event.get("user_id") != user_id:
                            continue
                        if event_type and event.get("event_type") != event_type.value:
                            continue
                        
                        event_time = datetime.fromisoformat(event["timestamp"])
                        if start_date and event_time < start_date:
                            continue
                        if end_date and event_time > end_date:
                            continue
                        
                        results.append(event)
                        
                        if len(results) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
            
            # Sort by timestamp (newest first)
            results.sort(key=lambda x: x["timestamp"], reverse=True)
            return results
        except Exception as e:
            logger.error(f"Failed to query audit log: {e}")
            return []
    
    def cleanup_old_logs(self):
        """Clean up audit logs older than retention period"""
        if not self.log_file.exists():
            return
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        cutoff_str = cutoff_date.isoformat()
        
        try:
            # Read all logs
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter out old logs
            kept_lines = [
                line for line in lines
                if line.strip() and json.loads(line.strip()).get("timestamp", "") >= cutoff_str
            ]
            
            # Write back
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.writelines(kept_lines)
            
            logger.info(f"Cleaned up audit logs older than {self.retention_days} days")
        except Exception as e:
            logger.error(f"Failed to cleanup audit logs: {e}")


# Global instance
audit_log_service = AuditLogService()

