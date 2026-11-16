"""
Adaptateur Forum ← DevStreet Hub (contrat ProjectDiscussionLink).

Chemin configuré :
  DEVSTREET_HUB_FORUM_ADAPTER=app.communaute.services.project_topics.create_linked_topic

Contrat d'appel : typiquement via WorkflowService.link_discussion / link_forum_post.
L'idempotence sur ``hub_request_key`` reste assurée ici aussi (IntegrityError).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.db import IntegrityError, transaction

from app.communaute.models import Publication
from app.communaute.services.publication_service import PublicationService
from app.communaute.services.tag_service import TagService

HUB_REQUEST_KEY_MAX_LEN = 64
DESCRIPTION_MAX_LEN = 20_000
ALLOWED_KINDS = frozenset({'DISCUSSION', 'APPLICATION', 'ENTRAIDE'})


def list_linked_publications(*, project_id: int, kind: Optional[str] = None) -> List[Dict[str, Any]]:
    """Publications forum déjà liées à un projet hub."""
    qs = Publication.objects.filter(projet_id=project_id).order_by('-id')
    if kind:
        cleaned = str(kind).strip().upper()
        if cleaned in ALLOWED_KINDS:
            qs = qs.filter(type=cleaned)
    return [
        {
            'id': pub.id,
            'type': pub.type,
            'titre': pub.titre,
            'created_at': pub.created_at.isoformat() if pub.created_at else None,
        }
        for pub in qs[:20]
    ]


def create_linked_topic(*, actor, project, task, title, body, request_key, **kwargs):
    """
    Compat historique : crée une DISCUSSION liée (FORUM_ADAPTER).

    Les kwargs supplémentaires (kind, lien_app, …) sont transmis à
    ``create_linked_publication``.
    """
    return create_linked_publication(
        actor=actor,
        project=project,
        task=task,
        title=title,
        body=body,
        request_key=request_key,
        kind=kwargs.get('kind') or 'DISCUSSION',
        lien_app=kwargs.get('lien_app'),
        plateforme_app=kwargs.get('plateforme_app') or 'WEB',
        tags_data=kwargs.get('tags_data'),
        images=kwargs.get('images'),
    )


def create_linked_publication(
    *,
    actor,
    project,
    task=None,
    title,
    body,
    request_key,
    kind='DISCUSSION',
    lien_app=None,
    plateforme_app='WEB',
    tags_data=None,
    images=None,
):
    """
    Crée ou reprend une publication forum liée à un projet Hub.

    Idempotent sur ``request_key`` : le même appel renvoie le même id publication.
    Kinds supportés : DISCUSSION, APPLICATION, ENTRAIDE.
    """
    key = str(request_key or '').strip()
    if not key:
        raise ValueError('request_key obligatoire')
    if len(key) > HUB_REQUEST_KEY_MAX_LEN:
        raise ValueError(
            f'request_key trop long (max {HUB_REQUEST_KEY_MAX_LEN} caractères)'
        )

    pub_kind = str(kind or 'DISCUSSION').strip().upper()
    if pub_kind not in ALLOWED_KINDS:
        raise ValueError(
            'kind invalide (DISCUSSION, APPLICATION ou ENTRAIDE).'
        )

    existing = Publication.objects.filter(hub_request_key=key).first()
    if existing is not None:
        return existing.id

    titre = (title or '').strip() or f'{pub_kind.title()} — {project.title}'
    description = (body or '').strip()
    if task is not None:
        description = (
            f"{description}\n\n—\nTâche liée : #{task.id} — {task.title}"
            if description
            else f"Tâche liée : #{task.id} — {task.title}"
        )
    if not description:
        description = (
            f"Publication ouverte depuis le projet « {project.title} » "
            f"sur DevStreet Hub."
        )
    if len(description) > DESCRIPTION_MAX_LEN:
        description = description[: DESCRIPTION_MAX_LEN - 1].rstrip() + '…'

    service = PublicationService()
    media = images or []

    try:
        with transaction.atomic():
            if pub_kind == 'APPLICATION':
                publication = service.create_application(
                    auteur=actor,
                    titre=titre[:200],
                    description=description,
                    lien_app=lien_app or '',
                    plateforme_app=plateforme_app or 'WEB',
                    images=media,
                    created_by=actor.id,
                    updated_by=actor.id,
                )
            elif pub_kind == 'ENTRAIDE':
                publication = service.create_entraide(
                    auteur=actor,
                    titre=titre[:200],
                    description=description,
                    images=media,
                    created_by=actor.id,
                    updated_by=actor.id,
                )
            else:
                publication = service.create_discussion(
                    auteur=actor,
                    titre=titre[:200],
                    description=description,
                    images=media,
                    created_by=actor.id,
                    updated_by=actor.id,
                )

            Publication.objects.filter(pk=publication.id).update(
                hub_request_key=key,
                projet_id=project.pk,
            )

            TagService().set_publication_tags(
                publication,
                tags_data or [],
                acteur_id=actor.id,
                auto_follow=True,
                membre=actor,
            )
            return publication.id
    except IntegrityError:
        raced = Publication.objects.filter(hub_request_key=key).first()
        if raced is not None:
            return raced.id
        raise
