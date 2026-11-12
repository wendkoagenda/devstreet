"""
Permissions pour les votes-sondage.
"""
from rest_framework import permissions


class CanViewVoteSondage(permissions.BasePermission):
    """
    Permission pour voir les votes-sondage.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('votes-sondage.view')


class CanCreateVoteSondage(permissions.BasePermission):
    """
    Permission pour créer des votes-sondage.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('votes-sondage.create')


class CanUpdateVoteSondage(permissions.BasePermission):
    """
    Permission pour modifier des votes-sondage.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('votes-sondage.update')


class CanDeleteVoteSondage(permissions.BasePermission):
    """
    Permission pour supprimer des votes-sondage.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('votes-sondage.delete')