"""
Experience repository interface définissant le contrat pour l'accès aux données experiences.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Experience


class ExperienceRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository experiences.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les experience, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les experience filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, experience_id: int) -> Optional[Experience]:
        """
        Obtenir un experience par ID.

        Args:
            experience_id (int): L'ID du experience

        Returns:
            Optional[Experience]: Le experience si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Experience:
        """
        Créer un nouveau experience.

        Args:
            **kwargs: Données du experience

        Returns:
            Experience: Le experience créé
        """
        pass

    @abstractmethod
    def update(self, experience: Experience, **kwargs) -> Experience:
        """
        Mettre à jour un experience existant.

        Args:
            experience (Experience): Le experience à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Experience: Le experience mis à jour
        """
        pass

    @abstractmethod
    def delete(self, experience: Experience) -> bool:
        """
        Supprimer un experience.

        Args:
            experience (Experience): Le experience à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, experience_id: int) -> bool:
        """
        Vérifier si un experience existe par ID.

        Args:
            experience_id (int): L'ID du experience

        Returns:
            bool: True si le experience existe, False sinon
        """
        pass