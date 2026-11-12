"""
Permissions pour les availabilities.
"""
from rest_framework import permissions


class CanViewAvailability(permissions.BasePermission):
    """
    Permission pour voir les availabilities.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('availabilities.view')


class CanCreateAvailability(permissions.BasePermission):
    """
    Permission pour créer des availabilities.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('availabilities.create')


class CanUpdateAvailability(permissions.BasePermission):
    """
    Permission pour modifier des availabilities.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('availabilities.update')


class CanDeleteAvailability(permissions.BasePermission):
    """
    Permission pour supprimer des availabilities.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('availabilities.delete')