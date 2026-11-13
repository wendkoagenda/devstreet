"""
Permissions pour les espaces.
"""
from rest_framework import permissions


class CanViewEspace(permissions.BasePermission):
    """
    Permission pour voir les espaces.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('espaces.view')


class CanCreateEspace(permissions.BasePermission):
    """
    Permission pour créer des espaces.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('espaces.create')


class CanUpdateEspace(permissions.BasePermission):
    """
    Permission pour modifier des espaces.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('espaces.update')


class CanDeleteEspace(permissions.BasePermission):
    """
    Permission pour supprimer des espaces.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('espaces.delete')