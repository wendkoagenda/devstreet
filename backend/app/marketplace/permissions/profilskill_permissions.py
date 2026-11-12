"""
Permissions pour les profil-skills.
"""
from rest_framework import permissions


class CanViewProfilSkill(permissions.BasePermission):
    """
    Permission pour voir les profil-skills.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profil-skills.view')


class CanCreateProfilSkill(permissions.BasePermission):
    """
    Permission pour créer des profil-skills.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profil-skills.create')


class CanUpdateProfilSkill(permissions.BasePermission):
    """
    Permission pour modifier des profil-skills.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profil-skills.update')


class CanDeleteProfilSkill(permissions.BasePermission):
    """
    Permission pour supprimer des profil-skills.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('profil-skills.delete')