"""
Permissions pour les conversations.
"""
from rest_framework import permissions


class CanViewConversation(permissions.BasePermission):
    """
    Permission pour voir les conversations.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('conversations.view')


class CanCreateConversation(permissions.BasePermission):
    """
    Permission pour créer des conversations.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('conversations.create')


class CanUpdateConversation(permissions.BasePermission):
    """
    Permission pour modifier des conversations.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('conversations.update')


class CanDeleteConversation(permissions.BasePermission):
    """
    Permission pour supprimer des conversations.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('conversations.delete')