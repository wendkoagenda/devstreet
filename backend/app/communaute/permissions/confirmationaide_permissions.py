"""
Permissions pour les confirmations-aide.
"""
from rest_framework import permissions


class CanViewConfirmationAide(permissions.BasePermission):
    """
    Permission pour voir les confirmations-aide.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('confirmations-aide.view')


class CanCreateConfirmationAide(permissions.BasePermission):
    """
    Permission pour créer des confirmations-aide.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('confirmations-aide.create')


class CanUpdateConfirmationAide(permissions.BasePermission):
    """
    Permission pour modifier des confirmations-aide.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('confirmations-aide.update')


class CanDeleteConfirmationAide(permissions.BasePermission):
    """
    Permission pour supprimer des confirmations-aide.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('confirmations-aide.delete')