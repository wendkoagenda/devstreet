"""
Conversation repository interface définissant le contrat pour l'accès aux données conversations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import Conversation


class ConversationRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository conversations.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les conversation, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les conversation filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """
        Obtenir un conversation par ID.

        Args:
            conversation_id (int): L'ID du conversation

        Returns:
            Optional[Conversation]: Le conversation si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Conversation:
        """
        Créer un nouveau conversation.

        Args:
            **kwargs: Données du conversation

        Returns:
            Conversation: Le conversation créé
        """
        pass

    @abstractmethod
    def update(self, conversation: Conversation, **kwargs) -> Conversation:
        """
        Mettre à jour un conversation existant.

        Args:
            conversation (Conversation): Le conversation à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Conversation: Le conversation mis à jour
        """
        pass

    @abstractmethod
    def delete(self, conversation: Conversation) -> bool:
        """
        Supprimer un conversation.

        Args:
            conversation (Conversation): Le conversation à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, conversation_id: int) -> bool:
        """
        Vérifier si un conversation existe par ID.

        Args:
            conversation_id (int): L'ID du conversation

        Returns:
            bool: True si le conversation existe, False sinon
        """
        pass