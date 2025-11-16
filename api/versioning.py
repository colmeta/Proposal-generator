"""API versioning system with backward compatibility"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from typing import Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class APIVersion:
    """Represents an API version"""
    
    def __init__(self, version: str, deprecated: bool = False, 
                 deprecation_date: Optional[str] = None,
                 sunset_date: Optional[str] = None):
        self.version = version
        self.deprecated = deprecated
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
    
    def is_deprecated(self) -> bool:
        """Check if version is deprecated"""
        return self.deprecated
    
    def is_sunset(self) -> bool:
        """Check if version is sunset (no longer supported)"""
        from datetime import datetime
        if self.sunset_date:
            return datetime.utcnow() > datetime.fromisoformat(self.sunset_date)
        return False


class APIVersionManager:
    """Manages API versions and routing"""
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.default_version = "v1"
        self.blueprints: Dict[str, Blueprint] = {}
        self.version_handlers: Dict[str, Dict[str, Callable]] = {}
    
    def register_version(
        self,
        version: str,
        deprecated: bool = False,
        deprecation_date: Optional[str] = None,
        sunset_date: Optional[str] = None
    ):
        """Register an API version"""
        self.versions[version] = APIVersion(
            version, deprecated, deprecation_date, sunset_date
        )
        logger.info(f"API version {version} registered")
    
    def get_version(self, version: str) -> Optional[APIVersion]:
        """Get version information"""
        return self.versions.get(version)
    
    def get_latest_version(self) -> str:
        """Get the latest API version"""
        if not self.versions:
            return self.default_version
        return max(self.versions.keys(), key=lambda v: [int(x) for x in v[1:].split('.')])
    
    def create_version_blueprint(self, version: str, import_name: str = __name__) -> Blueprint:
        """Create a blueprint for a specific version"""
        if version in self.blueprints:
            return self.blueprints[version]
        
        blueprint = Blueprint(f'api_{version}', import_name, url_prefix=f'/api/{version}')
        self.blueprints[version] = blueprint
        return blueprint
    
    def register_endpoint(
        self,
        version: str,
        rule: str,
        endpoint: Optional[str] = None,
        methods: Optional[list] = None
    ):
        """Register an endpoint for a specific version"""
        def decorator(func: Callable):
            if version not in self.version_handlers:
                self.version_handlers[version] = {}
            
            endpoint_name = endpoint or func.__name__
            key = f"{rule}:{':'.join(methods or ['GET'])}"
            self.version_handlers[version][key] = func
            
            # Register with blueprint
            blueprint = self.create_version_blueprint(version)
            blueprint.add_url_rule(rule, endpoint_name, func, methods=methods or ['GET'])
            
            return func
        return decorator
    
    def get_version_from_request(self) -> str:
        """Extract API version from request"""
        # Check URL path
        path_parts = request.path.split('/')
        if len(path_parts) >= 3 and path_parts[1] == 'api':
            version = path_parts[2]
            if version in self.versions:
                return version
        
        # Check header
        version_header = request.headers.get('X-API-Version')
        if version_header and version_header in self.versions:
            return version_header
        
        # Check query parameter
        version_param = request.args.get('version')
        if version_param and version_param in self.versions:
            return version_param
        
        # Default to default version
        return self.default_version
    
    def add_deprecation_headers(self, response, version: str):
        """Add deprecation headers to response"""
        version_info = self.get_version(version)
        if version_info and version_info.is_deprecated():
            response.headers['X-API-Deprecated'] = 'true'
            response.headers['X-API-Version'] = version
            if version_info.deprecation_date:
                response.headers['X-API-Deprecation-Date'] = version_info.deprecation_date
            if version_info.sunset_date:
                response.headers['X-API-Sunset-Date'] = version_info.sunset_date
            response.headers['X-API-Latest-Version'] = self.get_latest_version()
        
        return response


# Global version manager
_version_manager = APIVersionManager()


def init_versioning(app, default_version: str = "v1"):
    """Initialize API versioning for Flask app"""
    global _version_manager
    _version_manager.default_version = default_version
    
    # Register default version
    _version_manager.register_version(default_version)
    
    # Register all version blueprints
    for version, blueprint in _version_manager.blueprints.items():
        app.register_blueprint(blueprint)
    
    # Add deprecation headers middleware
    @app.after_request
    def add_version_headers(response):
        version = _version_manager.get_version_from_request()
        return _version_manager.add_deprecation_headers(response, version)
    
    logger.info(f"API versioning initialized with default version: {default_version}")


def api_version(version: str, rule: str, methods: Optional[list] = None):
    """Decorator for versioned endpoints"""
    return _version_manager.register_endpoint(version, rule, methods=methods)


def get_version_manager() -> APIVersionManager:
    """Get the global version manager"""
    return _version_manager


def backward_compatible(versions: list):
    """Decorator to mark endpoint as backward compatible across versions"""
    def decorator(func: Callable):
        func._compatible_versions = versions
        return func
    return decorator


# Example usage:
# @api_version("v1", "/jobs", methods=["GET", "POST"])
# def jobs_endpoint():
#     ...

