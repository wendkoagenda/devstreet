"""
Permissions pour les profil-histories.
"""
from rest_framework import permissions


class CanViewProfilHistory(permissions.BasePermission):
    """
    Permission pour voir les profil-histories.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profil-histories.view')


class CanCreateProfilHistory(permissions.BasePermission):
    """
    Permission pour créer des profil-histories.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profil-histories.create')


class CanUpdateProfilHistory(permissions.BasePermission):
    """
    Permission pour modifier des profil-histories.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profil-histories.update')


class CanDeleteProfilHistory(permissions.BasePermission):
    """
    Permission pour supprimer des profil-histories.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profil-histories.delete')