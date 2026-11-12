"""
Role service layer for business logic operations.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.core.models import Role
from app.core.repositories.role_repository import RoleRepository
from app.core.repositories.permission_repository import PermissionRepository


class RoleService:
    """
    Service class for role-related business logic.
    """

    def __init__(self):
        self.role_repository = RoleRepository()
        self.permission_repository = PermissionRepository()

    def get_all_roles(self) -> QuerySet:
        """
        Get all roles.
        
        Returns:
            QuerySet: All roles
        """
        return self.role_repository.get_all()

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """
        Get a role by ID.
        
        Args:
            role_id (int): The role ID
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        return self.role_repository.get_by_id(role_id)

    def get_role_by_name(self, name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            name (str): The role name
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        return self.role_repository.get_by_name(name)

    def create_role(self, role_data: Dict[str, Any]) -> Role:
        """
        Create a new role with validation.
        
        Args:
            role_data (Dict[str, Any]): Role data
            
        Returns:
            Role: The created role
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if not role_data.get('name'):
            raise ValidationError("Role name is required")

        # Check if role name already exists
        if self.role_repository.exists_by_name(role_data['name']):
            raise ValidationError("Role with this name already exists")

        # Validate and process permissions
        permission_codes = role_data.pop('permission_codes', [])
        permissions = []
        if permission_codes:
            for permission_code in permission_codes:
                permission = self.permission_repository.get_by_code(permission_code)
                if not permission:
                    raise ValidationError(f"Permission '{permission_code}' does not exist")
                permissions.append(permission)

        # Create role
        role_data['permissions'] = permissions
        return self.role_repository.create(**role_data)

    def update_role(self, role_id: int, role_data: Dict[str, Any]) -> Optional[Role]:
        """
        Update an existing role.
        
        Args:
            role_id (int): The role ID
            role_data (Dict[str, Any]): Updated role data
            
        Returns:
            Optional[Role]: The updated role if found, None otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        role = self.role_repository.get_by_id(role_id)
        if not role:
            return None

        # Check name uniqueness if name is being updated
        if 'name' in role_data and role_data['name'] != role.name:
            if self.role_repository.exists_by_name(role_data['name']):
                raise ValidationError("Role with this name already exists")

        # Validate and process permissions
        permission_codes = role_data.pop('permission_codes', None)
        if permission_codes is not None:
            permissions = []
            for permission_code in permission_codes:
                permission = self.permission_repository.get_by_code(permission_code)
                if not permission:
                    raise ValidationError(f"Permission '{permission_code}' does not exist")
                permissions.append(permission)
            role_data['permissions'] = permissions

        return self.role_repository.update(role, **role_data)

    def delete_role(self, role_id: int) -> bool:
        """
        Delete a role.
        
        Args:
            role_id (int): The role ID
            
        Returns:
            bool: True if deleted successfully, False if role not found
            
        Raises:
            ValidationError: If role is still assigned to users
        """
        role = self.role_repository.get_by_id(role_id)
        if not role:
            return False

        # Check if role is assigned to any users
        user_count = self.role_repository.get_user_count(role)
        if user_count > 0:
            raise ValidationError(f"Cannot delete role. It is assigned to {user_count} user(s)")

        return self.role_repository.delete(role)

    def assign_permission_to_role(self, role_id: int, permission_code: str) -> bool:
        """
        Assign a permission to a role.
        
        Args:
            role_id (int): The role ID
            permission_code (str): The permission code
            
        Returns:
            bool: True if assigned successfully
            
        Raises:
            ValidationError: If role or permission not found
        """
        role = self.role_repository.get_by_id(role_id)
        if not role:
            raise ValidationError("Role not found")

        permission = self.permission_repository.get_by_code(permission_code)
        if not permission:
            raise ValidationError("Permission not found")

        return self.role_repository.add_permission_to_role(role, permission.id)

    def remove_permission_from_role(self, role_id: int, permission_code: str) -> bool:
        """
        Remove a permission from a role.
        
        Args:
            role_id (int): The role ID
            permission_code (str): The permission code
            
        Returns:
            bool: True if removed successfully
            
        Raises:
            ValidationError: If role or permission not found
        """
        role = self.role_repository.get_by_id(role_id)
        if not role:
            raise ValidationError("Role not found")

        permission = self.permission_repository.get_by_code(permission_code)
        if not permission:
            raise ValidationError("Permission not found")

        return self.role_repository.remove_permission_from_role(role, permission.id)

    def get_roles_with_permission(self, permission_code: str) -> QuerySet:
        """
        Get roles that have a specific permission.
        
        Args:
            permission_code (str): The permission code
            
        Returns:
            QuerySet: Roles with the specified permission
        """
        return self.role_repository.get_roles_with_permission(permission_code)

    def get_role_permissions(self, role_id: int) -> List[str]:
        """
        Get all permissions for a role.
        
        Args:
            role_id (int): The role ID
            
        Returns:
            List[str]: List of permission codes
        """
        role = self.role_repository.get_by_id(role_id)
        if not role:
            return []

        return role.get_permissions()

    def get_role_user_count(self, role_id: int) -> int:
        """
        Get the number of users assigned to a role.
        
        Args:
            role_id (int): The role ID
            
        Returns:
            int: Number of users with this role
        """
        role = self.role_repository.get_by_id(role_id)
        if not role:
            return 0

        return self.role_repository.get_user_count(role)

    def bulk_assign_permissions(self, role_id: int, permission_codes: List[str]) -> bool:
        """
        Assign multiple permissions to a role.
        
        Args:
            role_id (int): The role ID
            permission_codes (List[str]): List of permission codes
            
        Returns:
            bool: True if all permissions assigned successfully
            
        Raises:
            ValidationError: If role not found or any permission not found
        """
        role = self.role_repository.get_by_id(role_id)
        if not role:
            raise ValidationError("Role not found")

        # Validate all permissions exist
        permissions = []
        for permission_code in permission_codes:
            permission = self.permission_repository.get_by_code(permission_code)
            if not permission:
                raise ValidationError(f"Permission '{permission_code}' does not exist")
            permissions.append(permission)

        # Assign all permissions
        role.permissions.set(permissions)
        return True

    def search_roles(self, query: str) -> QuerySet:
        """
        Search roles by name or description.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Matching roles
        """
        return Role.objects.filter(
            name__icontains=query
        ) | Role.objects.filter(
            description__icontains=query
        )