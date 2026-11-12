"""
Role repository interface defining the contract for role data access.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.core.models import Role


class RoleRepositoryInterface(ABC):
    """
    Abstract interface for role repository operations.
    """

    @abstractmethod
    def get_all(self) -> QuerySet:
        """
        Get all roles.
        
        Returns:
            QuerySet: All roles
        """
        pass

    @abstractmethod
    def get_by_id(self, role_id: int) -> Optional[Role]:
        """
        Get a role by ID.
        
        Args:
            role_id (int): The role ID
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            name (str): The role name
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Role:
        """
        Create a new role.
        
        Args:
            **kwargs: Role data
            
        Returns:
            Role: The created role
        """
        pass

    @abstractmethod
    def update(self, role: Role, **kwargs) -> Role:
        """
        Update an existing role.
        
        Args:
            role (Role): The role to update
            **kwargs: Updated role data
            
        Returns:
            Role: The updated role
        """
        pass

    @abstractmethod
    def delete(self, role: Role) -> bool:
        """
        Delete a role.
        
        Args:
            role (Role): The role to delete
            
        Returns:
            bool: True if deleted successfully
        """
        pass

    @abstractmethod
    def get_roles_with_permission(self, permission_code: str) -> QuerySet:
        """
        Get roles that have a specific permission.
        
        Args:
            permission_code (str): The permission code
            
        Returns:
            QuerySet: Roles with the specified permission
        """
        pass

    @abstractmethod
    def add_permission_to_role(self, role: Role, permission_id: int) -> bool:
        """
        Add a permission to a role.
        
        Args:
            role (Role): The role
            permission_id (int): The permission ID
            
        Returns:
            bool: True if added successfully
        """
        pass

    @abstractmethod
    def remove_permission_from_role(self, role: Role, permission_id: int) -> bool:
        """
        Remove a permission from a role.
        
        Args:
            role (Role): The role
            permission_id (int): The permission ID
            
        Returns:
            bool: True if removed successfully
        """
        pass

    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """
        Check if a role exists by name.
        
        Args:
            name (str): The role name to check
            
        Returns:
            bool: True if role exists, False otherwise
        """
        pass

    @abstractmethod
    def get_user_count(self, role: Role) -> int:
        """
        Get the number of users assigned to a role.
        
        Args:
            role (Role): The role
            
        Returns:
            int: Number of users with this role
        """
        pass