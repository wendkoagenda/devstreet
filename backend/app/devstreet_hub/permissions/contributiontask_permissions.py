"""
Permissions pour les contribution-tasks.
"""

from rest_framework import permissions


class CanViewContributionTask(permissions.BasePermission):
    """
    Permission pour voir les contribution-tasks.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("contribution-tasks.view")


class CanCreateContributionTask(permissions.BasePermission):
    """
    Permission pour créer des contribution-tasks.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("contribution-tasks.create")


class CanUpdateContributionTask(permissions.BasePermission):
    """
    Permission pour modifier des contribution-tasks.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("contribution-tasks.update")


class CanDeleteContributionTask(permissions.BasePermission):
    """
    Permission pour supprimer des contribution-tasks.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(
            request.user and request.user.is_authenticated
        ) and request.user.has_permission("contribution-tasks.delete")
