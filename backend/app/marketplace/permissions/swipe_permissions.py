"""
Permissions pour les swipes.
"""
from rest_framework import permissions


class CanViewSwipe(permissions.BasePermission):
    """
    Permission pour voir les swipes.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('swipes.view')


class CanCreateSwipe(permissions.BasePermission):
    """
    Permission pour créer des swipes.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('swipes.create')


class CanUpdateSwipe(permissions.BasePermission):
    """
    Permission pour modifier des swipes.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('swipes.update')


class CanDeleteSwipe(permissions.BasePermission):
    """
    Permission pour supprimer des swipes.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('swipes.delete')