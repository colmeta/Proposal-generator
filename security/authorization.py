"""
Authorization Service
Role-based access control (RBAC), permission system
"""

from typing import Dict, List, Optional, Set, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    VIEWER = "viewer"


class Permission(str, Enum):
    """System permissions"""
    # Proposal permissions
    CREATE_PROPOSAL = "create_proposal"
    READ_PROPOSAL = "read_proposal"
    UPDATE_PROPOSAL = "update_proposal"
    DELETE_PROPOSAL = "delete_proposal"
    
    # Project permissions
    CREATE_PROJECT = "create_project"
    READ_PROJECT = "read_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    EXPORT_DATA = "export_data"
    
    # API permissions
    USE_API = "use_api"
    MANAGE_WEBHOOKS = "manage_webhooks"


class AuthorizationService:
    """
    Authorization service for role-based access control
    """
    
    def __init__(self):
        """Initialize authorization service"""
        self.role_permissions: Dict[Role, Set[Permission]] = self._initialize_role_permissions()
        self.resource_permissions: Dict[str, Dict[str, Set[Permission]]] = {}  # resource_type -> resource_id -> permissions
        logger.info("AuthorizationService initialized")
    
    def _initialize_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """Initialize default role permissions"""
        return {
            Role.ADMIN: {
                Permission.CREATE_PROPOSAL,
                Permission.READ_PROPOSAL,
                Permission.UPDATE_PROPOSAL,
                Permission.DELETE_PROPOSAL,
                Permission.CREATE_PROJECT,
                Permission.READ_PROJECT,
                Permission.UPDATE_PROJECT,
                Permission.DELETE_PROJECT,
                Permission.MANAGE_USERS,
                Permission.MANAGE_SETTINGS,
                Permission.VIEW_AUDIT_LOGS,
                Permission.EXPORT_DATA,
                Permission.USE_API,
                Permission.MANAGE_WEBHOOKS,
            },
            Role.USER: {
                Permission.CREATE_PROPOSAL,
                Permission.READ_PROPOSAL,
                Permission.UPDATE_PROPOSAL,
                Permission.CREATE_PROJECT,
                Permission.READ_PROJECT,
                Permission.UPDATE_PROJECT,
                Permission.USE_API,
            },
            Role.VIEWER: {
                Permission.READ_PROPOSAL,
                Permission.READ_PROJECT,
            },
            Role.GUEST: {
                Permission.READ_PROPOSAL,  # Limited read access
            }
        }
    
    def has_permission(self, user_roles: List[Role], permission: Permission) -> bool:
        """
        Check if user has a permission
        
        Args:
            user_roles: List of user roles
            permission: Permission to check
        
        Returns:
            True if user has permission
        """
        for role in user_roles:
            if role in self.role_permissions:
                if permission in self.role_permissions[role]:
                    return True
        return False
    
    def has_any_permission(self, user_roles: List[Role], permissions: List[Permission]) -> bool:
        """
        Check if user has any of the specified permissions
        
        Args:
            user_roles: List of user roles
            permissions: List of permissions to check
        
        Returns:
            True if user has any permission
        """
        return any(self.has_permission(user_roles, perm) for perm in permissions)
    
    def has_all_permissions(self, user_roles: List[Role], permissions: List[Permission]) -> bool:
        """
        Check if user has all specified permissions
        
        Args:
            user_roles: List of user roles
            permissions: List of permissions to check
        
        Returns:
            True if user has all permissions
        """
        return all(self.has_permission(user_roles, perm) for perm in permissions)
    
    def check_resource_permission(
        self,
        user_roles: List[Role],
        user_id: str,
        resource_type: str,
        resource_id: str,
        permission: Permission
    ) -> bool:
        """
        Check resource-level permission
        
        Args:
            user_roles: List of user roles
            user_id: User ID
            resource_type: Type of resource
            resource_id: Resource ID
            permission: Permission to check
        
        Returns:
            True if user has permission
        """
        # Check role-based permission first
        if not self.has_permission(user_roles, permission):
            return False
        
        # Check resource-specific permissions
        if resource_type in self.resource_permissions:
            resource_perms = self.resource_permissions[resource_type].get(resource_id)
            if resource_perms is not None:
                return permission in resource_perms
        
        # Default: allow if role has permission
        return True
    
    def grant_resource_permission(
        self,
        resource_type: str,
        resource_id: str,
        permission: Permission
    ):
        """
        Grant permission on a specific resource
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            permission: Permission to grant
        """
        if resource_type not in self.resource_permissions:
            self.resource_permissions[resource_type] = {}
        if resource_id not in self.resource_permissions[resource_type]:
            self.resource_permissions[resource_type][resource_id] = set()
        
        self.resource_permissions[resource_type][resource_id].add(permission)
        logger.info(f"Granted {permission} on {resource_type}:{resource_id}")
    
    def revoke_resource_permission(
        self,
        resource_type: str,
        resource_id: str,
        permission: Permission
    ):
        """
        Revoke permission on a specific resource
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            permission: Permission to revoke
        """
        if resource_type in self.resource_permissions:
            if resource_id in self.resource_permissions[resource_type]:
                self.resource_permissions[resource_type][resource_id].discard(permission)
                logger.info(f"Revoked {permission} on {resource_type}:{resource_id}")
    
    def get_user_permissions(self, user_roles: List[Role]) -> Set[Permission]:
        """
        Get all permissions for a user
        
        Args:
            user_roles: List of user roles
        
        Returns:
            Set of permissions
        """
        permissions = set()
        for role in user_roles:
            if role in self.role_permissions:
                permissions.update(self.role_permissions[role])
        return permissions
    
    def require_permission(self, permission: Permission) -> Callable:
        """
        Decorator to require permission for a function
        
        Args:
            permission: Required permission
        
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # This would need user context from request/session
                # Implementation depends on framework integration
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Global instance
authorization_service = AuthorizationService()

