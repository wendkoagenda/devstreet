"""
Permission repository implementation for data access operations.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.core.models import Permission
from app.core.interfaces.permission_repository_interface import PermissionRepositoryInterface


class PermissionRepository(PermissionRepositoryInterface):
    """
    Concrete implementation of permission repository operations.
    """

    def get_all(self) -> QuerySet:
        """
        Get all permissions.
        
        Returns:
            QuerySet: All permissions
        """
        return Permission.objects.all()

    def get_by_id(self, permission_id: int) -> Optional[Permission]:
        """
        Get a permission by ID.
        
        Args:
            permission_id (int): The permission ID
            
        Returns:
            Optional[Permission]: The permission if found, None otherwise
        """
        return Permission.objects.filter(id=permission_id).first()

    def get_by_code(self, code: str) -> Optional[Permission]:
        """
        Get a permission by code.
        
        Args:
            code (str): The permission code
            
        Returns:
            Optional[Permission]: The permission if found, None otherwise
        """
        return Permission.objects.filter(code=code).first()

    def get_by_codes(self, codes: List[str]) -> QuerySet:
        """
        Get permissions by a list of codes.
        
        Args:
            codes (List[str]): List of permission codes
            
        Returns:
            QuerySet: Permissions matching the codes
        """
        return Permission.objects.filter(code__in=codes)

    def create(self, **kwargs) -> Permission:
        """
        Create a new permission.
        
        Args:
            **kwargs: Permission data
            
        Returns:
            Permission: The created permission
        """
        return Permission.objects.create(**kwargs)

    def update(self, permission: Permission, **kwargs) -> Permission:
        """
        Update an existing permission.
        
        Args:
            permission (Permission): The permission to update
            **kwargs: Updated permission data
            
        Returns:
            Permission: The updated permission
        """
        # Update permission fields
        for field, value in kwargs.items():
            if hasattr(permission, field):
                setattr(permission, field, value)
        
        permission.save()
        return permission

    def delete(self, permission: Permission) -> bool:
        """
        Delete a permission.
        
        Args:
            permission (Permission): The permission to delete
            
        Returns:
            bool: True if deleted successfully
        """
        permission.delete()
        return True

    def exists_by_code(self, code: str) -> bool:
        """
        Check if a permission exists by code.
        
        Args:
            code (str): The permission code to check
            
        Returns:
            bool: True if permission exists, False otherwise
        """
        return Permission.objects.filter(code=code).exists()

    def get_permissions_by_role(self, role_id: int) -> QuerySet:
        """
        Get all permissions assigned to a specific role.
        
        Args:
            role_id (int): The role ID
            
        Returns:
            QuerySet: Permissions assigned to the role
        """
        return Permission.objects.filter(roles__id=role_id)

    def get_permissions_by_user(self, user_id: int) -> QuerySet:
        """
        Get all permissions for a user through their roles.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            QuerySet: Permissions available to the user
        """
        return Permission.objects.filter(roles__users__id=user_id).distinct()

    def search_by_code_or_description(self, query: str) -> QuerySet:
        """
        Search permissions by code or description.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Matching permissions
        """
        return Permission.objects.filter(
            Q(code__icontains=query) | Q(description__icontains=query)
        )

    def get_role_count(self, permission: Permission) -> int:
        """
        Get the number of roles that have this permission.
        
        Args:
            permission (Permission): The permission
            
        Returns:
            int: Number of roles with this permission
        """
        return permission.roles.count()