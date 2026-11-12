"""
Classes de permissions personnalisées pour le contrôle d'accès basé sur les utilisateurs.
"""
from rest_framework import permissions
from typing import Any


class HasPermission(permissions.BasePermission):
    """
    Classe de permission personnalisée qui vérifie si l'utilisateur a une permission spécifique via ses rôles.
    """
    
    def __init__(self, permission_code: str):
        """
        Initialise avec un code de permission spécifique.
        
        Args:
            permission_code (str): Le code de permission à vérifier
        """
        self.permission_code = permission_code

    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur a la permission requise.
        
        Args:
            request: La requête HTTP
            view: La vue Django REST Framework
            
        Returns:
            bool: True si l'utilisateur a la permission, False sinon
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Les superutilisateurs ont toutes les permissions
        if request.user.is_superuser:
            return True
        
        return request.user.has_permission(self.permission_code)


class IsOwnerOrHasPermission(permissions.BasePermission):
    """
    Permission qui permet l'accès si l'utilisateur est le propriétaire de l'objet ou a une permission spécifique.
    """
    
    def __init__(self, permission_code: str, owner_field: str = 'user'):
        """
        Initialise avec un code de permission et un champ propriétaire.
        
        Args:
            permission_code (str): Le code de permission à vérifier
            owner_field (str): Le nom du champ qui identifie le propriétaire
        """
        self.permission_code = permission_code
        self.owner_field = owner_field

    def has_permission(self, request, view):
        """
        Vérifie les permissions au niveau de la vue.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """
        Vérifie les permissions au niveau de l'objet.
        
        Args:
            request: La requête HTTP
            view: La vue Django REST Framework
            obj: L'objet à vérifier
            
        Returns:
            bool: True si l'utilisateur a la permission, False sinon
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Les superutilisateurs ont toutes les permissions
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est le propriétaire
        owner = getattr(obj, self.owner_field, None)
        if owner == request.user:
            return True
        
        # Vérifier si l'utilisateur a la permission spécifique
        return request.user.has_permission(self.permission_code)


class RoleBasedPermission(permissions.BasePermission):
    """
    Permission basée sur les rôles de l'utilisateur.
    """
    
    def __init__(self, required_roles: list):
        """
        Initialise avec une liste de rôles requis.
        
        Args:
            required_roles (list): Liste des noms de rôles requis
        """
        self.required_roles = required_roles

    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur a au moins un des rôles requis.
        
        Args:
            request: La requête HTTP
            view: La vue Django REST Framework
            
        Returns:
            bool: True si l'utilisateur a au moins un rôle requis, False sinon
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Les superutilisateurs ont toutes les permissions
        if request.user.is_superuser:
            return True
        
        user_roles = request.user.get_roles()
        return any(role in user_roles for role in self.required_roles)


class PermissionRequiredMixin:
    """
    Mixin pour ajouter facilement des vérifications de permissions aux vues.
    """
    permission_code = None
    
    def get_permission_code(self):
        """
        Retourne le code de permission requis pour cette vue.
        
        Returns:
            str: Le code de permission
        """
        return self.permission_code
    
    def check_permissions(self, request):
        """
        Vérifie les permissions pour la requête.
        
        Args:
            request: La requête HTTP
            
        Raises:
            PermissionDenied: Si l'utilisateur n'a pas la permission
        """
        permission_code = self.get_permission_code()
        if permission_code and not request.user.has_permission(permission_code):
            self.permission_denied(
                request,
                message=f"Permission '{permission_code}' requise pour cette action."
            )


def permission_required(permission_code: str):
    """
    Décorateur pour vérifier les permissions sur les méthodes de vue.
    
    Args:
        permission_code (str): Le code de permission requis
        
    Returns:
        function: Le décorateur
    """
    def decorator(view_func):
        def wrapped_view(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return self.permission_denied(request, message="Authentification requise.")
            
            if not request.user.is_superuser and not request.user.has_permission(permission_code):
                return self.permission_denied(
                    request,
                    message=f"Permission '{permission_code}' requise pour cette action."
                )
            
            return view_func(self, request, *args, **kwargs)
        return wrapped_view
    return decorator


class DynamicPermission(permissions.BasePermission):
    """
    Permission dynamique qui peut être configurée au runtime.
    """
    
    def __init__(self, permission_checker=None):
        """
        Initialise avec une fonction de vérification de permission personnalisée.
        
        Args:
            permission_checker (callable): Fonction qui prend (user, request, view, obj=None) et retourne bool
        """
        self.permission_checker = permission_checker

    def has_permission(self, request, view):
        """
        Vérifie les permissions au niveau de la vue.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        if self.permission_checker:
            return self.permission_checker(request.user, request, view)
        
        return True

    def has_object_permission(self, request, view, obj):
        """
        Vérifie les permissions au niveau de l'objet.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        if self.permission_checker:
            return self.permission_checker(request.user, request, view, obj)
        
        return True


# Permissions prédéfinies pour les opérations CRUD communes
class CanViewUsers(HasPermission):
    """Permission pour voir les utilisateurs."""
    def __init__(self):
        super().__init__('users.view')


class CanCreateUsers(HasPermission):
    """Permission pour créer des utilisateurs."""
    def __init__(self):
        super().__init__('users.create')


class CanUpdateUsers(HasPermission):
    """Permission pour modifier des utilisateurs."""
    def __init__(self):
        super().__init__('users.update')


class CanDeleteUsers(HasPermission):
    """Permission pour supprimer des utilisateurs."""
    def __init__(self):
        super().__init__('users.delete')


class CanViewRoles(HasPermission):
    """Permission pour voir les rôles."""
    def __init__(self):
        super().__init__('roles.view')


class CanCreateRoles(HasPermission):
    """Permission pour créer des rôles."""
    def __init__(self):
        super().__init__('roles.create')


class CanUpdateRoles(HasPermission):
    """Permission pour modifier des rôles."""
    def __init__(self):
        super().__init__('roles.update')


class CanDeleteRoles(HasPermission):
    """Permission pour supprimer des rôles."""
    def __init__(self):
        super().__init__('roles.delete')


class CanViewPermissions(HasPermission):
    """Permission pour voir les permissions."""
    def __init__(self):
        super().__init__('permissions.view')


class CanCreatePermissions(HasPermission):
    """Permission pour créer des permissions."""
    def __init__(self):
        super().__init__('permissions.create')


class CanUpdatePermissions(HasPermission):
    """Permission pour modifier des permissions."""
    def __init__(self):
        super().__init__('permissions.update')


class CanDeletePermissions(HasPermission):
    """Permission pour supprimer des permissions."""
    def __init__(self):
        super().__init__('permissions.delete')