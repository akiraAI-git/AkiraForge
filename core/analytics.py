"""
Advanced Analytics System for Akira Forge
Comprehensive usage tracking, metrics collection, and reporting.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum
import json


class EventType(Enum):
    """Analytics event types."""
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    ERROR_OCCURRED = "error_occurred"
    FEATURE_USED = "feature_used"
    PERFORMANCE_METRIC = "performance_metric"
    SECURITY_EVENT = "security_event"


class AnalyticsEvent:
    """Represents an analytics event."""
    
    def __init__(self, event_type: EventType, event_name: str,
                 user_id: str = "anonymous", **data):
        self.id = str(datetime.now().timestamp())
        self.event_type = event_type
        self.event_name = event_name
        self.user_id = user_id
        self.timestamp = datetime.now()
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "event_name": self.event_name,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


class AnalyticsManager:
    """
    Advanced analytics system.
    
    Features:
    - Event tracking
    - User usage analytics
    - Performance metrics
    - Error tracking
    - Custom reports
    - Data aggregation
    """
    
    def __init__(self, retention_days: int = 30):
        self.events: List[AnalyticsEvent] = []
        self.retention_days = retention_days
        self.aggregations: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def track_event(self, event_type: EventType, event_name: str,
                   user_id: str = "anonymous", **data) -> AnalyticsEvent:
        """Track an analytics event."""
        event = AnalyticsEvent(event_type, event_name, user_id, **data)
        self.events.append(event)
        
        # Cleanup old events
        self._cleanup_old_events()
        
        # Update aggregations
        self._update_aggregations(event)
        
        return event
    
    def track_user_action(self, action: str, user_id: str = "anonymous", **data):
        """Track user action."""
        return self.track_event(EventType.USER_ACTION, action, user_id, **data)
    
    def track_api_call(self, endpoint: str, method: str,
                      status_code: int, duration_ms: float, user_id: str = "anonymous"):
        """Track API call."""
        return self.track_event(
            EventType.API_CALL,
            endpoint,
            user_id,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms
        )
    
    def track_error(self, error_type: str, error_message: str,
                   user_id: str = "anonymous", **context):
        """Track error event."""
        return self.track_event(
            EventType.ERROR_OCCURRED,
            error_type,
            user_id,
            error_message=error_message,
            **context
        )
    
    def track_feature_usage(self, feature_name: str, user_id: str = "anonymous", **data):
        """Track feature usage."""
        return self.track_event(
            EventType.FEATURE_USED,
            feature_name,
            user_id,
            **data
        )
    
    def track_performance(self, metric_name: str, value: float,
                         unit: str = "", user_id: str = "anonymous"):
        """Track performance metric."""
        return self.track_event(
            EventType.PERFORMANCE_METRIC,
            metric_name,
            user_id,
            value=value,
            unit=unit
        )
    
    def get_events(self, event_type: Optional[EventType] = None,
                  user_id: Optional[str] = None,
                  limit: int = 100) -> List[AnalyticsEvent]:
        """Get events with filtering."""
        results = self.events
        
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        
        return results[-limit:]
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        user_events = [e for e in self.events if e.user_id == user_id]
        
        if not user_events:
            return {}
        
        event_counts = defaultdict(int)
        for event in user_events:
            event_counts[event.event_name] += 1
        
        return {
            "user_id": user_id,
            "total_events": len(user_events),
            "first_seen": user_events[0].timestamp.isoformat(),
            "last_seen": user_events[-1].timestamp.isoformat(),
            "event_breakdown": dict(event_counts)
        }
    
    def get_top_events(self, limit: int = 10) -> List[tuple]:
        """Get top events by frequency."""
        event_counts = defaultdict(int)
        for event in self.events:
            event_counts[event.event_name] += 1
        
        return sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_top_users(self, limit: int = 10) -> List[tuple]:
        """Get top users by activity."""
        user_counts = defaultdict(int)
        for event in self.events:
            user_counts[event.user_id] += 1
        
        return sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get error summary."""
        errors = [e for e in self.events if e.event_type == EventType.ERROR_OCCURRED]
        
        error_counts = defaultdict(int)
        for error in errors:
            error_counts[error.event_name] += 1
        
        return dict(error_counts)
    
    def get_hourly_activity(self) -> Dict[str, int]:
        """Get activity by hour."""
        activity = defaultdict(int)
        
        for event in self.events:
            hour = event.timestamp.strftime("%Y-%m-%d %H:00")
            activity[hour] += 1
        
        return dict(sorted(activity.items()))
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        return {
            "generated_at": datetime.now().isoformat(),
            "total_events": len(self.events),
            "date_range": {
                "start": self.events[0].timestamp.isoformat() if self.events else None,
                "end": self.events[-1].timestamp.isoformat() if self.events else None
            },
            "top_events": dict(self.get_top_events(10)),
            "top_users": dict(self.get_top_users(10)),
            "error_summary": self.get_error_summary(),
            "hourly_activity": self.get_hourly_activity(),
            "event_types_breakdown": {
                event_type.value: len([e for e in self.events if e.event_type == event_type])
                for event_type in EventType
            }
        }
    
    def _update_aggregations(self, event: AnalyticsEvent):
        """Update aggregated statistics."""
        key = f"{event.event_type.value}:{event.event_name}"
        
        if "count" not in self.aggregations[key]:
            self.aggregations[key]["count"] = 0
            self.aggregations[key]["last_occurred"] = None
        
        self.aggregations[key]["count"] += 1
        self.aggregations[key]["last_occurred"] = event.timestamp.isoformat()
    
    def _cleanup_old_events(self):
        """Remove events older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        self.events = [e for e in self.events if e.timestamp > cutoff_date]


# Global instance
_analytics_manager: Optional[AnalyticsManager] = None


def get_analytics_manager() -> AnalyticsManager:
    """Get or create global analytics manager."""
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AnalyticsManager()
    return _analytics_manager


# Convenience functions
def track_event(event_type: EventType, event_name: str,
               user_id: str = "anonymous", **data):
    """Track an event (convenience function)."""
    return get_analytics_manager().track_event(event_type, event_name, user_id, **data)


def track_user_action(action: str, user_id: str = "anonymous", **data):
    """Track user action (convenience function)."""
    return get_analytics_manager().track_user_action(action, user_id, **data)
