"""
Permissions pour les companies.
"""
from rest_framework import permissions


class CanViewCompany(permissions.BasePermission):
    """
    Permission pour voir les companies.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('companies.view')


class CanCreateCompany(permissions.BasePermission):
    """
    Permission pour créer des companies.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('companies.create')


class CanUpdateCompany(permissions.BasePermission):
    """
    Permission pour modifier des companies.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('companies.update')


class CanDeleteCompany(permissions.BasePermission):
    """
    Permission pour supprimer des companies.
    """

    def has_permission(self, request, view):
        # Un visiteur anonyme est refusé (401) au lieu de provoquer une erreur 500
        return bool(request.user and request.user.is_authenticated) and request.user.has_permission('companies.delete')