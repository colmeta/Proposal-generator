"""Swagger/OpenAPI documentation setup"""
from flasgger import Swagger, swag_from
from flask import Flask, current_app
import os


def get_swagger_config() -> dict:
    """Get Swagger configuration"""
    return {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs",
        "title": "Proposal Generator API",
        "version": "1.0.0",
        "description": """
        Comprehensive API for Proposal Generator application.
        
        ## Authentication
        
        The API supports multiple authentication methods:
        
        ### API Key Authentication
        Include your API key in the request header:
        ```
        X-API-Key: your_api_key_here
        ```
        
        ### JWT Bearer Token
        Include the JWT token in the Authorization header:
        ```
        Authorization: Bearer your_jwt_token_here
        ```
        
        ### OAuth 2.0
        Use OAuth 2.0 flow for third-party integrations.
        
        ## Rate Limiting
        
        Rate limits are applied per user and per IP address:
        - Default user limit: 100 requests per minute
        - Default IP limit: 200 requests per minute
        
        Rate limit headers are included in all responses:
        - `X-RateLimit-Limit`: Maximum requests allowed
        - `X-RateLimit-Remaining`: Remaining requests
        - `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)
        
        ## Webhooks
        
        Register webhooks to receive real-time event notifications:
        - Job status changes
        - Project updates
        - Document generation
        - Error events
        
        ## Error Codes
        
        - `400`: Bad Request - Invalid input data
        - `401`: Unauthorized - Authentication required
        - `403`: Forbidden - Insufficient permissions
        - `404`: Not Found - Resource not found
        - `429`: Too Many Requests - Rate limit exceeded
        - `500`: Internal Server Error - Server error
        
        ## Versioning
        
        API versioning is supported via URL prefix:
        - `/api/v1/...` - Version 1 (current)
        - `/api/v2/...` - Version 2 (future)
        """,
        "termsOfService": "https://example.com/terms",
        "contact": {
            "name": "API Support",
            "email": "api@example.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        "tags": [
            {
                "name": "Jobs",
                "description": "Job management endpoints"
            },
            {
                "name": "Projects",
                "description": "Project management endpoints"
            },
            {
                "name": "Documents",
                "description": "Document generation endpoints"
            },
            {
                "name": "Webhooks",
                "description": "Webhook registration and management"
            },
            {
                "name": "Integrations",
                "description": "External integrations (CRM, PM tools)"
            },
            {
                "name": "Authentication",
                "description": "Authentication and authorization"
            },
            {
                "name": "Health",
                "description": "Health check and status endpoints"
            }
        ],
        "securityDefinitions": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header",
                "description": "API key authentication"
            },
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Bearer token authentication. Format: 'Bearer {token}'"
            },
            "OAuth2": {
                "type": "oauth2",
                "authorizationUrl": "/api/oauth/authorize",
                "tokenUrl": "/api/oauth/token",
                "flow": "authorizationCode",
                "scopes": {
                    "read": "Read access",
                    "write": "Write access",
                    "admin": "Admin access"
                }
            }
        }
    }


def setup_swagger(app: Flask):
    """Setup Swagger documentation for Flask app"""
    config = get_swagger_config()
    swagger = Swagger(app, config=config, template={
        "info": {
            "title": config["title"],
            "version": config["version"],
            "description": config["description"],
            "termsOfService": config["termsOfService"],
            "contact": config["contact"],
            "license": config["license"]
        },
        "securityDefinitions": config["securityDefinitions"],
        "tags": config["tags"]
    })
    
    return swagger


# Example Swagger documentation decorator usage
def swagger_doc(summary: str = None, description: str = None, tags: list = None, 
                security: list = None, responses: dict = None):
    """Decorator for adding Swagger documentation to endpoints"""
    def decorator(func):
        doc = {
            "summary": summary or func.__name__,
            "description": description or "",
            "tags": tags or [],
            "security": security or [],
            "responses": responses or {
                "200": {
                    "description": "Success"
                },
                "400": {
                    "description": "Bad Request"
                },
                "401": {
                    "description": "Unauthorized"
                },
                "500": {
                    "description": "Internal Server Error"
                }
            }
        }
        
        # Add request body if function has parameters
        if hasattr(func, '__annotations__'):
            doc["parameters"] = []
            for param_name, param_type in func.__annotations__.items():
                if param_name != 'return':
                    doc["parameters"].append({
                        "name": param_name,
                        "in": "body" if param_name == "body" else "query",
                        "required": True,
                        "schema": {"type": "object"}
                    })
        
        func._swagger_doc = doc
        return swag_from(doc)(func)
    return decorator

