"""
AvisChoix repository interface définissant le contrat pour l'accès aux données avischoixs.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import AvisChoix


class AvisChoixRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository avischoixs.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les avis_choix, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les avis_choix filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, avis_choix_id: int) -> Optional[AvisChoix]:
        """
        Obtenir un avis_choix par ID.

        Args:
            avis_choix_id (int): L'ID du avis_choix

        Returns:
            Optional[AvisChoix]: Le avis_choix si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> AvisChoix:
        """
        Créer un nouveau avis_choix.

        Args:
            **kwargs: Données du avis_choix

        Returns:
            AvisChoix: Le avis_choix créé
        """
        pass

    @abstractmethod
    def update(self, avis_choix: AvisChoix, **kwargs) -> AvisChoix:
        """
        Mettre à jour un avis_choix existant.

        Args:
            avis_choix (AvisChoix): Le avis_choix à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            AvisChoix: Le avis_choix mis à jour
        """
        pass

    @abstractmethod
    def delete(self, avis_choix: AvisChoix) -> bool:
        """
        Supprimer un avis_choix.

        Args:
            avis_choix (AvisChoix): Le avis_choix à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, avis_choix_id: int) -> bool:
        """
        Vérifier si un avis_choix existe par ID.

        Args:
            avis_choix_id (int): L'ID du avis_choix

        Returns:
            bool: True si le avis_choix existe, False sinon
        """
        pass