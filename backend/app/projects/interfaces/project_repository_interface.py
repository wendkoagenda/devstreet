"""
Project repository interface définissant le contrat pour l'accès aux données projects.
"""

from abc import ABC, abstractmethod
from typing import Optional
from django.db.models import QuerySet
from app.projects.models import Project


class ProjectRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository projects.
    """

    @abstractmethod
    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les project, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les project filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """
        Obtenir un project par ID.

        Args:
            project_id (int): L'ID du project

        Returns:
            Optional[Project]: Le project si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Project:
        """
        Créer un nouveau project.

        Args:
            **kwargs: Données du project

        Returns:
            Project: Le project créé
        """
        pass

    @abstractmethod
    def update(self, project: Project, **kwargs) -> Project:
        """
        Mettre à jour un project existant.

        Args:
            project (Project): Le project à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Project: Le project mis à jour
        """
        pass

    @abstractmethod
    def delete(self, project: Project) -> bool:
        """
        Supprimer un project.

        Args:
            project (Project): Le project à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, project_id: int) -> bool:
        """
        Vérifier si un project existe par ID.

        Args:
            project_id (int): L'ID du project

        Returns:
            bool: True si le project existe, False sinon
        """
        pass
