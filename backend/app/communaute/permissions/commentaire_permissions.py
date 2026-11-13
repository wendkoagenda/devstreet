"""
Permissions pour les commentaires.
"""
from rest_framework import permissions


class CanViewCommentaire(permissions.BasePermission):
    """
    Permission pour voir les commentaires.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('commentaires.view')


class CanCreateCommentaire(permissions.BasePermission):
    """
    Permission pour créer des commentaires.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('commentaires.create')


class CanUpdateCommentaire(permissions.BasePermission):
    """
    Permission pour modifier des commentaires.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('commentaires.update')


class CanDeleteCommentaire(permissions.BasePermission):
    """
    Permission pour supprimer des commentaires.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('commentaires.delete')