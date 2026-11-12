"""
User service layer for business logic operations.
"""
from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.core.repositories.user_repository import UserRepository
from app.core.repositories.role_repository import RoleRepository

User = get_user_model()


class UserService:
    """
    Service class for user-related business logic.
    """

    def __init__(self):
        self.user_repository = UserRepository()
        self.role_repository = RoleRepository()

    def get_all_users(self) -> QuerySet:
        """
        Get all users.
        
        Returns:
            QuerySet: All users
        """
        return self.user_repository.get_all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.user_repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email (str): The user email
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.user_repository.get_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username (str): The username
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.user_repository.get_by_username(username)

    def search_users(self, query: str) -> QuerySet:
        """
        Search users by e-mail, username or name.

        Args:
            query (str): The search term

        Returns:
            QuerySet: Matching users
        """
        return self.user_repository.search(query)

    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user with validation.
        
        Args:
            user_data (Dict[str, Any]): User data
            
        Returns:
            User: The created user
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        required_fields = ['email', 'username', 'first_name', 'last_name']
        for field in required_fields:
            if not user_data.get(field):
                raise ValidationError(f"{field} is required")

        # Check if email already exists
        if self.user_repository.exists_by_email(user_data['email']):
            raise ValidationError("User with this email already exists")

        # Check if username already exists
        if self.user_repository.exists_by_username(user_data['username']):
            raise ValidationError("User with this username already exists")

        # Validate and process roles
        role_names = user_data.pop('role_names', [])
        roles = []
        if role_names:
            for role_name in role_names:
                role = self.role_repository.get_by_name(role_name)
                if not role:
                    raise ValidationError(f"Role '{role_name}' does not exist")
                roles.append(role)

        # Create user (create_user will handle password hashing)
        user_data['roles'] = roles
        return self.user_repository.create(**user_data)

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user_id (int): The user ID
            user_data (Dict[str, Any]): Updated user data
            
        Returns:
            Optional[User]: The updated user if found, None otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None

        # Check email uniqueness if email is being updated
        if 'email' in user_data and user_data['email'] != user.email:
            if self.user_repository.exists_by_email(user_data['email']):
                raise ValidationError("User with this email already exists")

        # Check username uniqueness if username is being updated
        if 'username' in user_data and user_data['username'] != user.username:
            if self.user_repository.exists_by_username(user_data['username']):
                raise ValidationError("User with this username already exists")

        # Validate and process roles
        role_names = user_data.pop('role_names', None)
        if role_names is not None:
            roles = []
            for role_name in role_names:
                role = self.role_repository.get_by_name(role_name)
                if not role:
                    raise ValidationError(f"Role '{role_name}' does not exist")
                roles.append(role)
            user_data['roles'] = roles

        # Handle password update (use set_password for proper hashing)
        password = user_data.pop('password', None)
        
        # Update other fields first
        updated_user = self.user_repository.update(user, **user_data)
        
        # Set password separately if provided
        if password:
            updated_user.set_password(password)
            updated_user.save()
        
        return updated_user

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            bool: True if deleted successfully, False if user not found
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        return self.user_repository.delete(user)

    def assign_role_to_user(self, user_id: int, role_name: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id (int): The user ID
            role_name (str): The role name
            
        Returns:
            bool: True if assigned successfully
            
        Raises:
            ValidationError: If user or role not found
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")

        role = self.role_repository.get_by_name(role_name)
        if not role:
            raise ValidationError("Role not found")

        user.roles.add(role)
        return True

    def remove_role_from_user(self, user_id: int, role_name: str) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id (int): The user ID
            role_name (str): The role name
            
        Returns:
            bool: True if removed successfully
            
        Raises:
            ValidationError: If user or role not found
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")

        role = self.role_repository.get_by_name(role_name)
        if not role:
            raise ValidationError("Role not found")

        user.roles.remove(role)
        return True

    def get_users_by_role(self, role_name: str) -> QuerySet:
        """
        Get users by role name.
        
        Args:
            role_name (str): The role name
            
        Returns:
            QuerySet: Users with the specified role
        """
        return self.user_repository.get_users_by_role(role_name)

    def get_users_with_permission(self, permission_code: str) -> QuerySet:
        """
        Get users with a specific permission.
        
        Args:
            permission_code (str): The permission code
            
        Returns:
            QuerySet: Users with the specified permission
        """
        return self.user_repository.get_users_with_permission(permission_code)

    def check_user_permission(self, user_id: int, permission_code: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id (int): The user ID
            permission_code (str): The permission code
            
        Returns:
            bool: True if user has the permission, False otherwise
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        return user.has_permission(permission_code)

    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            List[str]: List of permission codes
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return []
        
        return user.get_all_permissions()

    def get_user_roles(self, user_id: int) -> List[str]:
        """
        Get all roles for a user.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            List[str]: List of role names
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return []
        
        return user.get_roles()