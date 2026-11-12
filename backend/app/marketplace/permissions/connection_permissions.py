"""
Permissions pour les connections.
"""
from rest_framework import permissions


class CanViewConnection(permissions.BasePermission):
    """
    Permission pour voir les connections.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('connections.view')


class CanCreateConnection(permissions.BasePermission):
    """
    Permission pour créer des connections.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('connections.create')


class CanUpdateConnection(permissions.BasePermission):
    """
    Permission pour modifier des connections.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('connections.update')


class CanDeleteConnection(permissions.BasePermission):
    """
    Permission pour supprimer des connections.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('connections.delete')