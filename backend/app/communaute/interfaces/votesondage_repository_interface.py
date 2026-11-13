"""
VoteSondage repository interface définissant le contrat pour l'accès aux données votesondages.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import VoteSondage


class VoteSondageRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository votesondages.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les vote_sondage, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les vote_sondage filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, vote_sondage_id: int) -> Optional[VoteSondage]:
        """
        Obtenir un vote_sondage par ID.

        Args:
            vote_sondage_id (int): L'ID du vote_sondage

        Returns:
            Optional[VoteSondage]: Le vote_sondage si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> VoteSondage:
        """
        Créer un nouveau vote_sondage.

        Args:
            **kwargs: Données du vote_sondage

        Returns:
            VoteSondage: Le vote_sondage créé
        """
        pass

    @abstractmethod
    def update(self, vote_sondage: VoteSondage, **kwargs) -> VoteSondage:
        """
        Mettre à jour un vote_sondage existant.

        Args:
            vote_sondage (VoteSondage): Le vote_sondage à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            VoteSondage: Le vote_sondage mis à jour
        """
        pass

    @abstractmethod
    def delete(self, vote_sondage: VoteSondage) -> bool:
        """
        Supprimer un vote_sondage.

        Args:
            vote_sondage (VoteSondage): Le vote_sondage à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, vote_sondage_id: int) -> bool:
        """
        Vérifier si un vote_sondage existe par ID.

        Args:
            vote_sondage_id (int): L'ID du vote_sondage

        Returns:
            bool: True si le vote_sondage existe, False sinon
        """
        pass