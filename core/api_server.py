#!/usr/bin/env python3
"""
RESTful API Server for Akira Forge

Provides HTTP API endpoints for remote access to application features,
enabling integration with external tools and web-based interfaces.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps
import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manage API keys and authentication."""
    
    def __init__(self):
        self.api_keys = {}
        self.rate_limits = {}
    
    def generate_api_key(self, name: str, permissions: List[str] = None) -> str:
        """Generate new API key."""
        import secrets
        key = f"ak_{secrets.token_urlsafe(32)}"
        self.api_keys[key] = {
            'name': name,
            'created': datetime.now().isoformat(),
            'permissions': permissions or ['read'],
            'active': True
        }
        logger.info(f"✓ Generated API key: {name}")
        return key
    
    def revoke_api_key(self, key: str) -> bool:
        """Revoke an API key."""
        if key in self.api_keys:
            self.api_keys[key]['active'] = False
            logger.info(f"✓ Revoked API key")
            return True
        return False
    
    def validate_key(self, key: str, required_permission: str = "read") -> bool:
        """Validate API key and check permissions."""
        if key not in self.api_keys:
            return False
        
        key_data = self.api_keys[key]
        if not key_data['active']:
            return False
        
        if required_permission not in key_data['permissions']:
            return False
        
        return True


class APIEndpoint:
    """Base API endpoint."""
    
    def __init__(self, path: str, method: str = "GET", auth_required: bool = True):
        self.path = path
        self.method = method
        self.auth_required = auth_required
        self.handlers = {}
    
    def handle(self, handler_func, status_code: int = 200) -> 'APIEndpoint':
        """Register handler function."""
        self.handlers[self.method] = {
            'func': handler_func,
            'status_code': status_code
        }
        return self
    
    def process(self, request_data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """Process endpoint request."""
        try:
            handler = self.handlers.get(self.method)
            if not handler:
                return {'error': f'Method {self.method} not supported', 'status': 405}
            
            result = handler['func'](request_data)
            return {
                'data': result,
                'status': handler['status_code'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Endpoint error: {e}")
            return {'error': str(e), 'status': 500}


class APIRouter:
    """Route API requests to appropriate endpoints."""
    
    def __init__(self):
        self.endpoints = {}
        self.api_key_manager = APIKeyManager()
        self.request_log = []
    
    def register_endpoint(self, path: str, method: str = "GET", 
                         auth_required: bool = True) -> APIEndpoint:
        """Register a new API endpoint."""
        endpoint = APIEndpoint(path, method, auth_required)
        key = f"{method.upper()} {path}"
        self.endpoints[key] = endpoint
        logger.info(f"✓ Registered endpoint: {key}")
        return endpoint
    
    def route_request(self, path: str, method: str, request_data: Dict[str, Any],
                     api_key: Optional[str] = None) -> Dict[str, Any]:
        """Route incoming request to endpoint."""
        key = f"{method.upper()} {path}"
        
        # Log request
        self._log_request(path, method, api_key)
        
        # Check if endpoint exists
        if key not in self.endpoints:
            return {'error': f'Endpoint {path} not found', 'status': 404}
        
        endpoint = self.endpoints[key]
        
        # Check authentication
        if endpoint.auth_required and not api_key:
            return {'error': 'API key required', 'status': 401}
        
        if endpoint.auth_required and not self.api_key_manager.validate_key(api_key):
            return {'error': 'Invalid API key', 'status': 401}
        
        # Process request
        return endpoint.process(request_data, api_key)
    
    def _log_request(self, path: str, method: str, api_key: Optional[str] = None):
        """Log API request."""
        self.request_log.append({
            'path': path,
            'method': method,
            'timestamp': datetime.now().isoformat(),
            'api_key': api_key[:10] + '...' if api_key else None
        })
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get API request statistics."""
        return {
            'total_requests': len(self.request_log),
            'registered_endpoints': len(self.endpoints),
            'active_api_keys': sum(1 for k in self.api_key_manager.api_keys.values() if k['active'])
        }


class WebSocketServer:
    """WebSocket server for real-time communication."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.clients = {}
        self.message_queue = []
    
    def add_client(self, client_id: str, connection_info: Dict[str, Any]):
        """Add connected client."""
        self.clients[client_id] = {
            'info': connection_info,
            'connected_at': datetime.now().isoformat()
        }
        logger.info(f"✓ Client connected: {client_id}")
    
    def remove_client(self, client_id: str):
        """Remove disconnected client."""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"✓ Client disconnected: {client_id}")
    
    def broadcast_message(self, message: Dict[str, Any], exclude_client: Optional[str] = None):
        """Broadcast message to all connected clients."""
        for client_id in self.clients:
            if client_id != exclude_client:
                self.message_queue.append({
                    'target': client_id,
                    'message': message,
                    'queued_at': datetime.now().isoformat()
                })
    
    def get_client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)


# Global instances
_router = None
_websocket_server = None


def get_router() -> APIRouter:
    """Get or create API router."""
    global _router
    if _router is None:
        _router = APIRouter()
        _setup_default_endpoints()
    return _router


def get_websocket_server() -> WebSocketServer:
    """Get or create WebSocket server."""
    global _websocket_server
    if _websocket_server is None:
        _websocket_server = WebSocketServer()
    return _websocket_server


def _setup_default_endpoints():
    """Setup default API endpoints."""
    router = get_router()
    
    # Health check endpoint
    def health_check(data):
        return {
            'status': 'healthy',
            'version': '1.1.4',
            'timestamp': datetime.now().isoformat()
        }
    
    router.register_endpoint('/health', 'GET', auth_required=False).handle(
        health_check, status_code=200
    )
    
    # Stats endpoint
    def get_stats(data):
        return router.get_request_stats()
    
    router.register_endpoint('/stats', 'GET', auth_required=True).handle(
        get_stats, status_code=200
    )
    
    logger.info("✓ Default API endpoints registered")
