"""
Review repository interface définissant le contrat pour l'accès aux données reviews.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Review


class ReviewRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository reviews.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les review, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les review filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, review_id: int) -> Optional[Review]:
        """
        Obtenir un review par ID.

        Args:
            review_id (int): L'ID du review

        Returns:
            Optional[Review]: Le review si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Review:
        """
        Créer un nouveau review.

        Args:
            **kwargs: Données du review

        Returns:
            Review: Le review créé
        """
        pass

    @abstractmethod
    def update(self, review: Review, **kwargs) -> Review:
        """
        Mettre à jour un review existant.

        Args:
            review (Review): Le review à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Review: Le review mis à jour
        """
        pass

    @abstractmethod
    def delete(self, review: Review) -> bool:
        """
        Supprimer un review.

        Args:
            review (Review): Le review à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, review_id: int) -> bool:
        """
        Vérifier si un review existe par ID.

        Args:
            review_id (int): L'ID du review

        Returns:
            bool: True si le review existe, False sinon
        """
        pass