"""
ParticipationEspace repository interface définissant le contrat pour l'accès aux données participationespaces.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import ParticipationEspace


class ParticipationEspaceRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository participationespaces.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les participation_espace, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les participation_espace filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, participation_espace_id: int) -> Optional[ParticipationEspace]:
        """
        Obtenir un participation_espace par ID.

        Args:
            participation_espace_id (int): L'ID du participation_espace

        Returns:
            Optional[ParticipationEspace]: Le participation_espace si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> ParticipationEspace:
        """
        Créer un nouveau participation_espace.

        Args:
            **kwargs: Données du participation_espace

        Returns:
            ParticipationEspace: Le participation_espace créé
        """
        pass

    @abstractmethod
    def update(self, participation_espace: ParticipationEspace, **kwargs) -> ParticipationEspace:
        """
        Mettre à jour un participation_espace existant.

        Args:
            participation_espace (ParticipationEspace): Le participation_espace à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ParticipationEspace: Le participation_espace mis à jour
        """
        pass

    @abstractmethod
    def delete(self, participation_espace: ParticipationEspace) -> bool:
        """
        Supprimer un participation_espace.

        Args:
            participation_espace (ParticipationEspace): Le participation_espace à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, participation_espace_id: int) -> bool:
        """
        Vérifier si un participation_espace existe par ID.

        Args:
            participation_espace_id (int): L'ID du participation_espace

        Returns:
            bool: True si le participation_espace existe, False sinon
        """
        pass