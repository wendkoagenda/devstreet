"""
Connection repository interface définissant le contrat pour l'accès aux données connections.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Connection


class ConnectionRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository connections.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les connection, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les connection filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, connection_id: int) -> Optional[Connection]:
        """
        Obtenir un connection par ID.

        Args:
            connection_id (int): L'ID du connection

        Returns:
            Optional[Connection]: Le connection si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Connection:
        """
        Créer un nouveau connection.

        Args:
            **kwargs: Données du connection

        Returns:
            Connection: Le connection créé
        """
        pass

    @abstractmethod
    def update(self, connection: Connection, **kwargs) -> Connection:
        """
        Mettre à jour un connection existant.

        Args:
            connection (Connection): Le connection à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Connection: Le connection mis à jour
        """
        pass

    @abstractmethod
    def delete(self, connection: Connection) -> bool:
        """
        Supprimer un connection.

        Args:
            connection (Connection): Le connection à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, connection_id: int) -> bool:
        """
        Vérifier si un connection existe par ID.

        Args:
            connection_id (int): L'ID du connection

        Returns:
            bool: True si le connection existe, False sinon
        """
        pass