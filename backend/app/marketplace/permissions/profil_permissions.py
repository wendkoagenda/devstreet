"""
Permissions pour les profils.
"""
from rest_framework import permissions


class CanViewProfil(permissions.BasePermission):
    """
    Permission pour voir les profils.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profils.view')


class CanCreateProfil(permissions.BasePermission):
    """
    Permission pour créer des profils.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profils.create')


class CanUpdateProfil(permissions.BasePermission):
    """
    Permission pour modifier des profils.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profils.update')


class CanDeleteProfil(permissions.BasePermission):
    """
    Permission pour supprimer des profils.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profils.delete')