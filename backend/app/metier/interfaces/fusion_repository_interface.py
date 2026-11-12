"""
Fusion repository interface définissant le contrat pour l'accès aux données fusions.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.metier.models import Fusion


class FusionRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository fusions.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les fusion, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les fusion filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, fusion_id: int) -> Optional[Fusion]:
        """
        Obtenir un fusion par ID.

        Args:
            fusion_id (int): L'ID du fusion

        Returns:
            Optional[Fusion]: Le fusion si trouvé, None sinon
        """
        pass

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Optional[Fusion]:
        """
        Obtenir un fusion par UUID.

        Args:
            uuid (str): L'UUID du fusion

        Returns:
            Optional[Fusion]: Le fusion si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Fusion:
        """
        Créer un nouveau fusion.

        Args:
            **kwargs: Données du fusion

        Returns:
            Fusion: Le fusion créé
        """
        pass

    @abstractmethod
    def update(self, fusion: Fusion, **kwargs) -> Fusion:
        """
        Mettre à jour un fusion existant.

        Args:
            fusion (Fusion): Le fusion à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Fusion: Le fusion mis à jour
        """
        pass

    @abstractmethod
    def delete(self, fusion: Fusion) -> bool:
        """
        Supprimer un fusion.

        Args:
            fusion (Fusion): Le fusion à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, fusion_id: int) -> bool:
        """
        Vérifier si un fusion existe par ID.

        Args:
            fusion_id (int): L'ID du fusion

        Returns:
            bool: True si le fusion existe, False sinon
        """
        pass