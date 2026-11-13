"""
Permissions pour les likes-publication.
"""
from rest_framework import permissions


class CanViewLikePublication(permissions.BasePermission):
    """
    Permission pour voir les likes-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('likes-publication.view')


class CanCreateLikePublication(permissions.BasePermission):
    """
    Permission pour créer des likes-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('likes-publication.create')


class CanUpdateLikePublication(permissions.BasePermission):
    """
    Permission pour modifier des likes-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('likes-publication.update')


class CanDeleteLikePublication(permissions.BasePermission):
    """
    Permission pour supprimer des likes-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('likes-publication.delete')