"""Permissions métier construites sur l'IAM existant, sans nouvelle authentification."""

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from app.core.services.audit_service import record


def require_permission(actor, code):
    if not getattr(actor, "is_authenticated", False):
        raise NotAuthenticated()
    if not actor.is_active or not actor.has_permission(code):
        record("access.denied", actor=actor, metadata={"permission": code})
        raise PermissionDenied("Votre rôle IAM ne permet pas cette action.")


def require_maintainer(actor, project, repository):
    if not actor.is_authenticated or not repository.is_maintainer(project, actor):
        raise PermissionDenied(
            "Vous devez être propriétaire ou mainteneur de ce projet."
        )


def require_owner(actor, project):
    if not actor.is_authenticated or project.owner_id != actor.pk:
        raise PermissionDenied("Action réservée au propriétaire du projet.")
