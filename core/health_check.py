"""
Health Check System for Akira Forge
Comprehensive health monitoring of application components.
"""

from typing import Dict, Any, Callable, Optional
from datetime import datetime
from enum import Enum
import psutil
import os


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentHealth:
    """Health status for a component."""
    
    def __init__(self, name: str, status: HealthStatus = HealthStatus.UNKNOWN):
        self.name = name
        self.status = status
        self.message = ""
        self.details: Dict[str, Any] = {}
        self.last_checked = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "last_checked": self.last_checked.isoformat()
        }


class HealthChecker:
    """
    System health checker.
    
    Features:
    - Check database connectivity
    - Monitor system resources
    - Check external service availability
    - Custom health checks
    - Health history and alerts
    """
    
    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {}
        self.checks: Dict[str, Callable] = {}
        self.alerts: list = []
    
    def register_check(self, name: str, check_func: Callable):
        """Register a custom health check."""
        self.checks[name] = check_func
    
    def perform_check(self, name: str) -> bool:
        """Perform a specific health check."""
        if name not in self.checks:
            return False
        
        try:
            result = self.checks[name]()
            self._update_component(name, HealthStatus.HEALTHY if result else HealthStatus.CRITICAL)
            return result
        except Exception as e:
            self._update_component(name, HealthStatus.CRITICAL, str(e))
            return False
    
    def check_all(self) -> Dict[str, ComponentHealth]:
        """Perform all health checks."""
        # System checks
        self._check_cpu()
        self._check_memory()
        self._check_disk()
        self._check_database()
        
        # Custom checks
        for name in self.checks:
            self.perform_check(name)
        
        return self.components
    
    def _check_cpu(self):
        """Check CPU health."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            status = HealthStatus.HEALTHY
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
            elif cpu_percent > 75:
                status = HealthStatus.DEGRADED
            
            self._update_component(
                "cpu",
                status,
                f"CPU usage at {cpu_percent}%",
                {"usage_percent": cpu_percent, "cores": psutil.cpu_count()}
            )
        except Exception as e:
            self._update_component("cpu", HealthStatus.UNKNOWN, str(e))
    
    def _check_memory(self):
        """Check memory health."""
        try:
            mem = psutil.virtual_memory()
            status = HealthStatus.HEALTHY
            
            if mem.percent > 90:
                status = HealthStatus.CRITICAL
            elif mem.percent > 75:
                status = HealthStatus.DEGRADED
            
            self._update_component(
                "memory",
                status,
                f"Memory usage at {mem.percent}%",
                {
                    "used_gb": mem.used / (1024**3),
                    "total_gb": mem.total / (1024**3),
                    "percent": mem.percent
                }
            )
        except Exception as e:
            self._update_component("memory", HealthStatus.UNKNOWN, str(e))
    
    def _check_disk(self):
        """Check disk health."""
        try:
            disk = psutil.disk_usage('/')
            status = HealthStatus.HEALTHY
            
            if disk.percent > 90:
                status = HealthStatus.CRITICAL
            elif disk.percent > 75:
                status = HealthStatus.DEGRADED
            
            self._update_component(
                "disk",
                status,
                f"Disk usage at {disk.percent}%",
                {
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3),
                    "percent": disk.percent
                }
            )
        except Exception as e:
            self._update_component("disk", HealthStatus.UNKNOWN, str(e))
    
    def _check_database(self):
        """Check database connectivity."""
        try:
            from .db import get_db_connection
            conn = get_db_connection()
            if conn:
                self._update_component(
                    "database",
                    HealthStatus.HEALTHY,
                    "Database connection successful"
                )
            else:
                self._update_component(
                    "database",
                    HealthStatus.CRITICAL,
                    "Failed to establish database connection"
                )
        except Exception as e:
            self._update_component(
                "database",
                HealthStatus.CRITICAL,
                str(e)
            )
    
    def _update_component(self, name: str, status: HealthStatus,
                         message: str = "", details: Dict[str, Any] = None):
        """Update component health status."""
        if details is None:
            details = {}
        
        if name not in self.components:
            self.components[name] = ComponentHealth(name)
        
        component = self.components[name]
        component.status = status
        component.message = message
        component.details = details
        component.last_checked = datetime.now()
        
        # Log alerts for critical status
        if status == HealthStatus.CRITICAL:
            self.alerts.append({
                "component": name,
                "timestamp": datetime.now().isoformat(),
                "message": message
            })
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall application health."""
        if not self.components:
            return HealthStatus.UNKNOWN
        
        statuses = [c.status for c in self.components.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif HealthStatus.HEALTHY in statuses:
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def get_report(self) -> Dict[str, Any]:
        """Get complete health report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.get_overall_status().value,
            "components": {
                name: component.to_dict()
                for name, component in self.components.items()
            },
            "recent_alerts": self.alerts[-10:]  # Last 10 alerts
        }


# Global instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker
