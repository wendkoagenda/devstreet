"""
Permissions pour les liens-invitation.
"""
from rest_framework import permissions


class CanViewLienInvitation(permissions.BasePermission):
    """
    Permission pour voir les liens-invitation.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('liens-invitation.view')


class CanCreateLienInvitation(permissions.BasePermission):
    """
    Permission pour créer des liens-invitation.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('liens-invitation.create')


class CanUpdateLienInvitation(permissions.BasePermission):
    """
    Permission pour modifier des liens-invitation.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('liens-invitation.update')


class CanDeleteLienInvitation(permissions.BasePermission):
    """
    Permission pour supprimer des liens-invitation.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('liens-invitation.delete')