"""
Dragon repository interface définissant le contrat pour l'accès aux données dragons.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.metier.models import Dragon


class DragonRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository dragons.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les dragon, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les dragon filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, dragon_id: int) -> Optional[Dragon]:
        """
        Obtenir un dragon par ID.

        Args:
            dragon_id (int): L'ID du dragon

        Returns:
            Optional[Dragon]: Le dragon si trouvé, None sinon
        """
        pass

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Optional[Dragon]:
        """
        Obtenir un dragon par UUID.

        Args:
            uuid (str): L'UUID du dragon

        Returns:
            Optional[Dragon]: Le dragon si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Dragon:
        """
        Créer un nouveau dragon.

        Args:
            **kwargs: Données du dragon

        Returns:
            Dragon: Le dragon créé
        """
        pass

    @abstractmethod
    def update(self, dragon: Dragon, **kwargs) -> Dragon:
        """
        Mettre à jour un dragon existant.

        Args:
            dragon (Dragon): Le dragon à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Dragon: Le dragon mis à jour
        """
        pass

    @abstractmethod
    def delete(self, dragon: Dragon) -> bool:
        """
        Supprimer un dragon.

        Args:
            dragon (Dragon): Le dragon à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, dragon_id: int) -> bool:
        """
        Vérifier si un dragon existe par ID.

        Args:
            dragon_id (int): L'ID du dragon

        Returns:
            bool: True si le dragon existe, False sinon
        """
        pass