"""
Availability repository interface définissant le contrat pour l'accès aux données availabilitys.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Availability


class AvailabilityRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository availabilitys.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les availability, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les availability filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, availability_id: int) -> Optional[Availability]:
        """
        Obtenir un availability par ID.

        Args:
            availability_id (int): L'ID du availability

        Returns:
            Optional[Availability]: Le availability si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Availability:
        """
        Créer un nouveau availability.

        Args:
            **kwargs: Données du availability

        Returns:
            Availability: Le availability créé
        """
        pass

    @abstractmethod
    def update(self, availability: Availability, **kwargs) -> Availability:
        """
        Mettre à jour un availability existant.

        Args:
            availability (Availability): Le availability à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Availability: Le availability mis à jour
        """
        pass

    @abstractmethod
    def delete(self, availability: Availability) -> bool:
        """
        Supprimer un availability.

        Args:
            availability (Availability): Le availability à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, availability_id: int) -> bool:
        """
        Vérifier si un availability existe par ID.

        Args:
            availability_id (int): L'ID du availability

        Returns:
            bool: True si le availability existe, False sinon
        """
        pass