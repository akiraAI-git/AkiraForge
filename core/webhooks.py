"""
Webhook System for Akira Forge
Enables external integrations through event-driven webhooks.
"""

import json
import uuid
from typing import Dict, Callable, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import requests


class WebhookEvent(Enum):
    """Webhook event types."""
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"
    USER_DELETED = "user.deleted"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"
    DOCUMENT_CREATED = "document.created"
    DOCUMENT_UPDATED = "document.updated"
    DOCUMENT_DELETED = "document.deleted"
    SECURITY_ALERT = "security.alert"
    SYSTEM_ERROR = "system.error"
    BACKUP_COMPLETED = "backup.completed"


class Webhook:
    """Represents a webhook registration."""
    
    def __init__(self, url: str, event: WebhookEvent, name: str = "",
                 secret: str = "", active: bool = True):
        self.id = str(uuid.uuid4())
        self.url = url
        self.event = event
        self.name = name or f"webhook_{event.value}"
        self.secret = secret or str(uuid.uuid4())
        self.active = active
        self.created_at = datetime.now()
        self.last_triggered = None
        self.failure_count = 0
        self.max_retries = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "event": self.event.value,
            "name": self.name,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "failure_count": self.failure_count
        }


class WebhookManager:
    """
    Manages webhook registrations and delivery.
    
    Features:
    - Register webhooks for specific events
    - Async webhook delivery with retries
    - Webhook verification with HMAC signatures
    - Event history and monitoring
    - Webhook deactivation on repeated failures
    """
    
    def __init__(self):
        self.webhooks: Dict[str, List[Webhook]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    def register_webhook(self, url: str, event: WebhookEvent,
                        name: str = "", secret: str = "") -> Webhook:
        """Register a new webhook."""
        webhook = Webhook(url, event, name, secret)
        
        event_key = event.value
        if event_key not in self.webhooks:
            self.webhooks[event_key] = []
        
        self.webhooks[event_key].append(webhook)
        return webhook
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """Unregister a webhook."""
        for event_key in self.webhooks:
            for i, webhook in enumerate(self.webhooks[event_key]):
                if webhook.id == webhook_id:
                    self.webhooks[event_key].pop(i)
                    return True
        return False
    
    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        for event_key in self.webhooks:
            for webhook in self.webhooks[event_key]:
                if webhook.id == webhook_id:
                    return webhook
        return None
    
    def list_webhooks(self, event: Optional[WebhookEvent] = None) -> List[Webhook]:
        """List webhooks."""
        if event:
            return self.webhooks.get(event.value, [])
        
        all_webhooks = []
        for event_key in self.webhooks:
            all_webhooks.extend(self.webhooks[event_key])
        return all_webhooks
    
    def trigger_event(self, event: WebhookEvent, data: Dict[str, Any]):
        """Trigger webhooks for an event."""
        event_key = event.value
        webhooks = self.webhooks.get(event_key, [])
        
        # Log event
        self._log_event(event, data)
        
        # Deliver to active webhooks
        for webhook in webhooks:
            if webhook.active:
                self._deliver_webhook(webhook, data)
    
    def _deliver_webhook(self, webhook: Webhook, data: Dict[str, Any]):
        """Deliver webhook with retry logic."""
        payload = {
            "event": webhook.event.value,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Calculate HMAC signature
        import hmac
        import hashlib
        payload_json = json.dumps(payload)
        signature = hmac.new(
            webhook.secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-Webhook-Event": webhook.event.value,
            "X-Webhook-Signature": f"sha256={signature}",
            "Content-Type": "application/json"
        }
        
        # Retry logic
        for attempt in range(webhook.max_retries):
            try:
                response = requests.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if 200 <= response.status_code < 300:
                    webhook.last_triggered = datetime.now()
                    webhook.failure_count = 0
                    return
                
            except Exception as e:
                print(f"❌ Webhook delivery failed (attempt {attempt + 1}): {str(e)}")
        
        # All retries failed
        webhook.failure_count += 1
        
        # Deactivate after too many failures
        if webhook.failure_count >= 10:
            webhook.active = False
            print(f"⚠️  Webhook {webhook.id} deactivated after repeated failures")
    
    def _log_event(self, event: WebhookEvent, data: Dict[str, Any]):
        """Log event to history."""
        log_entry = {
            "event": event.value,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        self.event_history.append(log_entry)
        
        # Trim history
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
    
    def get_event_history(self, event: Optional[WebhookEvent] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history."""
        if event:
            history = [e for e in self.event_history if e["event"] == event.value]
        else:
            history = self.event_history
        
        return history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get webhook statistics."""
        total_webhooks = sum(len(w) for w in self.webhooks.values())
        active_webhooks = sum(
            1 for w in self.list_webhooks()
            if w.active
        )
        
        return {
            "total_webhooks": total_webhooks,
            "active_webhooks": active_webhooks,
            "events_logged": len(self.event_history),
            "events_by_type": {
                event_key: len(self.webhooks.get(event_key, []))
                for event_key in self.webhooks
            }
        }


# Global instance
_webhook_manager: Optional[WebhookManager] = None


def get_webhook_manager() -> WebhookManager:
    """Get or create global webhook manager."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager


def trigger_webhook_event(event: WebhookEvent, data: Dict[str, Any]):
    """Trigger a webhook event (convenience function)."""
    get_webhook_manager().trigger_event(event, data)
