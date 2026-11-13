"""
Permissions pour les messages.
"""
from rest_framework import permissions


class CanViewMessage(permissions.BasePermission):
    """
    Permission pour voir les messages.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('messages.view')


class CanCreateMessage(permissions.BasePermission):
    """
    Permission pour créer des messages.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('messages.create')


class CanUpdateMessage(permissions.BasePermission):
    """
    Permission pour modifier des messages.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('messages.update')


class CanDeleteMessage(permissions.BasePermission):
    """
    Permission pour supprimer des messages.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('messages.delete')