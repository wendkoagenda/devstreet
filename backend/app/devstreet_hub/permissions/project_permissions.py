"""
Permissions pour les projects.
"""

from rest_framework import permissions


class CanViewProject(permissions.BasePermission):
    """
    Permission pour voir les projects.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("projects.view")


class CanCreateProject(permissions.BasePermission):
    """
    Permission pour créer des projects.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("projects.create")


class CanUpdateProject(permissions.BasePermission):
    """
    Permission pour modifier des projects.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("projects.update")


class CanDeleteProject(permissions.BasePermission):
    """
    Permission pour supprimer des projects.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("projects.delete")
