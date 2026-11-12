"""
Permission service layer for business logic operations.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.core.models import Permission
from app.core.repositories.permission_repository import PermissionRepository


class PermissionService:
    """
    Service class for permission-related business logic.
    """

    def __init__(self):
        self.permission_repository = PermissionRepository()

    def get_all_permissions(self) -> QuerySet:
        """
        Get all permissions.
        
        Returns:
            QuerySet: All permissions
        """
        return self.permission_repository.get_all()

    def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        """
        Get a permission by ID.
        
        Args:
            permission_id (int): The permission ID
            
        Returns:
            Optional[Permission]: The permission if found, None otherwise
        """
        return self.permission_repository.get_by_id(permission_id)

    def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """
        Get a permission by code.
        
        Args:
            code (str): The permission code
            
        Returns:
            Optional[Permission]: The permission if found, None otherwise
        """
        return self.permission_repository.get_by_code(code)

    def get_permissions_by_codes(self, codes: List[str]) -> QuerySet:
        """
        Get permissions by a list of codes.
        
        Args:
            codes (List[str]): List of permission codes
            
        Returns:
            QuerySet: Permissions matching the codes
        """
        return self.permission_repository.get_by_codes(codes)

    def create_permission(self, permission_data: Dict[str, Any]) -> Permission:
        """
        Create a new permission with validation.
        
        Args:
            permission_data (Dict[str, Any]): Permission data
            
        Returns:
            Permission: The created permission
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if not permission_data.get('code'):
            raise ValidationError("Permission code is required")

        # Validate code format (alphanumeric, underscores, dots allowed)
        code = permission_data['code']
        if not code.replace('_', '').replace('.', '').isalnum():
            raise ValidationError("Permission code can only contain letters, numbers, underscores, and dots")

        # Check if permission code already exists
        if self.permission_repository.exists_by_code(code):
            raise ValidationError("Permission with this code already exists")

        return self.permission_repository.create(**permission_data)

    def update_permission(self, permission_id: int, permission_data: Dict[str, Any]) -> Optional[Permission]:
        """
        Update an existing permission.
        
        Args:
            permission_id (int): The permission ID
            permission_data (Dict[str, Any]): Updated permission data
            
        Returns:
            Optional[Permission]: The updated permission if found, None otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        permission = self.permission_repository.get_by_id(permission_id)
        if not permission:
            return None

        # Check code uniqueness if code is being updated
        if 'code' in permission_data and permission_data['code'] != permission.code:
            # Validate code format
            code = permission_data['code']
            if not code.replace('_', '').replace('.', '').isalnum():
                raise ValidationError("Permission code can only contain letters, numbers, underscores, and dots")
            
            if self.permission_repository.exists_by_code(code):
                raise ValidationError("Permission with this code already exists")

        return self.permission_repository.update(permission, **permission_data)

    def delete_permission(self, permission_id: int) -> bool:
        """
        Delete a permission.
        
        Args:
            permission_id (int): The permission ID
            
        Returns:
            bool: True if deleted successfully, False if permission not found
            
        Raises:
            ValidationError: If permission is still assigned to roles
        """
        permission = self.permission_repository.get_by_id(permission_id)
        if not permission:
            return False

        # Check if permission is assigned to any roles
        role_count = self.permission_repository.get_role_count(permission)
        if role_count > 0:
            raise ValidationError(f"Cannot delete permission. It is assigned to {role_count} role(s)")

        return self.permission_repository.delete(permission)

    def get_permissions_by_role(self, role_id: int) -> QuerySet:
        """
        Get all permissions assigned to a specific role.
        
        Args:
            role_id (int): The role ID
            
        Returns:
            QuerySet: Permissions assigned to the role
        """
        return self.permission_repository.get_permissions_by_role(role_id)

    def get_permissions_by_user(self, user_id: int) -> QuerySet:
        """
        Get all permissions for a user through their roles.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            QuerySet: Permissions available to the user
        """
        return self.permission_repository.get_permissions_by_user(user_id)

    def search_permissions(self, query: str) -> QuerySet:
        """
        Search permissions by code or description.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Matching permissions
        """
        return self.permission_repository.search_by_code_or_description(query)

    def get_permission_role_count(self, permission_id: int) -> int:
        """
        Get the number of roles that have this permission.
        
        Args:
            permission_id (int): The permission ID
            
        Returns:
            int: Number of roles with this permission
        """
        permission = self.permission_repository.get_by_id(permission_id)
        if not permission:
            return 0

        return self.permission_repository.get_role_count(permission)

    def bulk_create_permissions(self, permissions_data: List[Dict[str, Any]]) -> List[Permission]:
        """
        Create multiple permissions at once.
        
        Args:
            permissions_data (List[Dict[str, Any]]): List of permission data
            
        Returns:
            List[Permission]: List of created permissions
            
        Raises:
            ValidationError: If any validation fails
        """
        created_permissions = []
        
        # Validate all permissions first
        codes = []
        for permission_data in permissions_data:
            if not permission_data.get('code'):
                raise ValidationError("Permission code is required for all permissions")
            
            code = permission_data['code']
            if code in codes:
                raise ValidationError(f"Duplicate permission code in request: {code}")
            codes.append(code)
            
            # Validate code format
            if not code.replace('_', '').replace('.', '').isalnum():
                raise ValidationError(f"Permission code '{code}' can only contain letters, numbers, underscores, and dots")
            
            # Check if permission code already exists
            if self.permission_repository.exists_by_code(code):
                raise ValidationError(f"Permission with code '{code}' already exists")

        # Create all permissions
        for permission_data in permissions_data:
            permission = self.permission_repository.create(**permission_data)
            created_permissions.append(permission)

        return created_permissions

    def get_permission_usage_stats(self, permission_id: int) -> Dict[str, Any]:
        """
        Get usage statistics for a permission.
        
        Args:
            permission_id (int): The permission ID
            
        Returns:
            Dict[str, Any]: Usage statistics
        """
        permission = self.permission_repository.get_by_id(permission_id)
        if not permission:
            return {}

        role_count = self.permission_repository.get_role_count(permission)
        
        # Get user count through roles
        user_count = 0
        roles_with_permission = permission.roles.all()
        for role in roles_with_permission:
            user_count += role.users.count()

        return {
            'permission_id': permission.id,
            'permission_code': permission.code,
            'role_count': role_count,
            'user_count': user_count,
            'roles': [role.name for role in roles_with_permission]
        }

    def validate_permission_codes(self, codes: List[str]) -> Dict[str, bool]:
        """
        Validate multiple permission codes.
        
        Args:
            codes (List[str]): List of permission codes to validate
            
        Returns:
            Dict[str, bool]: Dictionary mapping codes to their existence status
        """
        result = {}
        for code in codes:
            result[code] = self.permission_repository.exists_by_code(code)
        return result