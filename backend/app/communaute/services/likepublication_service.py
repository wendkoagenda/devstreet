"""
LikePublication service layer.
"""
from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from app.communaute.models import LikePublication, Publication
from app.communaute.repositories.likepublication_repository import LikePublicationRepository

User = get_user_model()


class LikePublicationService:
    """Service métier des likes de publication."""

    def __init__(self):
        self.like_publication_repository = LikePublicationRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        return self.like_publication_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, like_publication_id: int) -> Optional[LikePublication]:
        return self.like_publication_repository.get_by_id(like_publication_id)

    def toggle(self, *, publication_id: int, membre: User) -> Dict[str, Any]:
        """
        Ajoute ou retire le like du membre sur la publication.
        Retourne l'état courant et le compteur.
        """
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

        existing = LikePublication.objects.filter(
            publication_id=publication_id, membre_id=membre.id
        ).first()
        if existing:
            existing.delete()
            liked = False
        else:
            LikePublication.objects.create(
                publication=publication,
                membre=membre,
                created_by=membre.id,
                updated_by=membre.id,
            )
            liked = True

        likes_count = LikePublication.objects.filter(publication_id=publication_id).count()
        return {'liked': liked, 'likes_count': likes_count, 'publication_id': publication_id}

    def create(self, like_publication_data: Dict[str, Any]) -> LikePublication:
        return self.like_publication_repository.create(**like_publication_data)

    def update(
        self, like_publication_id: int, like_publication_data: Dict[str, Any], partial: bool = False
    ) -> Optional[LikePublication]:
        like_publication = self.like_publication_repository.get_by_id(like_publication_id)
        if not like_publication:
            return None
        return self.like_publication_repository.update(like_publication, **like_publication_data)

    def delete(self, like_publication_id: int) -> bool:
        like_publication = self.like_publication_repository.get_by_id(like_publication_id)
        if not like_publication:
            return False
        return self.like_publication_repository.delete(like_publication)
