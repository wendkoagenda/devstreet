"""
Permissions pour les participations-espace.
"""
from rest_framework import permissions


class CanViewParticipationEspace(permissions.BasePermission):
    """
    Permission pour voir les participations-espace.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('participations-espace.view')


class CanCreateParticipationEspace(permissions.BasePermission):
    """
    Permission pour créer des participations-espace.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('participations-espace.create')


class CanUpdateParticipationEspace(permissions.BasePermission):
    """
    Permission pour modifier des participations-espace.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('participations-espace.update')


class CanDeleteParticipationEspace(permissions.BasePermission):
    """
    Permission pour supprimer des participations-espace.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('participations-espace.delete')