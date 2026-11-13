"""
Permissions pour les notifications-resume.
"""
from rest_framework import permissions


class CanViewNotificationResume(permissions.BasePermission):
    """
    Permission pour voir les notifications-resume.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('notifications-resume.view')


class CanCreateNotificationResume(permissions.BasePermission):
    """
    Permission pour créer des notifications-resume.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('notifications-resume.create')


class CanUpdateNotificationResume(permissions.BasePermission):
    """
    Permission pour modifier des notifications-resume.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('notifications-resume.update')


class CanDeleteNotificationResume(permissions.BasePermission):
    """
    Permission pour supprimer des notifications-resume.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('notifications-resume.delete')