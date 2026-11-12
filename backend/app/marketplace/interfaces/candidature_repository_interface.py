"""
Candidature repository interface définissant le contrat pour l'accès aux données candidatures.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Candidature


class CandidatureRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository candidatures.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les candidature, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les candidature filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, candidature_id: int) -> Optional[Candidature]:
        """
        Obtenir un candidature par ID.

        Args:
            candidature_id (int): L'ID du candidature

        Returns:
            Optional[Candidature]: Le candidature si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Candidature:
        """
        Créer un nouveau candidature.

        Args:
            **kwargs: Données du candidature

        Returns:
            Candidature: Le candidature créé
        """
        pass

    @abstractmethod
    def update(self, candidature: Candidature, **kwargs) -> Candidature:
        """
        Mettre à jour un candidature existant.

        Args:
            candidature (Candidature): Le candidature à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Candidature: Le candidature mis à jour
        """
        pass

    @abstractmethod
    def delete(self, candidature: Candidature) -> bool:
        """
        Supprimer un candidature.

        Args:
            candidature (Candidature): Le candidature à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, candidature_id: int) -> bool:
        """
        Vérifier si un candidature existe par ID.

        Args:
            candidature_id (int): L'ID du candidature

        Returns:
            bool: True si le candidature existe, False sinon
        """
        pass