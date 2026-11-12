"""
Technology repository interface définissant le contrat pour l'accès aux données technologys.
"""

from abc import ABC, abstractmethod
from typing import Optional
from django.db.models import QuerySet
from app.projects.models import Technology


class TechnologyRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository technologys.
    """

    @abstractmethod
    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les technology, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les technology filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, technology_id: int) -> Optional[Technology]:
        """
        Obtenir un technology par ID.

        Args:
            technology_id (int): L'ID du technology

        Returns:
            Optional[Technology]: Le technology si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Technology:
        """
        Créer un nouveau technology.

        Args:
            **kwargs: Données du technology

        Returns:
            Technology: Le technology créé
        """
        pass

    @abstractmethod
    def update(self, technology: Technology, **kwargs) -> Technology:
        """
        Mettre à jour un technology existant.

        Args:
            technology (Technology): Le technology à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Technology: Le technology mis à jour
        """
        pass

    @abstractmethod
    def delete(self, technology: Technology) -> bool:
        """
        Supprimer un technology.

        Args:
            technology (Technology): Le technology à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, technology_id: int) -> bool:
        """
        Vérifier si un technology existe par ID.

        Args:
            technology_id (int): L'ID du technology

        Returns:
            bool: True si le technology existe, False sinon
        """
        pass
