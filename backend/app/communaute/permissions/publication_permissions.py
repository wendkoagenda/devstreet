"""
Permissions pour les publications.
"""
from rest_framework import permissions


class CanViewPublication(permissions.BasePermission):
    """
    Permission pour voir les publications.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('publications.view')


class CanCreatePublication(permissions.BasePermission):
    """
    Permission pour créer des publications.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('publications.create')


class CanUpdatePublication(permissions.BasePermission):
    """
    Permission pour modifier des publications.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('publications.update')


class CanDeletePublication(permissions.BasePermission):
    """
    Permission pour supprimer des publications.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('publications.delete')