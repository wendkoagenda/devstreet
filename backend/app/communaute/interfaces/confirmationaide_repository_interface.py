"""
ConfirmationAide repository interface définissant le contrat pour l'accès aux données confirmationaides.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import ConfirmationAide


class ConfirmationAideRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository confirmationaides.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les confirmation_aide, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les confirmation_aide filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, confirmation_aide_id: int) -> Optional[ConfirmationAide]:
        """
        Obtenir un confirmation_aide par ID.

        Args:
            confirmation_aide_id (int): L'ID du confirmation_aide

        Returns:
            Optional[ConfirmationAide]: Le confirmation_aide si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> ConfirmationAide:
        """
        Créer un nouveau confirmation_aide.

        Args:
            **kwargs: Données du confirmation_aide

        Returns:
            ConfirmationAide: Le confirmation_aide créé
        """
        pass

    @abstractmethod
    def update(self, confirmation_aide: ConfirmationAide, **kwargs) -> ConfirmationAide:
        """
        Mettre à jour un confirmation_aide existant.

        Args:
            confirmation_aide (ConfirmationAide): Le confirmation_aide à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ConfirmationAide: Le confirmation_aide mis à jour
        """
        pass

    @abstractmethod
    def delete(self, confirmation_aide: ConfirmationAide) -> bool:
        """
        Supprimer un confirmation_aide.

        Args:
            confirmation_aide (ConfirmationAide): Le confirmation_aide à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, confirmation_aide_id: int) -> bool:
        """
        Vérifier si un confirmation_aide existe par ID.

        Args:
            confirmation_aide_id (int): L'ID du confirmation_aide

        Returns:
            bool: True si le confirmation_aide existe, False sinon
        """
        pass