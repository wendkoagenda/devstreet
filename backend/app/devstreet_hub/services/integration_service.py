"""Contrats pour les futures apps forum/marketplace et réception des événements de forge."""

import hashlib
import hmac
import json
import re
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from app.devstreet_hub.conf import config
from app.devstreet_hub.repositories.workflow_repository import WorkflowRepository
from app.devstreet_hub.services.errors import ExternalUnavailable


def selectable_evidence(actor):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionDenied()
    return WorkflowRepository().public_evidence(actor.pk)


def validate_application_evidence(actor, contribution_id):
    """La marketplace doit vérifier en plus que la candidature appartient à actor."""
    return get_object_or_404(selectable_evidence(actor), pk=contribution_id)


def receive_webhook(body, signature, delivery_id, event):
    secret = config("GITEA_WEBHOOK_SECRET")
    if not secret:
        raise ExternalUnavailable("Webhook Gitea non configuré.")
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise PermissionDenied("Signature du webhook invalide.")
    if not re.fullmatch(r"[A-Za-z0-9-]{1,100}", delivery_id or ""):
        raise ValidationError("Identifiant de livraison absent ou invalide.")
    try:
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError()
    except (ValueError, UnicodeDecodeError) as error:
        raise ValidationError("Corps du webhook invalide.") from error
    repo = WorkflowRepository()
    with transaction.atomic():
        if not repo.register_delivery(delivery_id):
            return {"duplicate": True}
        if event != "push":
            return {"ignored": True}
        repository_data = payload.get("repository")
        if not isinstance(repository_data, dict) or not isinstance(
            repository_data.get("id"), int
        ):
            raise ValidationError("Dépôt absent de l’événement.")
        repository = repo.repository_by_forge_id(repository_data["id"])
        sha = payload.get("after", "")
        if (
            repository
            and payload.get("ref") == "refs/heads/" + repository.default_branch
        ):
            if not isinstance(sha, str) or not re.fullmatch(r"[a-fA-F0-9]{40,64}", sha):
                raise ValidationError("SHA du webhook invalide.")
            # Information de fraîcheur uniquement : toute analyse relit la référence dans Gitea.
            repo.save(repository, current_sha=sha)
    return {"received": True}
