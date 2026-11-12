"""
Offer repository interface définissant le contrat pour l'accès aux données offers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Offer


class OfferRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository offers.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les offer, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les offer filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, offer_id: int) -> Optional[Offer]:
        """
        Obtenir un offer par ID.

        Args:
            offer_id (int): L'ID du offer

        Returns:
            Optional[Offer]: Le offer si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Offer:
        """
        Créer un nouveau offer.

        Args:
            **kwargs: Données du offer

        Returns:
            Offer: Le offer créé
        """
        pass

    @abstractmethod
    def update(self, offer: Offer, **kwargs) -> Offer:
        """
        Mettre à jour un offer existant.

        Args:
            offer (Offer): Le offer à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Offer: Le offer mis à jour
        """
        pass

    @abstractmethod
    def delete(self, offer: Offer) -> bool:
        """
        Supprimer un offer.

        Args:
            offer (Offer): Le offer à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, offer_id: int) -> bool:
        """
        Vérifier si un offer existe par ID.

        Args:
            offer_id (int): L'ID du offer

        Returns:
            bool: True si le offer existe, False sinon
        """
        pass