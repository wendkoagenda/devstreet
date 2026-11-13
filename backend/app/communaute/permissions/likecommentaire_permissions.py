"""
Permissions pour les likes-commentaire.
"""
from rest_framework import permissions


class CanViewLikeCommentaire(permissions.BasePermission):
    """
    Permission pour voir les likes-commentaire.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('likes-commentaire.view')


class CanCreateLikeCommentaire(permissions.BasePermission):
    """
    Permission pour créer des likes-commentaire.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('likes-commentaire.create')


class CanUpdateLikeCommentaire(permissions.BasePermission):
    """
    Permission pour modifier des likes-commentaire.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('likes-commentaire.update')


class CanDeleteLikeCommentaire(permissions.BasePermission):
    """
    Permission pour supprimer des likes-commentaire.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('likes-commentaire.delete')