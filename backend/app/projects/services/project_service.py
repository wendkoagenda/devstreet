"""
Project service layer pour les opérations de logique métier.
"""

from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.projects.models import Project
from app.projects.repositories.project_repository import ProjectRepository


class ProjectService:
    """
    Classe de service pour la logique métier liée aux projects.
    """

    def __init__(self):
        self.project_repository = ProjectRepository()

    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les projects, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les projects filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.project_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """
        Obtenir un project par ID.

        Args:
            project_id (int): L'ID du project

        Returns:
            Optional[Project]: Le project si trouvé, None sinon
        """
        return self.project_repository.get_by_id(project_id)

    def create(self, project_data: Dict[str, Any]) -> Project:
        """
        Créer un nouveau project avec validation.

        Args:
            project_data (Dict[str, Any]): Données du project

        Returns:
            Project: Le project créé

        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(project_data)

        return self.project_repository.create(**project_data)

    def update(
        self, project_id: int, project_data: Dict[str, Any], partial: bool = False
    ) -> Optional[Project]:
        """
        Mettre à jour un project existant.

        Args:
            project_id (int): L'ID du project
            project_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle

        Returns:
            Optional[Project]: Le project mis à jour si trouvé, None sinon

        Raises:
            ValidationError: Si la validation échoue
        """
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None

        # Validation des données
        if not partial:
            self.validate_data(project_data)

        return self.project_repository.update(project, **project_data)

    def delete(self, project_id: int) -> bool:
        """
        Supprimer un project.

        Args:
            project_id (int): L'ID du project

        Returns:
            bool: True si supprimé avec succès, False si project non trouvé
        """
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return False

        return self.project_repository.delete(project)

    def validate_data(self, project_data: Dict[str, Any]):
        """
        Valider les données du project.

        Args:
            project_data (Dict[str, Any]): Données du project à valider

        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if "status" in project_data:
            _valid_status = ["draft", "published", "archived"]
            if project_data["status"] not in _valid_status:
                raise ValidationError("Valeur invalide pour le champ status")
        # Ajoutez d'autres validations selon vos besoins
