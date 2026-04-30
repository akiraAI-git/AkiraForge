#!/usr/bin/env python3
"""
Email Alert System
==================

Sends email notifications for critical audit events.

Features:
  - SMTP configuration
  - Alert templates for different events
  - Rate limiting to prevent email spam
  - HTML email formatting
  - Bulk alerting capability
"""

import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import json
import threading
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

class EmailAlertSystem:
    """Sends email alerts for important events."""
    
    def __init__(self, smtp_host: str = None, smtp_port: int = 587):
        """
        Initialize email alert system.
        
        Args:
            smtp_host: SMTP server host (default: from env or disabled)
            smtp_port: SMTP port (default: 587)
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "")
        self.smtp_port = smtp_port
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin@akiraforge.local")
        
        self.lock = threading.Lock()
        self.alert_queue = []
        self.alert_history = defaultdict(list)  # {email: [alert_timestamps]}
        
        # Alert rate limits (from environment or defaults)
        self.rate_limits = {
            "critical": int(os.getenv("ALERT_RATE_LIMIT_CRITICAL", "10")),      # 10 per hour
            "security": int(os.getenv("ALERT_RATE_LIMIT_SECURITY", "5")),       # 5 per hour
            "info": int(os.getenv("ALERT_RATE_LIMIT_INFO", "20"))          # 20 per hour
        }
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"Email alert system initialized: {'ENABLED' if self.is_enabled() else 'DISABLED'}")
    
    def _validate_configuration(self):
        """Validate email configuration."""
        if not self.is_enabled():
            logger.warning("Email alerting not configured (set SMTP_HOST, SMTP_USER, SMTP_PASSWORD, ADMIN_EMAIL)")
        else:
            logger.info(f"Email alerting configured for: {self.admin_email}")
            logger.debug(f"SMTP: {self.smtp_user}@{self.smtp_host}:{self.smtp_port}")
    
    def is_enabled(self) -> bool:
        """Check if email alerting is enabled."""
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)
    
    def send_alert(self, alert_type: str, subject: str, message: str,
                  recipient: str = None, details: dict = None) -> bool:
        """
        Send an alert email.
        
        Args:
            alert_type: Type of alert (critical, security, info)
            subject: Email subject
            message: Email message body
            recipient: Email recipient (default: admin)
            details: Additional details to include
            
        Returns:
            True if sent successfully
        """
        if not self.is_enabled():
            logger.debug(f"Alert not sent (not configured): {alert_type} - {subject}")
            return False
        
        recipient = recipient or self.admin_email
        
        with self.lock:
            # Check rate limit
            if not self._check_rate_limit(recipient, alert_type):
                logger.warning(f"Alert rate limit exceeded for {recipient}")
                return False
            
            # Create email
            try:
                html_message = self._create_html_message(
                    alert_type, message, subject, details
                )
                
                # Send email
                if self._send_email(recipient, subject, html_message):
                    self.alert_history[recipient].append(time.time())
                    logger.info(f"Alert sent: {alert_type} to {recipient}")
                    return True
                else:
                    return False
            
            except Exception as e:
                logger.error(f"Error sending alert: {e}")
                return False
    
    def _check_rate_limit(self, recipient: str, alert_type: str) -> bool:
        """Check if alert is rate-limited."""
        limit = self.rate_limits.get(alert_type, 5)
        current_time = time.time()
        one_hour_ago = current_time - 3600
        
        # Clean up old entries
        self.alert_history[recipient] = [
            ts for ts in self.alert_history[recipient]
            if ts > one_hour_ago
        ]
        
        return len(self.alert_history[recipient]) < limit
    
    def _send_email(self, recipient: str, subject: str, html_message: str) -> bool:
        """Send email via SMTP."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = recipient
            
            msg.attach(MIMEText(html_message, "html"))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
    
    def _create_html_message(self, alert_type: str, message: str,
                            subject: str, details: dict = None) -> str:
        """Create formatted HTML email message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Color coding by alert type
        colors = {
            "critical": "#DC2626",
            "security": "#F59E0B",
            "info": "#3B82F6"
        }
        
        color = colors.get(alert_type, "#6B7280")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    border: 3px solid {color};
                    border-radius: 8px;
                    padding: 20px;
                }}
                .alert-header {{
                    background-color: {color};
                    color: white;
                    padding: 15px;
                    border-radius: 4px;
                    margin: -20px -20px 20px -20px;
                }}
                .alert-title {{
                    font-size: 24px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .alert-type {{
                    font-size: 14px;
                    opacity: 0.8;
                }}
                .alert-body {{
                    font-size: 14px;
                    line-height: 1.6;
                    color: #333;
                }}
                .alert-details {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 15px;
                    font-family: monospace;
                    font-size: 12px;
                }}
                .alert-footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #999;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="alert-container">
                <div class="alert-header">
                    <div class="alert-title">⚠️ {alert_type.upper()} ALERT</div>
                    <div class="alert-type">{subject}</div>
                </div>
                
                <div class="alert-body">
                    {message}
                </div>
        """
        
        if details:
            html += '<div class="alert-details">'
            for key, value in details.items():
                html += f"<strong>{key}:</strong> {value}<br/>"
            html += '</div>'
        
        html += f"""
                <div class="alert-footer">
                    Generated: {timestamp}<br/>
                    From: Akira Forge Security System
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_critical_alert(self, message: str, details: dict = None) -> bool:
        """Send critical alert."""
        return self.send_alert(
            "critical",
            "CRITICAL SECURITY ALERT",
            message,
            details=details
        )
    
    def send_security_alert(self, message: str, details: dict = None) -> bool:
        """Send security alert."""
        return self.send_alert(
            "security",
            "Security Event Detected",
            message,
            details=details
        )
    
    def send_admin_notification(self, message: str, details: dict = None) -> bool:
        """Send admin notification."""
        return self.send_alert(
            "info",
            "Admin Notification",
            message,
            details=details
        )
    
    def get_metrics(self) -> dict:
        """Get alert system metrics."""
        with self.lock:
            return {
                "enabled": self.is_enabled(),
                "total_alerts_sent": sum(len(timestamps) for timestamps in self.alert_history.values()),
                "alerted_recipients": len(self.alert_history),
                "rate_limits": self.rate_limits
            }

# ... rest of file unchanged ...
    
    def is_enabled(self) -> bool:
        """Check if email alerting is enabled."""
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)
    
    def send_alert(self, alert_type: str, subject: str, message: str,
                  recipient: str = None, details: dict = None) -> bool:
        """
        Send an alert email.
        
        Args:
            alert_type: Type of alert (critical, security, info)
            subject: Email subject
            message: Email message body
            recipient: Email recipient (default: admin)
            details: Additional details to include
            
        Returns:
            True if sent successfully
        """
        if not self.is_enabled():
            return False
        
        recipient = recipient or self.admin_email
        
        with self.lock:
            # Check rate limit
            if not self._check_rate_limit(recipient, alert_type):
                print(f"[ALERT] Rate limit exceeded for {recipient}")
                return False
            
            # Create email
            try:
                html_message = self._create_html_message(
                    alert_type, message, subject, details
                )
                
                # Send email
                if self._send_email(recipient, subject, html_message):
                    self.alert_history[recipient].append(time.time())
                    return True
                else:
                    return False
            
            except Exception as e:
                print(f"[ALERT] Error sending alert: {e}")
                return False
    
    def _check_rate_limit(self, recipient: str, alert_type: str) -> bool:
        """Check if alert is rate-limited."""
        limit = self.rate_limits.get(alert_type, 5)
        current_time = time.time()
        one_hour_ago = current_time - 3600
        
        # Clean up old entries
        self.alert_history[recipient] = [
            ts for ts in self.alert_history[recipient]
            if ts > one_hour_ago
        ]
        
        return len(self.alert_history[recipient]) < limit
    
    def _send_email(self, recipient: str, subject: str, html_message: str) -> bool:
        """Send email via SMTP."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = recipient
            
            msg.attach(MIMEText(html_message, "html"))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print(f"[ALERT] SMTP error: {e}")
            return False
    
    def _create_html_message(self, alert_type: str, message: str,
                            subject: str, details: dict = None) -> str:
        """Create formatted HTML email message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Color coding by alert type
        colors = {
            "critical": "#DC2626",
            "security": "#F59E0B",
            "info": "#3B82F6"
        }
        
        color = colors.get(alert_type, "#6B7280")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    border: 3px solid {color};
                    border-radius: 8px;
                    padding: 20px;
                }}
                .alert-header {{
                    background-color: {color};
                    color: white;
                    padding: 15px;
                    border-radius: 4px;
                    margin: -20px -20px 20px -20px;
                }}
                .alert-title {{
                    font-size: 24px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .alert-type {{
                    font-size: 14px;
                    opacity: 0.8;
                }}
                .alert-body {{
                    font-size: 14px;
                    line-height: 1.6;
                    color: #333;
                }}
                .alert-details {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 15px;
                    font-family: monospace;
                    font-size: 12px;
                }}
                .alert-footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #999;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="alert-container">
                <div class="alert-header">
                    <div class="alert-title">⚠️ {alert_type.upper()} ALERT</div>
                    <div class="alert-type">{subject}</div>
                </div>
                
                <div class="alert-body">
                    {message}
                </div>
        """
        
        if details:
            html += '<div class="alert-details">'
            for key, value in details.items():
                html += f"<strong>{key}:</strong> {value}<br/>"
            html += '</div>'
        
        html += f"""
                <div class="alert-footer">
                    Generated: {timestamp}<br/>
                    From: Akira Forge Security System
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_critical_alert(self, message: str, details: dict = None) -> bool:
        """Send critical alert."""
        return self.send_alert(
            "critical",
            "CRITICAL SECURITY ALERT",
            message,
            details=details
        )
    
    def send_security_alert(self, message: str, details: dict = None) -> bool:
        """Send security alert."""
        return self.send_alert(
            "security",
            "Security Event Detected",
            message,
            details=details
        )
    
    def send_admin_notification(self, message: str, details: dict = None) -> bool:
        """Send admin notification."""
        return self.send_alert(
            "info",
            "Admin Notification",
            message,
            details=details
        )

# Global instance
_global_alert_system = None

def get_alert_system() -> EmailAlertSystem:
    """Get or create global alert system."""
    global _global_alert_system
    if _global_alert_system is None:
        _global_alert_system = EmailAlertSystem()
    return _global_alert_system

def send_alert(alert_type: str, subject: str, message: str, **kwargs) -> bool:
    """Send alert."""
    system = get_alert_system()
    return system.send_alert(alert_type, subject, message, **kwargs)

def send_critical_alert(message: str, details: dict = None) -> bool:
    """Send critical alert."""
    system = get_alert_system()
    return system.send_critical_alert(message, details)

def is_alerting_enabled() -> bool:
    """Check if alerting is enabled."""
    system = get_alert_system()
    return system.is_enabled()
