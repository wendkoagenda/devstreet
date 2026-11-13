"""
Espace repository interface définissant le contrat pour l'accès aux données espaces.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import Espace


class EspaceRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository espaces.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les espace, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les espace filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, espace_id: int) -> Optional[Espace]:
        """
        Obtenir un espace par ID.

        Args:
            espace_id (int): L'ID du espace

        Returns:
            Optional[Espace]: Le espace si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Espace:
        """
        Créer un nouveau espace.

        Args:
            **kwargs: Données du espace

        Returns:
            Espace: Le espace créé
        """
        pass

    @abstractmethod
    def update(self, espace: Espace, **kwargs) -> Espace:
        """
        Mettre à jour un espace existant.

        Args:
            espace (Espace): Le espace à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Espace: Le espace mis à jour
        """
        pass

    @abstractmethod
    def delete(self, espace: Espace) -> bool:
        """
        Supprimer un espace.

        Args:
            espace (Espace): Le espace à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, espace_id: int) -> bool:
        """
        Vérifier si un espace existe par ID.

        Args:
            espace_id (int): L'ID du espace

        Returns:
            bool: True si le espace existe, False sinon
        """
        pass