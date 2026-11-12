"""
ContributionTask service layer pour les opérations de logique métier.
"""

from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.devstreet_hub.models import ContributionTask
from app.devstreet_hub.repositories.contributiontask_repository import (
    ContributionTaskRepository,
)


class ContributionTaskService:
    """
    Classe de service pour la logique métier liée aux contribution_tasks.
    """

    def __init__(self):
        self.contributiontask_repository = ContributionTaskRepository()

    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les contribution_tasks, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les contribution_tasks filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.contributiontask_repository.get_all(
            search=search, ordering=ordering
        )

    def get_by_id(self, contribution_task_id: int) -> Optional[ContributionTask]:
        """
        Obtenir un contribution_task par ID.

        Args:
            contribution_task_id (int): L'ID du contribution_task

        Returns:
            Optional[ContributionTask]: Le contribution_task si trouvé, None sinon
        """
        return self.contributiontask_repository.get_by_id(contribution_task_id)

    def create(self, contribution_task_data: Dict[str, Any]) -> ContributionTask:
        """
        Créer un nouveau contribution_task avec validation.

        Args:
            contribution_task_data (Dict[str, Any]): Données du contribution_task

        Returns:
            ContributionTask: Le contribution_task créé

        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(contribution_task_data)

        return self.contributiontask_repository.create(**contribution_task_data)

    def update(
        self,
        contribution_task_id: int,
        contribution_task_data: Dict[str, Any],
        partial: bool = False,
    ) -> Optional[ContributionTask]:
        """
        Mettre à jour un contribution_task existant.

        Args:
            contribution_task_id (int): L'ID du contribution_task
            contribution_task_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle

        Returns:
            Optional[ContributionTask]: Le contribution_task mis à jour si trouvé, None sinon

        Raises:
            ValidationError: Si la validation échoue
        """
        contribution_task = self.contributiontask_repository.get_by_id(
            contribution_task_id
        )
        if not contribution_task:
            return None

        # Validation des données
        if not partial:
            self.validate_data(contribution_task_data)

        return self.contributiontask_repository.update(
            contribution_task, **contribution_task_data
        )

    def delete(self, contribution_task_id: int) -> bool:
        """
        Supprimer un contribution_task.

        Args:
            contribution_task_id (int): L'ID du contribution_task

        Returns:
            bool: True si supprimé avec succès, False si contribution_task non trouvé
        """
        contribution_task = self.contributiontask_repository.get_by_id(
            contribution_task_id
        )
        if not contribution_task:
            return False

        return self.contributiontask_repository.delete(contribution_task)

    def validate_data(self, contribution_task_data: Dict[str, Any]):
        """
        Valider les données du contribution_task.

        Args:
            contribution_task_data (Dict[str, Any]): Données du contribution_task à valider

        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if "status" in contribution_task_data:
            _valid_status = ["draft", "open", "closed"]
            if contribution_task_data["status"] not in _valid_status:
                raise ValidationError("Valeur invalide pour le champ status")
        # Ajoutez d'autres validations selon vos besoins
