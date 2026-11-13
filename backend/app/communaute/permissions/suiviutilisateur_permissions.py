"""
Permissions pour les suivis-utilisateur.
"""
from rest_framework import permissions


class CanViewSuiviUtilisateur(permissions.BasePermission):
    """
    Permission pour voir les suivis-utilisateur.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('suivis-utilisateur.view')


class CanCreateSuiviUtilisateur(permissions.BasePermission):
    """
    Permission pour créer des suivis-utilisateur.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('suivis-utilisateur.create')


class CanUpdateSuiviUtilisateur(permissions.BasePermission):
    """
    Permission pour modifier des suivis-utilisateur.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('suivis-utilisateur.update')


class CanDeleteSuiviUtilisateur(permissions.BasePermission):
    """
    Permission pour supprimer des suivis-utilisateur.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('suivis-utilisateur.delete')