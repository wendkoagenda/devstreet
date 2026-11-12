"""
Prestation repository interface définissant le contrat pour l'accès aux données prestations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Prestation


class PrestationRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository prestations.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les prestation, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les prestation filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, prestation_id: int) -> Optional[Prestation]:
        """
        Obtenir un prestation par ID.

        Args:
            prestation_id (int): L'ID du prestation

        Returns:
            Optional[Prestation]: Le prestation si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Prestation:
        """
        Créer un nouveau prestation.

        Args:
            **kwargs: Données du prestation

        Returns:
            Prestation: Le prestation créé
        """
        pass

    @abstractmethod
    def update(self, prestation: Prestation, **kwargs) -> Prestation:
        """
        Mettre à jour un prestation existant.

        Args:
            prestation (Prestation): Le prestation à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Prestation: Le prestation mis à jour
        """
        pass

    @abstractmethod
    def delete(self, prestation: Prestation) -> bool:
        """
        Supprimer un prestation.

        Args:
            prestation (Prestation): Le prestation à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, prestation_id: int) -> bool:
        """
        Vérifier si un prestation existe par ID.

        Args:
            prestation_id (int): L'ID du prestation

        Returns:
            bool: True si le prestation existe, False sinon
        """
        pass