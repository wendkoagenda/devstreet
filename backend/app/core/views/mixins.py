"""
Comportements communs des ViewSets de gestion des comptes et des rôles.
"""
from rest_framework import status
from rest_framework.response import Response

from app.core.services import audit_service
from app.core.services.access_policy import AccessDenied, AccessPolicy
from app.core.services.audit_service import Actions


class AccessPolicyMixin:
    """
    Fournit `self.policy` (politique d'accès de l'utilisateur connecté) et transforme un refus de la politique en
    réponse 403 avec un message clair, après l'avoir inscrit au journal d'audit.
    """

    @property
    def policy(self) -> AccessPolicy:
        return AccessPolicy(self.request.user)

    def handle_exception(self, exc):
        if isinstance(exc, AccessDenied):
            audit_service.record(
                Actions.ACCESS_DENIED, actor=self.request.user, request=self.request,
                metadata={'action': self.action, 'method': self.request.method, 'reason': str(exc)},
            )
            return Response({'error': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)
