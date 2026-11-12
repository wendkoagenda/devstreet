"""
Permissions pour les reviews.
"""
from rest_framework import permissions


class CanViewReview(permissions.BasePermission):
    """
    Permission pour voir les reviews.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('reviews.view')


class CanCreateReview(permissions.BasePermission):
    """
    Permission pour créer des reviews.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('reviews.create')


class CanUpdateReview(permissions.BasePermission):
    """
    Permission pour modifier des reviews.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('reviews.update')


class CanDeleteReview(permissions.BasePermission):
    """
    Permission pour supprimer des reviews.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('reviews.delete')