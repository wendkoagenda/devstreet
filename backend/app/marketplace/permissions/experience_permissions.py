"""
Permissions pour les experiences.
"""
from rest_framework import permissions


class CanViewExperience(permissions.BasePermission):
    """
    Permission pour voir les experiences.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('experiences.view')


class CanCreateExperience(permissions.BasePermission):
    """
    Permission pour créer des experiences.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('experiences.create')


class CanUpdateExperience(permissions.BasePermission):
    """
    Permission pour modifier des experiences.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('experiences.update')


class CanDeleteExperience(permissions.BasePermission):
    """
    Permission pour supprimer des experiences.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('experiences.delete')