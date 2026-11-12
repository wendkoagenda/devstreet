"""
Permissions pour les dragons.
"""
from rest_framework import permissions


class CanViewDragon(permissions.BasePermission):
    """
    Permission pour voir les dragons.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('dragons.view')


class CanCreateDragon(permissions.BasePermission):
    """
    Permission pour créer des dragons.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('dragons.create')


class CanUpdateDragon(permissions.BasePermission):
    """
    Permission pour modifier des dragons.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('dragons.update')


class CanDeleteDragon(permissions.BasePermission):
    """
    Permission pour supprimer des dragons.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('dragons.delete')