"""
Permissions pour les elitesties.
"""
from rest_framework import permissions


class CanViewElitesty(permissions.BasePermission):
    """
    Permission pour voir les elitesties.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('elitesties.view')


class CanCreateElitesty(permissions.BasePermission):
    """
    Permission pour créer des elitesties.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('elitesties.create')


class CanUpdateElitesty(permissions.BasePermission):
    """
    Permission pour modifier des elitesties.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('elitesties.update')


class CanDeleteElitesty(permissions.BasePermission):
    """
    Permission pour supprimer des elitesties.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('elitesties.delete')