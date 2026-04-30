#!/usr/bin/env python3
"""
Metrics Collector
=================

Collects application metrics and performance data.
Tracks window launch times, session duration, feature usage.
"""

import logging
import time
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects application metrics and statistics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "app_start_time": datetime.now(),
            "window_launches": {},
            "session_start_time": None,
            "session_duration": 0,
            "total_sessions": 0,
            "feature_access_count": {},
        }
        logger.info("MetricsCollector initialized")
    
    def record_window_launch(self, window_type: str, duration_ms: float) -> None:
        """
        Record window launch time.
        
        Args:
            window_type: Type of window
            duration_ms: Launch time in milliseconds
        """
        if window_type not in self.metrics["window_launches"]:
            self.metrics["window_launches"][window_type] = []
        
        self.metrics["window_launches"][window_type].append(duration_ms)
        logger.debug(f"Recorded {window_type} launch time: {duration_ms:.2f}ms")
    
    def record_feature_access(self, feature_name: str) -> None:
        """
        Record feature access.
        
        Args:
            feature_name: Name of feature accessed
        """
        if feature_name not in self.metrics["feature_access_count"]:
            self.metrics["feature_access_count"][feature_name] = 0
        
        self.metrics["feature_access_count"][feature_name] += 1
        logger.debug(f"Recorded {feature_name} access ({self.metrics['feature_access_count'][feature_name]} times)")
    
    def start_session(self) -> None:
        """Mark start of user session."""
        self.metrics["session_start_time"] = time.time()
        self.metrics["total_sessions"] += 1
        logger.info(f"Session started (total: {self.metrics['total_sessions']})")
    
    def end_session(self) -> float:
        """
        Mark end of user session.
        
        Returns:
            Session duration in seconds
        """
        if self.metrics["session_start_time"]:
            duration = time.time() - self.metrics["session_start_time"]
            self.metrics["session_duration"] = duration
            logger.info(f"Session ended (duration: {duration:.2f}s)")
            return duration
        return 0
    
    def get_metrics(self) -> Dict:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            "app_start_time": self.metrics["app_start_time"].isoformat(),
            "uptime_seconds": (datetime.now() - self.metrics["app_start_time"]).total_seconds(),
            "window_launches": {
                wtype: {
                    "count": len(times),
                    "avg_ms": sum(times) / len(times) if times else 0,
                    "min_ms": min(times) if times else 0,
                    "max_ms": max(times) if times else 0,
                }
                for wtype, times in self.metrics["window_launches"].items()
            },
            "session_duration_seconds": self.metrics["session_duration"],
            "total_sessions": self.metrics["total_sessions"],
            "feature_access_count": self.metrics["feature_access_count"],
        }
    
    def get_window_stats(self, window_type: str) -> Dict:
        """
        Get statistics for specific window.
        
        Args:
            window_type: Type of window
            
        Returns:
            Window statistics
        """
        times = self.metrics["window_launches"].get(window_type, [])
        
        if not times:
            return {"count": 0, "avg_ms": 0, "min_ms": 0, "max_ms": 0}
        
        return {
            "count": len(times),
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
        }
    
    def reset(self) -> None:
        """Reset all metrics (for testing)."""
        self.metrics = {
            "app_start_time": datetime.now(),
            "window_launches": {},
            "session_start_time": None,
            "session_duration": 0,
            "total_sessions": 0,
            "feature_access_count": {},
        }
        logger.info("Metrics reset")
