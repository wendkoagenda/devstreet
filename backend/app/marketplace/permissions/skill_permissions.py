"""
Permissions pour les skills.
"""
from rest_framework import permissions


class CanViewSkill(permissions.BasePermission):
    """
    Permission pour voir les skills.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('skills.view')


class CanCreateSkill(permissions.BasePermission):
    """
    Permission pour créer des skills.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('skills.create')


class CanUpdateSkill(permissions.BasePermission):
    """
    Permission pour modifier des skills.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('skills.update')


class CanDeleteSkill(permissions.BasePermission):
    """
    Permission pour supprimer des skills.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('skills.delete')