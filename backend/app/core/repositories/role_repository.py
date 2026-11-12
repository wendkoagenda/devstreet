"""
Role repository implementation for data access operations.
"""
from typing import Optional
from django.db.models import QuerySet
from app.core.models import Role, Permission
from app.core.interfaces.role_repository_interface import RoleRepositoryInterface


class RoleRepository(RoleRepositoryInterface):
    """
    Concrete implementation of role repository operations.
    """

    def get_all(self) -> QuerySet:
        """
        Get all roles.
        
        Returns:
            QuerySet: All roles with related permissions
        """
        return Role.objects.prefetch_related('permissions').all()

    def get_by_id(self, role_id: int) -> Optional[Role]:
        """
        Get a role by ID.
        
        Args:
            role_id (int): The role ID
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        return Role.objects.prefetch_related('permissions').filter(id=role_id).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            name (str): The role name
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        return Role.objects.prefetch_related('permissions').filter(name=name).first()

    def create(self, **kwargs) -> Role:
        """
        Create a new role.
        
        Args:
            **kwargs: Role data
            
        Returns:
            Role: The created role
        """
        # Extract permissions if provided
        permissions = kwargs.pop('permissions', [])
        
        # Create role
        role = Role.objects.create(**kwargs)
        
        # Assign permissions if provided
        if permissions:
            role.permissions.set(permissions)
        
        return role

    def update(self, role: Role, **kwargs) -> Role:
        """
        Update an existing role.
        
        Args:
            role (Role): The role to update
            **kwargs: Updated role data
            
        Returns:
            Role: The updated role
        """
        # Extract permissions if provided
        permissions = kwargs.pop('permissions', None)
        
        # Update role fields
        for field, value in kwargs.items():
            if hasattr(role, field):
                setattr(role, field, value)
        
        role.save()
        
        # Update permissions if provided
        if permissions is not None:
            role.permissions.set(permissions)
        
        return role

    def delete(self, role: Role) -> bool:
        """
        Delete a role.
        
        Args:
            role (Role): The role to delete
            
        Returns:
            bool: True if deleted successfully
        """
        role.delete()
        return True

    def get_roles_with_permission(self, permission_code: str) -> QuerySet:
        """
        Get roles that have a specific permission.
        
        Args:
            permission_code (str): The permission code
            
        Returns:
            QuerySet: Roles with the specified permission
        """
        return Role.objects.filter(permissions__code=permission_code).distinct()

    def add_permission_to_role(self, role: Role, permission_id: int) -> bool:
        """
        Add a permission to a role.
        
        Args:
            role (Role): The role
            permission_id (int): The permission ID
            
        Returns:
            bool: True if added successfully
        """
        permission = Permission.objects.filter(id=permission_id).first()
        if permission is None:
            return False
        role.permissions.add(permission)
        return True

    def remove_permission_from_role(self, role: Role, permission_id: int) -> bool:
        """
        Remove a permission from a role.
        
        Args:
            role (Role): The role
            permission_id (int): The permission ID
            
        Returns:
            bool: True if removed successfully
        """
        permission = Permission.objects.filter(id=permission_id).first()
        if permission is None:
            return False
        role.permissions.remove(permission)
        return True

    def exists_by_name(self, name: str) -> bool:
        """
        Check if a role exists by name.
        
        Args:
            name (str): The role name to check
            
        Returns:
            bool: True if role exists, False otherwise
        """
        return Role.objects.filter(name=name).exists()

    def get_user_count(self, role: Role) -> int:
        """
        Get the number of users assigned to a role.
        
        Args:
            role (Role): The role
            
        Returns:
            int: Number of users with this role
        """
        return role.users.count()