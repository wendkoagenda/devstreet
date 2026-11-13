"""Service des favoris (bookmarks) de publication."""
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from app.communaute.models import FavoriPublication, Publication

User = get_user_model()


class FavoriPublicationService:
    """Ajoute ou retire un favori sur une publication."""

    def toggle(self, *, publication_id: int, membre: User) -> Dict[str, Any]:
        publication = (
            Publication.objects.filter(id=publication_id)
            .select_related('espace')
            .first()
        )
        if publication is None:
            raise ValidationError('Publication introuvable.')
        if publication.espace_id:
            from app.communaute.services.espace_service import EspaceService

            EspaceService().assert_can_interact(
                espace=publication.espace, acteur=membre
            )

        existing = FavoriPublication.objects.filter(
            publication_id=publication_id, membre_id=membre.id
        ).first()
        if existing:
            existing.delete()
            saved = False
        else:
            FavoriPublication.objects.create(
                publication=publication,
                membre=membre,
                created_by=membre.id,
                updated_by=membre.id,
            )
            saved = True

        return {
            'saved': saved,
            'publication_id': publication_id,
        }
