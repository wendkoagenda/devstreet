"""
Swipe repository interface définissant le contrat pour l'accès aux données swipes.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Swipe


class SwipeRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository swipes.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les swipe, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les swipe filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, swipe_id: int) -> Optional[Swipe]:
        """
        Obtenir un swipe par ID.

        Args:
            swipe_id (int): L'ID du swipe

        Returns:
            Optional[Swipe]: Le swipe si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Swipe:
        """
        Créer un nouveau swipe.

        Args:
            **kwargs: Données du swipe

        Returns:
            Swipe: Le swipe créé
        """
        pass

    @abstractmethod
    def update(self, swipe: Swipe, **kwargs) -> Swipe:
        """
        Mettre à jour un swipe existant.

        Args:
            swipe (Swipe): Le swipe à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Swipe: Le swipe mis à jour
        """
        pass

    @abstractmethod
    def delete(self, swipe: Swipe) -> bool:
        """
        Supprimer un swipe.

        Args:
            swipe (Swipe): Le swipe à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, swipe_id: int) -> bool:
        """
        Vérifier si un swipe existe par ID.

        Args:
            swipe_id (int): L'ID du swipe

        Returns:
            bool: True si le swipe existe, False sinon
        """
        pass