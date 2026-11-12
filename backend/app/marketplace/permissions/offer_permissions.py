"""
Permissions pour les offers.
"""
from rest_framework import permissions


class CanViewOffer(permissions.BasePermission):
    """
    Permission pour voir les offers.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('offers.view')


class CanCreateOffer(permissions.BasePermission):
    """
    Permission pour créer des offers.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('offers.create')


class CanUpdateOffer(permissions.BasePermission):
    """
    Permission pour modifier des offers.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('offers.update')


class CanDeleteOffer(permissions.BasePermission):
    """
    Permission pour supprimer des offers.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('offers.delete')