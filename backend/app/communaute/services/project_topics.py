"""
Adaptateur Forum ← DevStreet Hub (contrat ProjectDiscussionLink).

Chemin configuré :
  DEVSTREET_HUB_FORUM_ADAPTER=app.communaute.services.project_topics.create_linked_topic

Contrat d'appel : typiquement via WorkflowService.link_discussion (verrou projet).
L'idempotence sur ``hub_request_key`` reste assurée ici aussi (IntegrityError).
"""
from __future__ import annotations

from django.db import IntegrityError, transaction

from app.communaute.models import Publication
from app.communaute.services.publication_service import PublicationService

HUB_REQUEST_KEY_MAX_LEN = 64
DESCRIPTION_MAX_LEN = 20_000


def create_linked_topic(*, actor, project, task, title, body, request_key):
    """
    Crée ou reprend une discussion forum liée à un projet Hub.

    Idempotent sur ``request_key`` : le même appel renvoie le même id publication.
    """
    key = str(request_key or '').strip()
    if not key:
        raise ValueError('request_key obligatoire')
    if len(key) > HUB_REQUEST_KEY_MAX_LEN:
        raise ValueError(
            f'request_key trop long (max {HUB_REQUEST_KEY_MAX_LEN} caractères)'
        )

    existing = Publication.objects.filter(hub_request_key=key).first()
    if existing is not None:
        return existing.id

    titre = (title or '').strip() or f'Discussion — {project.title}'
    description = (body or '').strip()
    if task is not None:
        description = (
            f"{description}\n\n—\nTâche liée : #{task.id} — {task.title}"
            if description
            else f"Tâche liée : #{task.id} — {task.title}"
        )
    if not description:
        description = (
            f"Discussion ouverte depuis le projet « {project.title} » "
            f"sur DevStreet Hub."
        )
    if len(description) > DESCRIPTION_MAX_LEN:
        description = description[: DESCRIPTION_MAX_LEN - 1].rstrip() + '…'

    try:
        # PublicationService.create_discussion ouvre déjà un atomic() (savepoint).
        with transaction.atomic():
            publication = PublicationService().create_discussion(
                auteur=actor,
                titre=titre[:200],
                description=description,
                images=[],
                created_by=actor.id,
                updated_by=actor.id,
            )
            Publication.objects.filter(pk=publication.id).update(
                hub_request_key=key,
                projet_id=project.pk,
            )
            return publication.id
    except IntegrityError:
        raced = Publication.objects.filter(hub_request_key=key).first()
        if raced is not None:
            return raced.id
        raise
