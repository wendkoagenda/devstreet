"""
Permissions pour les candidatures.
"""
from rest_framework import permissions


class CanViewCandidature(permissions.BasePermission):
    """
    Permission pour voir les candidatures.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('candidatures.view')


class CanCreateCandidature(permissions.BasePermission):
    """
    Permission pour créer des candidatures.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('candidatures.create')


class CanUpdateCandidature(permissions.BasePermission):
    """
    Permission pour modifier des candidatures.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('candidatures.update')


class CanDeleteCandidature(permissions.BasePermission):
    """
    Permission pour supprimer des candidatures.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('candidatures.delete')