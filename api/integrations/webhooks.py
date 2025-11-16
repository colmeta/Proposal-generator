"""Webhook system for event notifications"""
import hmac
import hashlib
import json
import time
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import requests
from flask import current_app
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)
Base = declarative_base()


class WebhookEventType(str, Enum):
    """Webhook event types"""
    JOB_CREATED = "job.created"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_UPDATED = "job.updated"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    DOCUMENT_GENERATED = "document.generated"
    ERROR_OCCURRED = "error.occurred"


class WebhookEvent:
    """Represents a webhook event"""
    
    def __init__(self, event_type: WebhookEventType, data: Dict, timestamp: Optional[datetime] = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.id = f"{int(time.time() * 1000)}"
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class WebhookDelivery(Base):
    """Database model for webhook deliveries"""
    __tablename__ = 'webhook_deliveries'
    
    id = Column(Integer, primary_key=True)
    webhook_id = Column(Integer, nullable=False)
    event_id = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # pending, success, failed
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    next_retry_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)


class WebhookRegistration(Base):
    """Database model for webhook registrations"""
    __tablename__ = 'webhook_registrations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)
    event_types = Column(JSON, nullable=False)  # List of event types to subscribe to
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebhookManager:
    """Manages webhook registrations and deliveries"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.retry_delays = [60, 300, 900]  # 1min, 5min, 15min
    
    def register_webhook(
        self,
        user_id: int,
        url: str,
        event_types: List[WebhookEventType],
        secret: Optional[str] = None
    ) -> WebhookRegistration:
        """Register a new webhook"""
        if secret is None:
            secret = self._generate_secret()
        
        webhook = WebhookRegistration(
            user_id=user_id,
            url=url,
            secret=secret,
            event_types=[et.value for et in event_types],
            active=True
        )
        
        if self.db_session:
            self.db_session.add(webhook)
            self.db_session.commit()
        
        logger.info(f"Webhook registered: {webhook.id} for user {user_id}")
        return webhook
    
    def unregister_webhook(self, webhook_id: int) -> bool:
        """Unregister a webhook"""
        if not self.db_session:
            return False
        
        webhook = self.db_session.query(WebhookRegistration).filter_by(id=webhook_id).first()
        if webhook:
            webhook.active = False
            self.db_session.commit()
            logger.info(f"Webhook unregistered: {webhook_id}")
            return True
        return False
    
    def send_event(self, event: WebhookEvent, user_id: Optional[int] = None) -> List[WebhookDelivery]:
        """Send webhook event to all registered webhooks"""
        if not self.db_session:
            logger.warning("No database session available for webhook delivery")
            return []
        
        # Find all active webhooks that subscribe to this event type
        query = self.db_session.query(WebhookRegistration).filter_by(
            active=True
        ).filter(
            WebhookRegistration.event_types.contains([event.event_type.value])
        )
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        webhooks = query.all()
        deliveries = []
        
        for webhook in webhooks:
            delivery = self._deliver_webhook(webhook, event)
            deliveries.append(delivery)
        
        return deliveries
    
    def _deliver_webhook(
        self,
        webhook: WebhookRegistration,
        event: WebhookEvent
    ) -> WebhookDelivery:
        """Deliver a webhook event"""
        payload = json.dumps(event.to_dict())
        signature = self._generate_signature(payload, webhook.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event.event_type.value,
            "X-Webhook-Id": str(webhook.id),
            "User-Agent": "ProposalGenerator-Webhook/1.0"
        }
        
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event_id=event.id,
            url=webhook.url,
            payload=payload,
            status="pending",
            attempts=0
        )
        
        if self.db_session:
            self.db_session.add(delivery)
            self.db_session.commit()
        
        # Attempt delivery
        success = self._attempt_delivery(delivery, headers, payload)
        
        if success:
            delivery.status = "success"
            delivery.delivered_at = datetime.utcnow()
        else:
            delivery.status = "failed"
            if delivery.attempts < delivery.max_attempts:
                delay = self.retry_delays[min(delivery.attempts, len(self.retry_delays) - 1)]
                delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
        
        if self.db_session:
            self.db_session.commit()
        
        return delivery
    
    def _attempt_delivery(
        self,
        delivery: WebhookDelivery,
        headers: Dict,
        payload: str
    ) -> bool:
        """Attempt to deliver a webhook"""
        delivery.attempts += 1
        
        try:
            response = requests.post(
                delivery.url,
                data=payload,
                headers=headers,
                timeout=10
            )
            
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:1000]  # Limit response body size
            
            if 200 <= response.status_code < 300:
                logger.info(f"Webhook delivered successfully: {delivery.id}")
                return True
            else:
                logger.warning(f"Webhook delivery failed with status {response.status_code}: {delivery.id}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook delivery error: {e} (delivery {delivery.id})")
            delivery.response_body = str(e)[:1000]
            return False
    
    def retry_failed_deliveries(self) -> int:
        """Retry failed webhook deliveries that are due for retry"""
        if not self.db_session:
            return 0
        
        now = datetime.utcnow()
        failed_deliveries = self.db_session.query(WebhookDelivery).filter(
            WebhookDelivery.status == "failed",
            WebhookDelivery.attempts < WebhookDelivery.max_attempts,
            WebhookDelivery.next_retry_at <= now
        ).all()
        
        retried = 0
        for delivery in failed_deliveries:
            webhook = self.db_session.query(WebhookRegistration).filter_by(
                id=delivery.webhook_id
            ).first()
            
            if webhook and webhook.active:
                event_data = json.loads(delivery.payload)
                event = WebhookEvent(
                    event_type=WebhookEventType(event_data["event_type"]),
                    data=event_data["data"],
                    timestamp=datetime.fromisoformat(event_data["timestamp"])
                )
                
                signature = self._generate_signature(delivery.payload, webhook.secret)
                headers = {
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Event": event.event_type.value,
                    "X-Webhook-Id": str(webhook.id),
                    "User-Agent": "ProposalGenerator-Webhook/1.0"
                }
                
                success = self._attempt_delivery(delivery, headers, delivery.payload)
                
                if success:
                    delivery.status = "success"
                    delivery.delivered_at = datetime.utcnow()
                else:
                    if delivery.attempts < delivery.max_attempts:
                        delay = self.retry_delays[min(delivery.attempts - 1, len(self.retry_delays) - 1)]
                        delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
                
                self.db_session.commit()
                retried += 1
        
        return retried
    
    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = self._generate_signature(payload, secret)
        return hmac.compare_digest(expected_signature, signature)
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _generate_secret(self) -> str:
        """Generate a random secret for webhook"""
        import secrets
        return secrets.token_urlsafe(32)

