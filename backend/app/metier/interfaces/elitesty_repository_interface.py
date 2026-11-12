"""
Elitesty repository interface définissant le contrat pour l'accès aux données elitestys.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.metier.models import Elitesty


class ElitestyRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository elitestys.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les elitesty, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les elitesty filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, elitesty_id: int) -> Optional[Elitesty]:
        """
        Obtenir un elitesty par ID.

        Args:
            elitesty_id (int): L'ID du elitesty

        Returns:
            Optional[Elitesty]: Le elitesty si trouvé, None sinon
        """
        pass

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Optional[Elitesty]:
        """
        Obtenir un elitesty par UUID.

        Args:
            uuid (str): L'UUID du elitesty

        Returns:
            Optional[Elitesty]: Le elitesty si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Elitesty:
        """
        Créer un nouveau elitesty.

        Args:
            **kwargs: Données du elitesty

        Returns:
            Elitesty: Le elitesty créé
        """
        pass

    @abstractmethod
    def update(self, elitesty: Elitesty, **kwargs) -> Elitesty:
        """
        Mettre à jour un elitesty existant.

        Args:
            elitesty (Elitesty): Le elitesty à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Elitesty: Le elitesty mis à jour
        """
        pass

    @abstractmethod
    def delete(self, elitesty: Elitesty) -> bool:
        """
        Supprimer un elitesty.

        Args:
            elitesty (Elitesty): Le elitesty à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, elitesty_id: int) -> bool:
        """
        Vérifier si un elitesty existe par ID.

        Args:
            elitesty_id (int): L'ID du elitesty

        Returns:
            bool: True si le elitesty existe, False sinon
        """
        pass