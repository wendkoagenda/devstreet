"""
Permissions pour les gados.
"""
from rest_framework import permissions


class CanViewGado(permissions.BasePermission):
    """
    Permission pour voir les gados.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('gados.view')


class CanCreateGado(permissions.BasePermission):
    """
    Permission pour créer des gados.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('gados.create')


class CanUpdateGado(permissions.BasePermission):
    """
    Permission pour modifier des gados.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('gados.update')


class CanDeleteGado(permissions.BasePermission):
    """
    Permission pour supprimer des gados.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('gados.delete')