"""
Permissions pour les images-publication.
"""
from rest_framework import permissions


class CanViewImagePublication(permissions.BasePermission):
    """
    Permission pour voir les images-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('images-publication.view')


class CanCreateImagePublication(permissions.BasePermission):
    """
    Permission pour créer des images-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('images-publication.create')


class CanUpdateImagePublication(permissions.BasePermission):
    """
    Permission pour modifier des images-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('images-publication.update')


class CanDeleteImagePublication(permissions.BasePermission):
    """
    Permission pour supprimer des images-publication.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('images-publication.delete')