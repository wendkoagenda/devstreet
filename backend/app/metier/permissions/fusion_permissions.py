"""
Permissions pour les fusions.
"""
from rest_framework import permissions


class CanViewFusion(permissions.BasePermission):
    """
    Permission pour voir les fusions.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('fusions.view')


class CanCreateFusion(permissions.BasePermission):
    """
    Permission pour créer des fusions.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('fusions.create')


class CanUpdateFusion(permissions.BasePermission):
    """
    Permission pour modifier des fusions.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('fusions.update')


class CanDeleteFusion(permissions.BasePermission):
    """
    Permission pour supprimer des fusions.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('fusions.delete')