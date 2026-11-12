"""
User repository interface defining the contract for user data access.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

User = get_user_model()


class UserRepositoryInterface(ABC):
    """
    Abstract interface for user repository operations.
    """

    @abstractmethod
    def get_all(self) -> QuerySet:
        """
        Get all users.
        
        Returns:
            QuerySet: All users
        """
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email (str): The user email
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username (str): The username
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> User:
        """
        Create a new user.
        
        Args:
            **kwargs: User data
            
        Returns:
            User: The created user
        """
        pass

    @abstractmethod
    def update(self, user: User, **kwargs) -> User:
        """
        Update an existing user.
        
        Args:
            user (User): The user to update
            **kwargs: Updated user data
            
        Returns:
            User: The updated user
        """
        pass

    @abstractmethod
    def delete(self, user: User) -> bool:
        """
        Delete a user.
        
        Args:
            user (User): The user to delete
            
        Returns:
            bool: True if deleted successfully
        """
        pass

    @abstractmethod
    def get_users_by_role(self, role_name: str) -> QuerySet:
        """
        Get users by role name.
        
        Args:
            role_name (str): The role name
            
        Returns:
            QuerySet: Users with the specified role
        """
        pass

    @abstractmethod
    def search(self, query: str) -> QuerySet:
        """
        Search users by e-mail, username, first name or last name (case-insensitive).

        Args:
            query (str): The search term

        Returns:
            QuerySet: Matching users
        """
        pass

    @abstractmethod
    def get_users_with_permission(self, permission_code: str) -> QuerySet:
        """
        Get users with a specific permission.
        
        Args:
            permission_code (str): The permission code
            
        Returns:
            QuerySet: Users with the specified permission
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists by email.
        
        Args:
            email (str): The email to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        pass

    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """
        Check if a user exists by username.
        
        Args:
            username (str): The username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        pass

    @abstractmethod
    def get_active_by_email(self, email: str) -> Optional[User]:
        """
        Get an active user by e-mail (case-insensitive).

        Args:
            email (str): The user e-mail

        Returns:
            Optional[User]: The active user if found, None otherwise
        """
        pass

    @abstractmethod
    def update_password(self, user: User, raw_password: str) -> None:
        """
        Set a new password for a user (hashed by Django).

        Args:
            user (User): The user
            raw_password (str): The new clear-text password
        """
        pass

    @abstractmethod
    def blacklist_refresh_tokens(self, user: User) -> int:
        """
        Blacklist every outstanding JWT refresh token of a user.

        Args:
            user (User): The user

        Returns:
            int: Number of newly blacklisted tokens
        """
        pass
