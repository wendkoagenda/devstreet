"""
ProfilHistory repository interface définissant le contrat pour l'accès aux données profilhistorys.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import ProfilHistory


class ProfilHistoryRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository profilhistorys.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profil_history, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les profil_history filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, profil_history_id: int) -> Optional[ProfilHistory]:
        """
        Obtenir un profil_history par ID.

        Args:
            profil_history_id (int): L'ID du profil_history

        Returns:
            Optional[ProfilHistory]: Le profil_history si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> ProfilHistory:
        """
        Créer un nouveau profil_history.

        Args:
            **kwargs: Données du profil_history

        Returns:
            ProfilHistory: Le profil_history créé
        """
        pass

    @abstractmethod
    def update(self, profil_history: ProfilHistory, **kwargs) -> ProfilHistory:
        """
        Mettre à jour un profil_history existant.

        Args:
            profil_history (ProfilHistory): Le profil_history à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ProfilHistory: Le profil_history mis à jour
        """
        pass

    @abstractmethod
    def delete(self, profil_history: ProfilHistory) -> bool:
        """
        Supprimer un profil_history.

        Args:
            profil_history (ProfilHistory): Le profil_history à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, profil_history_id: int) -> bool:
        """
        Vérifier si un profil_history existe par ID.

        Args:
            profil_history_id (int): L'ID du profil_history

        Returns:
            bool: True si le profil_history existe, False sinon
        """
        pass