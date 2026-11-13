"""
LikeCommentaire service layer.
"""
from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from app.communaute.models import LikeCommentaire, Commentaire
from app.communaute.repositories.likecommentaire_repository import LikeCommentaireRepository

User = get_user_model()


class LikeCommentaireService:
    """Service métier des likes de commentaire."""

    def __init__(self):
        self.like_commentaire_repository = LikeCommentaireRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        return self.like_commentaire_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, like_commentaire_id: int) -> Optional[LikeCommentaire]:
        return self.like_commentaire_repository.get_by_id(like_commentaire_id)

    def toggle(self, *, commentaire_id: int, membre: User) -> Dict[str, Any]:
        """Ajoute ou retire le like du membre sur le commentaire."""
        commentaire = (
            Commentaire.objects.filter(id=commentaire_id)
            .select_related('publication', 'publication__espace')
            .first()
        )
        if commentaire is None:
            raise ValidationError('Commentaire introuvable.')
        if commentaire.publication.espace_id:
            from app.communaute.services.espace_service import EspaceService

            EspaceService().assert_can_interact(
                espace=commentaire.publication.espace, acteur=membre
            )

        existing = LikeCommentaire.objects.filter(
            commentaire_id=commentaire_id, membre_id=membre.id
        ).first()
        if existing:
            existing.delete()
            liked = False
        else:
            LikeCommentaire.objects.create(
                commentaire=commentaire,
                membre=membre,
                created_by=membre.id,
                updated_by=membre.id,
            )
            liked = True

        likes_count = LikeCommentaire.objects.filter(commentaire_id=commentaire_id).count()
        return {
            'liked': liked,
            'likes_count': likes_count,
            'commentaire_id': commentaire_id,
        }

    def create(self, like_commentaire_data: Dict[str, Any]) -> LikeCommentaire:
        return self.like_commentaire_repository.create(**like_commentaire_data)

    def update(
        self, like_commentaire_id: int, like_commentaire_data: Dict[str, Any], partial: bool = False
    ) -> Optional[LikeCommentaire]:
        like_commentaire = self.like_commentaire_repository.get_by_id(like_commentaire_id)
        if not like_commentaire:
            return None
        return self.like_commentaire_repository.update(like_commentaire, **like_commentaire_data)

    def delete(self, like_commentaire_id: int) -> bool:
        like_commentaire = self.like_commentaire_repository.get_by_id(like_commentaire_id)
        if not like_commentaire:
            return False
        return self.like_commentaire_repository.delete(like_commentaire)
