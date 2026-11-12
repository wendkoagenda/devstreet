"""
Profil repository interface définissant le contrat pour l'accès aux données profils.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Profil


class ProfilRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository profils.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profil, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les profil filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, profil_id: int) -> Optional[Profil]:
        """
        Obtenir un profil par ID.

        Args:
            profil_id (int): L'ID du profil

        Returns:
            Optional[Profil]: Le profil si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Profil:
        """
        Créer un nouveau profil.

        Args:
            **kwargs: Données du profil

        Returns:
            Profil: Le profil créé
        """
        pass

    @abstractmethod
    def update(self, profil: Profil, **kwargs) -> Profil:
        """
        Mettre à jour un profil existant.

        Args:
            profil (Profil): Le profil à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Profil: Le profil mis à jour
        """
        pass

    @abstractmethod
    def delete(self, profil: Profil) -> bool:
        """
        Supprimer un profil.

        Args:
            profil (Profil): Le profil à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, profil_id: int) -> bool:
        """
        Vérifier si un profil existe par ID.

        Args:
            profil_id (int): L'ID du profil

        Returns:
            bool: True si le profil existe, False sinon
        """
        pass