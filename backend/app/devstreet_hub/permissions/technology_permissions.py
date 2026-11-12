"""
Permissions pour les technologies.
"""

from rest_framework import permissions


class CanViewTechnology(permissions.BasePermission):
    """
    Permission pour voir les technologies.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("technologies.view")


class CanCreateTechnology(permissions.BasePermission):
    """
    Permission pour créer des technologies.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("technologies.create")


class CanUpdateTechnology(permissions.BasePermission):
    """
    Permission pour modifier des technologies.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("technologies.update")


class CanDeleteTechnology(permissions.BasePermission):
    """
    Permission pour supprimer des technologies.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("technologies.delete")
