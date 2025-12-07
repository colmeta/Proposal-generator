"""Alert system with configurable rules and channels"""
import os
import smtplib
import requests
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from threading import Lock
import json


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert notification channels"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"


@dataclass
class AlertRule:
    """Represents an alert rule"""
    name: str
    condition: str  # e.g., "error_count > 10"
    severity: AlertSeverity
    channels: List[AlertChannel]
    enabled: bool = True
    cooldown_minutes: int = 60
    last_triggered: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['channels'] = [c.value for c in self.channels]
        if self.last_triggered:
            data['last_triggered'] = self.last_triggered.isoformat()
        return data


@dataclass
class Alert:
    """Represents an alert"""
    rule_name: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    metadata: Dict[str, Any]
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self._rules: Dict[str, AlertRule] = {}
        self._alerts: List[Alert] = []
        self._lock = Lock()
        self._setup_default_rules()
        
        # Configuration
        self.email_config = {
            'smtp_server': os.getenv('ALERT_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('ALERT_SMTP_PORT', '587')),
            'username': os.getenv('ALERT_EMAIL_USERNAME', ''),
            'password': os.getenv('ALERT_EMAIL_PASSWORD', ''),
            'from_email': os.getenv('ALERT_FROM_EMAIL', ''),
            'to_emails': os.getenv('ALERT_TO_EMAILS', '').split(',')
        }
        
        self.webhook_url = os.getenv('ALERT_WEBHOOK_URL', '')
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        default_rules = [
            AlertRule(
                name='high_error_rate',
                condition='error_count > 50',
                severity=AlertSeverity.ERROR,
                channels=[AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                cooldown_minutes=60
            ),
            AlertRule(
                name='critical_error',
                condition='critical_error_count > 0',
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                cooldown_minutes=0
            ),
            AlertRule(
                name='high_response_time',
                condition='p95_response_time > 5.0',
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=120
            ),
            AlertRule(
                name='high_cpu_usage',
                condition='cpu_percent > 80',
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=60
            ),
            AlertRule(
                name='high_memory_usage',
                condition='memory_percent > 85',
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=60
            ),
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule"""
        with self._lock:
            self._rules[rule.name] = rule
    
    def remove_rule(self, rule_name: str) -> None:
        """Remove an alert rule"""
        with self._lock:
            if rule_name in self._rules:
                del self._rules[rule_name]
    
    def get_rules(self) -> List[AlertRule]:
        """Get all alert rules"""
        with self._lock:
            return list(self._rules.values())
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check all alert rules against current metrics"""
        triggered_alerts = []
        
        with self._lock:
            for rule in self._rules.values():
                if not rule.enabled:
                    continue
                
                # Check cooldown
                if rule.last_triggered:
                    cooldown_end = rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)
                    if datetime.utcnow() < cooldown_end:
                        continue
                
                # Evaluate condition
                if self._evaluate_condition(rule.condition, metrics):
                    alert = Alert(
                        rule_name=rule.name,
                        message=f"Alert triggered: {rule.name}",
                        severity=rule.severity,
                        timestamp=datetime.utcnow(),
                        metadata={'condition': rule.condition, 'metrics': metrics}
                    )
                    
                    triggered_alerts.append(alert)
                    self._alerts.append(alert)
                    
                    # Update last triggered
                    rule.last_triggered = datetime.utcnow()
                    
                    # Send notifications
                    self._send_notifications(alert, rule.channels)
        
        return triggered_alerts
    
    def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert condition (simplified - in production use a proper expression evaluator)"""
        try:
            # Simple condition evaluation
            # Replace metric names with values
            for key, value in metrics.items():
                condition = condition.replace(key, str(value))
            
            # Evaluate (this is simplified - use ast.literal_eval or a proper library in production)
            return eval(condition)
        except Exception:
            return False
    
    def _send_notifications(self, alert: Alert, channels: List[AlertChannel]) -> None:
        """Send alert notifications through configured channels"""
        for channel in channels:
            try:
                if channel == AlertChannel.EMAIL:
                    self._send_email(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_webhook(alert)
                elif channel == AlertChannel.LOG:
                    self._log_alert(alert)
            except Exception as e:
                # Log notification failure but don't raise
                print(f"Failed to send alert via {channel.value}: {e}")
    
    def _send_email(self, alert: Alert) -> None:
        """Send alert via email"""
        if not self.email_config['from_email'] or not self.email_config['to_emails']:
            return
        
        try:
            msg = f"""Subject: [{alert.severity.value.upper()}] {alert.message}

Alert Details:
- Rule: {alert.rule_name}
- Severity: {alert.severity.value}
- Time: {alert.timestamp.isoformat()}
- Message: {alert.message}

Metadata: {json.dumps(alert.metadata, indent=2)}
"""
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                if self.email_config['username']:
                    server.login(self.email_config['username'], self.email_config['password'])
                server.sendmail(
                    self.email_config['from_email'],
                    self.email_config['to_emails'],
                    msg
                )
        except Exception as e:
            print(f"Email send failed: {e}")
    
    def _send_webhook(self, alert: Alert) -> None:
        """Send alert via webhook"""
        if not self.webhook_url:
            return
        
        try:
            payload = alert.to_dict()
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as e:
            print(f"Webhook send failed: {e}")
    
    def _log_alert(self, alert: Alert) -> None:
        """Log alert"""
        print(f"[ALERT] {alert.severity.value.upper()}: {alert.message} (Rule: {alert.rule_name})")
    
    def get_alerts(self, 
                   severity: Optional[AlertSeverity] = None,
                   limit: int = 100,
                   unacknowledged_only: bool = False) -> List[Alert]:
        """Get alerts with optional filtering"""
        with self._lock:
            alerts = self._alerts.copy()
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        
        # Sort by timestamp
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return alerts[:limit]
    
    def acknowledge_alert(self, alert_index: int) -> bool:
        """Acknowledge an alert"""
        with self._lock:
            if 0 <= alert_index < len(self._alerts):
                self._alerts[alert_index].acknowledged = True
                return True
        return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        with self._lock:
            total = len(self._alerts)
            by_severity = {}
            for severity in AlertSeverity:
                by_severity[severity.value] = len([a for a in self._alerts if a.severity == severity])
            
            unacknowledged = len([a for a in self._alerts if not a.acknowledged])
            
            recent_alerts = [
                a for a in self._alerts
                if a.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ]
        
        return {
            'total_alerts': total,
            'by_severity': by_severity,
            'unacknowledged': unacknowledged,
            'recent_24h': len(recent_alerts)
        }


# Global alert manager instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager



