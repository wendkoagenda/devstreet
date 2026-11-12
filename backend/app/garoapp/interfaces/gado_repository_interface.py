"""
Gado repository interface définissant le contrat pour l'accès aux données gados.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.garoapp.models import Gado


class GadoRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository gados.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les gado, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les gado filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, gado_id: int) -> Optional[Gado]:
        """
        Obtenir un gado par ID.

        Args:
            gado_id (int): L'ID du gado

        Returns:
            Optional[Gado]: Le gado si trouvé, None sinon
        """
        pass

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Optional[Gado]:
        """
        Obtenir un gado par UUID.

        Args:
            uuid (str): L'UUID du gado

        Returns:
            Optional[Gado]: Le gado si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Gado:
        """
        Créer un nouveau gado.

        Args:
            **kwargs: Données du gado

        Returns:
            Gado: Le gado créé
        """
        pass

    @abstractmethod
    def update(self, gado: Gado, **kwargs) -> Gado:
        """
        Mettre à jour un gado existant.

        Args:
            gado (Gado): Le gado à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Gado: Le gado mis à jour
        """
        pass

    @abstractmethod
    def delete(self, gado: Gado) -> bool:
        """
        Supprimer un gado.

        Args:
            gado (Gado): Le gado à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, gado_id: int) -> bool:
        """
        Vérifier si un gado existe par ID.

        Args:
            gado_id (int): L'ID du gado

        Returns:
            bool: True si le gado existe, False sinon
        """
        pass