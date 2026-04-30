"""
API Documentation Generator for Akira Forge
Auto-generates API documentation in OpenAPI/Swagger format.
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import json


class HTTPMethod(Enum):
    """HTTP method enumeration."""
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"


class EndpointParameter:
    """Represents an endpoint parameter."""
    
    def __init__(self, name: str, param_type: str = "string",
                 required: bool = False, description: str = ""):
        self.name = name
        self.type = param_type
        self.required = required
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "in": "query",
            "required": self.required,
            "schema": {"type": self.type},
            "description": self.description
        }


class APIEndpoint:
    """Represents an API endpoint."""
    
    def __init__(self, path: str, method: HTTPMethod, summary: str = "",
                 description: str = ""):
        self.path = path
        self.method = method
        self.summary = summary
        self.description = description
        self.parameters: List[EndpointParameter] = []
        self.request_body: Optional[Dict[str, Any]] = None
        self.responses: Dict[int, Dict[str, Any]] = {
            200: {"description": "Success"},
            400: {"description": "Bad Request"},
            401: {"description": "Unauthorized"},
            500: {"description": "Internal Server Error"}
        }
    
    def add_parameter(self, name: str, param_type: str = "string",
                     required: bool = False, description: str = ""):
        """Add a parameter."""
        param = EndpointParameter(name, param_type, required, description)
        self.parameters.append(param)
    
    def set_request_body(self, schema: Dict[str, Any]):
        """Set request body schema."""
        self.request_body = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": schema
                }
            }
        }
    
    def add_response(self, status_code: int, description: str,
                    schema: Optional[Dict[str, Any]] = None):
        """Add response definition."""
        response: Dict[str, Any] = {"description": description}
        
        if schema:
            response["content"] = {
                "application/json": {
                    "schema": schema
                }
            }
        
        self.responses[status_code] = response
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OpenAPI object."""
        endpoint: Dict[str, Any] = {
            "summary": self.summary,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "responses": self.responses
        }
        
        if self.request_body:
            endpoint["requestBody"] = self.request_body
        
        return endpoint


class APIDocumentationGenerator:
    """
    OpenAPI/Swagger documentation generator.
    
    Features:
    - Auto-generate API documentation
    - OpenAPI 3.0 compliance
    - Interactive API explorer
    - Schema validation
    """
    
    def __init__(self, title: str = "Akira Forge API",
                 version: str = "1.0.0",
                 base_url: str = "http://localhost:8000"):
        self.title = title
        self.version = version
        self.base_url = base_url
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}
    
    def register_endpoint(self, path: str, method: HTTPMethod,
                         summary: str = "", description: str = "") -> APIEndpoint:
        """Register an API endpoint."""
        key = f"{method.value.upper()} {path}"
        endpoint = APIEndpoint(path, method, summary, description)
        self.endpoints[key] = endpoint
        return endpoint
    
    def register_schema(self, name: str, schema: Dict[str, Any]):
        """Register a reusable schema."""
        self.schemas[name] = schema
    
    def generate_openapi_doc(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        paths = {}
        
        for key, endpoint in self.endpoints.items():
            if endpoint.path not in paths:
                paths[endpoint.path] = {}
            
            paths[endpoint.path][endpoint.method.value] = endpoint.to_dict()
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": f"API documentation for {self.title}"
            },
            "servers": [
                {"url": self.base_url, "description": "Production server"}
            ],
            "paths": paths,
            "components": {
                "schemas": self.schemas
            }
        }
    
    def export_to_file(self, filepath: str):
        """Export documentation to file."""
        try:
            doc = self.generate_openapi_doc()
            with open(filepath, 'w') as f:
                json.dump(doc, f, indent=2)
            print(f"✓ Exported API documentation to {filepath}")
        except Exception as e:
            print(f"❌ Failed to export documentation: {str(e)}")
    
    def export_to_swagger_ui(self, output_dir: str = "api_docs"):
        """Generate Swagger UI HTML."""
        import os
        from pathlib import Path
        
        try:
            doc = self.generate_openapi_doc()
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Save spec
            spec_path = output_path / "openapi.json"
            with open(spec_path, 'w') as f:
                json.dump(doc, f, indent=2)
            
            # Generate HTML
            html_content = self._generate_swagger_html(str(spec_path))
            html_path = output_path / "index.html"
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            print(f"✓ Generated Swagger UI at {html_path}")
        except Exception as e:
            print(f"❌ Failed to generate Swagger UI: {str(e)}")
    
    def get_endpoint_list(self) -> List[str]:
        """Get list of all endpoints."""
        return list(self.endpoints.keys())
    
    def _generate_swagger_html(self, spec_url: str) -> str:
        """Generate Swagger UI HTML."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.title} - API Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.css">
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            padding:0;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.js"></script>
    <script>
        window.onload = function() {{
            SwaggerUIBundle({{
                url: "{spec_url}",
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                onComplete: function() {{
                    console.log("Swagger UI loaded");
                }}
            }});
        }}
    </script>
</body>
</html>
"""


# Global instance
_api_doc_generator: Optional[APIDocumentationGenerator] = None


def get_api_documentation_generator() -> APIDocumentationGenerator:
    """Get or create global API documentation generator."""
    global _api_doc_generator
    if _api_doc_generator is None:
        _api_doc_generator = APIDocumentationGenerator()
    return _api_doc_generator


def register_endpoint(path: str, method: HTTPMethod,
                     summary: str = "", description: str = "") -> APIEndpoint:
    """Register an endpoint (convenience function)."""
    return get_api_documentation_generator().register_endpoint(path, method, summary, description)
