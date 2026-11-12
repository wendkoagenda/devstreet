"""
Technology service layer pour les opérations de logique métier.
"""

from typing import Optional, Dict, Any
from django.db.models import QuerySet
from app.devstreet_hub.models import Technology
from app.devstreet_hub.repositories.technology_repository import TechnologyRepository


class TechnologyService:
    """
    Classe de service pour la logique métier liée aux technologys.
    """

    def __init__(self):
        self.technology_repository = TechnologyRepository()

    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les technologys, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les technologys filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.technology_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, technology_id: int) -> Optional[Technology]:
        """
        Obtenir un technology par ID.

        Args:
            technology_id (int): L'ID du technology

        Returns:
            Optional[Technology]: Le technology si trouvé, None sinon
        """
        return self.technology_repository.get_by_id(technology_id)

    def create(self, technology_data: Dict[str, Any]) -> Technology:
        """
        Créer un nouveau technology avec validation.

        Args:
            technology_data (Dict[str, Any]): Données du technology

        Returns:
            Technology: Le technology créé

        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(technology_data)

        return self.technology_repository.create(**technology_data)

    def update(
        self, technology_id: int, technology_data: Dict[str, Any], partial: bool = False
    ) -> Optional[Technology]:
        """
        Mettre à jour un technology existant.

        Args:
            technology_id (int): L'ID du technology
            technology_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle

        Returns:
            Optional[Technology]: Le technology mis à jour si trouvé, None sinon

        Raises:
            ValidationError: Si la validation échoue
        """
        technology = self.technology_repository.get_by_id(technology_id)
        if not technology:
            return None

        # Validation des données
        if not partial:
            self.validate_data(technology_data)

        return self.technology_repository.update(technology, **technology_data)

    def delete(self, technology_id: int) -> bool:
        """
        Supprimer un technology.

        Args:
            technology_id (int): L'ID du technology

        Returns:
            bool: True si supprimé avec succès, False si technology non trouvé
        """
        technology = self.technology_repository.get_by_id(technology_id)
        if not technology:
            return False

        return self.technology_repository.delete(technology)

    def validate_data(self, technology_data: Dict[str, Any]):
        """
        Valider les données du technology.

        Args:
            technology_data (Dict[str, Any]): Données du technology à valider

        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins
