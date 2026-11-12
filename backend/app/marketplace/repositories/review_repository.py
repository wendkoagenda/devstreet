"""
Review repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Review
from app.marketplace.interfaces.review_repository_interface import ReviewRepositoryInterface


class ReviewRepository(ReviewRepositoryInterface):
    """
    Implémentation concrète des opérations du repository reviews.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('comment',)
    ORDERING_FIELDS = ('id', 'rating', 'comment', 'is_public', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les review, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les review filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Review.objects.all()
        if search:
            condition = Q()
            for field_name in self.SEARCH_FIELDS:
                condition |= Q(**{f'{field_name}__icontains': search})
            queryset = queryset.filter(condition)
        if ordering:
            if ordering.lstrip('-') not in self.ORDERING_FIELDS:
                raise ValueError(f'Tri non autorisé : {ordering}')
            return queryset.order_by(ordering, 'id')
        return queryset.order_by('id')

    def get_by_id(self, review_id: int) -> Optional[Review]:
        """
        Obtenir un review par ID.

        Args:
            review_id (int): L'ID du review

        Returns:
            Optional[Review]: Le review si trouvé, None sinon
        """
        return Review.objects.filter(id=review_id).first()

    def create(self, **kwargs) -> Review:
        """
        Créer un nouveau review.

        Args:
            **kwargs: Données du review

        Returns:
            Review: Le review créé
        """
        return Review.objects.create(**kwargs)

    def update(self, review: Review, **kwargs) -> Review:
        """
        Mettre à jour un review existant.

        Args:
            review (Review): Le review à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Review: Le review mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(review, field):
                setattr(review, field, value)

        review.save()
        return review

    def delete(self, review: Review) -> bool:
        """
        Supprimer un review.

        Args:
            review (Review): Le review à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        review.delete()
        return True

    def exists_by_id(self, review_id: int) -> bool:
        """
        Vérifier si un review existe par ID.

        Args:
            review_id (int): L'ID du review

        Returns:
            bool: True si le review existe, False sinon
        """
        return Review.objects.filter(id=review_id).exists()