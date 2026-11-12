"""
Skill repository interface définissant le contrat pour l'accès aux données skills.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Skill


class SkillRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository skills.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les skill, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les skill filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        """
        Obtenir un skill par ID.

        Args:
            skill_id (int): L'ID du skill

        Returns:
            Optional[Skill]: Le skill si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Skill:
        """
        Créer un nouveau skill.

        Args:
            **kwargs: Données du skill

        Returns:
            Skill: Le skill créé
        """
        pass

    @abstractmethod
    def update(self, skill: Skill, **kwargs) -> Skill:
        """
        Mettre à jour un skill existant.

        Args:
            skill (Skill): Le skill à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Skill: Le skill mis à jour
        """
        pass

    @abstractmethod
    def delete(self, skill: Skill) -> bool:
        """
        Supprimer un skill.

        Args:
            skill (Skill): Le skill à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, skill_id: int) -> bool:
        """
        Vérifier si un skill existe par ID.

        Args:
            skill_id (int): L'ID du skill

        Returns:
            bool: True si le skill existe, False sinon
        """
        pass