"""
Permissions pour les options-publication.
"""
from rest_framework import permissions


class CanViewOptionPublication(permissions.BasePermission):
    """
    Permission pour voir les options-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('options-publication.view')


class CanCreateOptionPublication(permissions.BasePermission):
    """
    Permission pour créer des options-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('options-publication.create')


class CanUpdateOptionPublication(permissions.BasePermission):
    """
    Permission pour modifier des options-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('options-publication.update')


class CanDeleteOptionPublication(permissions.BasePermission):
    """
    Permission pour supprimer des options-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('options-publication.delete')