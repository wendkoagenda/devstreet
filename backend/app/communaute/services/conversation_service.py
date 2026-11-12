"""
Conversation service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import Conversation
from app.communaute.repositories.conversation_repository import ConversationRepository


class ConversationService:
    """
    Classe de service pour la logique métier liée aux conversations.
    """

    def __init__(self):
        self.conversation_repository = ConversationRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les conversations, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les conversations filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.conversation_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """
        Obtenir un conversation par ID.
        
        Args:
            conversation_id (int): L'ID du conversation
            
        Returns:
            Optional[Conversation]: Le conversation si trouvé, None sinon
        """
        return self.conversation_repository.get_by_id(conversation_id)

    def create(self, conversation_data: Dict[str, Any]) -> Conversation:
        """
        Créer un nouveau conversation avec validation.
        
        Args:
            conversation_data (Dict[str, Any]): Données du conversation
            
        Returns:
            Conversation: Le conversation créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(conversation_data)
        
        return self.conversation_repository.create(**conversation_data)

    def update(self, conversation_id: int, conversation_data: Dict[str, Any], partial: bool = False) -> Optional[Conversation]:
        """
        Mettre à jour un conversation existant.
        
        Args:
            conversation_id (int): L'ID du conversation
            conversation_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Conversation]: Le conversation mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if not conversation:
            return None

        # Validation des données
        if not partial:
            self.validate_data(conversation_data)

        return self.conversation_repository.update(conversation, **conversation_data)

    def delete(self, conversation_id: int) -> bool:
        """
        Supprimer un conversation.
        
        Args:
            conversation_id (int): L'ID du conversation
            
        Returns:
            bool: True si supprimé avec succès, False si conversation non trouvé
        """
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if not conversation:
            return False

        return self.conversation_repository.delete(conversation)

    def validate_data(self, conversation_data: Dict[str, Any]):
        """
        Valider les données du conversation.
        
        Args:
            conversation_data (Dict[str, Any]): Données du conversation à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins