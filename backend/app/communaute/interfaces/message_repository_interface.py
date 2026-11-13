"""
Message repository interface définissant le contrat pour l'accès aux données messages.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import Message


class MessageRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository messages.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les message, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les message filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, message_id: int) -> Optional[Message]:
        """
        Obtenir un message par ID.

        Args:
            message_id (int): L'ID du message

        Returns:
            Optional[Message]: Le message si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Message:
        """
        Créer un nouveau message.

        Args:
            **kwargs: Données du message

        Returns:
            Message: Le message créé
        """
        pass

    @abstractmethod
    def update(self, message: Message, **kwargs) -> Message:
        """
        Mettre à jour un message existant.

        Args:
            message (Message): Le message à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Message: Le message mis à jour
        """
        pass

    @abstractmethod
    def delete(self, message: Message) -> bool:
        """
        Supprimer un message.

        Args:
            message (Message): Le message à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, message_id: int) -> bool:
        """
        Vérifier si un message existe par ID.

        Args:
            message_id (int): L'ID du message

        Returns:
            bool: True si le message existe, False sinon
        """
        pass