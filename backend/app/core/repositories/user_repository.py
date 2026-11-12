"""
User repository implementation for data access operations.
"""
from typing import Optional
from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from app.core.interfaces.user_repository_interface import UserRepositoryInterface

User = get_user_model()


class UserRepository(UserRepositoryInterface):
    """
    Concrete implementation of user repository operations.
    """

    def get_all(self) -> QuerySet:
        """
        Get all users.
        
        Returns:
            QuerySet: All users with related roles and permissions
        """
        return User.objects.select_related().prefetch_related('roles__permissions').all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return User.objects.select_related().prefetch_related('roles__permissions').filter(id=user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email (str): The user email
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return User.objects.select_related().prefetch_related('roles__permissions').filter(email=email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username (str): The username
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return User.objects.select_related().prefetch_related('roles__permissions').filter(username=username).first()

    def create(self, **kwargs) -> User:
        """
        Create a new user.
        
        Args:
            **kwargs: User data
            
        Returns:
            User: The created user
        """
        # Extract roles if provided
        roles = kwargs.pop('roles', [])
        
        # Create user
        user = User.objects.create_user(**kwargs)
        
        # Assign roles if provided
        if roles:
            user.roles.set(roles)
        
        return user

    def update(self, user: User, **kwargs) -> User:
        """
        Update an existing user.
        
        Args:
            user (User): The user to update
            **kwargs: Updated user data
            
        Returns:
            User: The updated user
        """
        # Extract roles if provided
        roles = kwargs.pop('roles', None)
        
        # Update user fields
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.save()
        
        # Update roles if provided
        if roles is not None:
            user.roles.set(roles)
        
        return user

    def delete(self, user: User) -> bool:
        """
        Delete a user.
        
        Args:
            user (User): The user to delete
            
        Returns:
            bool: True if deleted successfully
        """
        user.delete()
        return True

    def search(self, query: str) -> QuerySet:
        """
        Search users by e-mail, username, first name or last name (case-insensitive).

        Args:
            query (str): The search term

        Returns:
            QuerySet: Matching users
        """
        return User.objects.filter(
            Q(email__icontains=query) | Q(username__icontains=query)
            | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    def get_users_by_role(self, role_name: str) -> QuerySet:
        """
        Get users by role name.
        
        Args:
            role_name (str): The role name
            
        Returns:
            QuerySet: Users with the specified role
        """
        return User.objects.filter(roles__name=role_name).distinct()

    def get_users_with_permission(self, permission_code: str) -> QuerySet:
        """
        Get users with a specific permission.
        
        Args:
            permission_code (str): The permission code
            
        Returns:
            QuerySet: Users with the specified permission
        """
        return User.objects.filter(roles__permissions__code=permission_code).distinct()

    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists by email.
        
        Args:
            email (str): The email to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        return User.objects.filter(email=email).exists()

    def exists_by_username(self, username: str) -> bool:
        """
        Check if a user exists by username.
        
        Args:
            username (str): The username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        return User.objects.filter(username=username).exists()

    def get_active_by_email(self, email: str) -> Optional[User]:
        """
        Get an active user by e-mail (case-insensitive).
        """
        return User.objects.filter(email__iexact=email, is_active=True).first()

    def update_password(self, user: User, raw_password: str) -> None:
        """
        Set a new password for a user (hashed by Django).
        """
        user.set_password(raw_password)
        user.save(update_fields=['password', 'updated_at'])

    def blacklist_refresh_tokens(self, user: User) -> int:
        """
        Blacklist every outstanding JWT refresh token of a user.
        """
        count = 0
        for outstanding in OutstandingToken.objects.filter(user=user):
            _, created = BlacklistedToken.objects.get_or_create(token=outstanding)
            count += int(created)
        return count
