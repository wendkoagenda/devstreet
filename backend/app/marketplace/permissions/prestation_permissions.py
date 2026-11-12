"""
Permissions pour les prestations.
"""
from rest_framework import permissions


class CanViewPrestation(permissions.BasePermission):
    """
    Permission pour voir les prestations.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('prestations.view')


class CanCreatePrestation(permissions.BasePermission):
    """
    Permission pour créer des prestations.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('prestations.create')


class CanUpdatePrestation(permissions.BasePermission):
    """
    Permission pour modifier des prestations.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('prestations.update')


class CanDeletePrestation(permissions.BasePermission):
    """
    Permission pour supprimer des prestations.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('prestations.delete')