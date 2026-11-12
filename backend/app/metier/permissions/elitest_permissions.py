"""
Permissions pour les elitests.
"""
from rest_framework import permissions


class CanViewElitest(permissions.BasePermission):
    """
    Permission pour voir les elitests.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('elitests.view')


class CanCreateElitest(permissions.BasePermission):
    """
    Permission pour créer des elitests.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('elitests.create')


class CanUpdateElitest(permissions.BasePermission):
    """
    Permission pour modifier des elitests.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('elitests.update')


class CanDeleteElitest(permissions.BasePermission):
    """
    Permission pour supprimer des elitests.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('elitests.delete')