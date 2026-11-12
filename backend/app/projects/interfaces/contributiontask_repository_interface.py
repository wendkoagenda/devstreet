"""
ContributionTask repository interface définissant le contrat pour l'accès aux données contributiontasks.
"""

from abc import ABC, abstractmethod
from typing import Optional
from django.db.models import QuerySet
from app.projects.models import ContributionTask


class ContributionTaskRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository contributiontasks.
    """

    @abstractmethod
    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les contribution_task, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les contribution_task filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, contribution_task_id: int) -> Optional[ContributionTask]:
        """
        Obtenir un contribution_task par ID.

        Args:
            contribution_task_id (int): L'ID du contribution_task

        Returns:
            Optional[ContributionTask]: Le contribution_task si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> ContributionTask:
        """
        Créer un nouveau contribution_task.

        Args:
            **kwargs: Données du contribution_task

        Returns:
            ContributionTask: Le contribution_task créé
        """
        pass

    @abstractmethod
    def update(self, contribution_task: ContributionTask, **kwargs) -> ContributionTask:
        """
        Mettre à jour un contribution_task existant.

        Args:
            contribution_task (ContributionTask): Le contribution_task à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ContributionTask: Le contribution_task mis à jour
        """
        pass

    @abstractmethod
    def delete(self, contribution_task: ContributionTask) -> bool:
        """
        Supprimer un contribution_task.

        Args:
            contribution_task (ContributionTask): Le contribution_task à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, contribution_task_id: int) -> bool:
        """
        Vérifier si un contribution_task existe par ID.

        Args:
            contribution_task_id (int): L'ID du contribution_task

        Returns:
            bool: True si le contribution_task existe, False sinon
        """
        pass
