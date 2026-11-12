"""
SuiviUtilisateur repository interface définissant le contrat pour l'accès aux données suiviutilisateurs.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import SuiviUtilisateur


class SuiviUtilisateurRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository suiviutilisateurs.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les suivi_utilisateur, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les suivi_utilisateur filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, suivi_utilisateur_id: int) -> Optional[SuiviUtilisateur]:
        """
        Obtenir un suivi_utilisateur par ID.

        Args:
            suivi_utilisateur_id (int): L'ID du suivi_utilisateur

        Returns:
            Optional[SuiviUtilisateur]: Le suivi_utilisateur si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> SuiviUtilisateur:
        """
        Créer un nouveau suivi_utilisateur.

        Args:
            **kwargs: Données du suivi_utilisateur

        Returns:
            SuiviUtilisateur: Le suivi_utilisateur créé
        """
        pass

    @abstractmethod
    def update(self, suivi_utilisateur: SuiviUtilisateur, **kwargs) -> SuiviUtilisateur:
        """
        Mettre à jour un suivi_utilisateur existant.

        Args:
            suivi_utilisateur (SuiviUtilisateur): Le suivi_utilisateur à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            SuiviUtilisateur: Le suivi_utilisateur mis à jour
        """
        pass

    @abstractmethod
    def delete(self, suivi_utilisateur: SuiviUtilisateur) -> bool:
        """
        Supprimer un suivi_utilisateur.

        Args:
            suivi_utilisateur (SuiviUtilisateur): Le suivi_utilisateur à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, suivi_utilisateur_id: int) -> bool:
        """
        Vérifier si un suivi_utilisateur existe par ID.

        Args:
            suivi_utilisateur_id (int): L'ID du suivi_utilisateur

        Returns:
            bool: True si le suivi_utilisateur existe, False sinon
        """
        pass