"""
Permissions pour les avis-choix.
"""
from rest_framework import permissions


class CanViewAvisChoix(permissions.BasePermission):
    """
    Permission pour voir les avis-choix.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('avis-choix.view')


class CanCreateAvisChoix(permissions.BasePermission):
    """
    Permission pour créer des avis-choix.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('avis-choix.create')


class CanUpdateAvisChoix(permissions.BasePermission):
    """
    Permission pour modifier des avis-choix.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('avis-choix.update')


class CanDeleteAvisChoix(permissions.BasePermission):
    """
    Permission pour supprimer des avis-choix.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('avis-choix.delete')