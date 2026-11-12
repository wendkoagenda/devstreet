"""
Message service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import Message
from app.communaute.repositories.message_repository import MessageRepository


class MessageService:
    """
    Classe de service pour la logique métier liée aux messages.
    """

    def __init__(self):
        self.message_repository = MessageRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les messages, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les messages filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.message_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, message_id: int) -> Optional[Message]:
        """
        Obtenir un message par ID.
        
        Args:
            message_id (int): L'ID du message
            
        Returns:
            Optional[Message]: Le message si trouvé, None sinon
        """
        return self.message_repository.get_by_id(message_id)

    def create(self, message_data: Dict[str, Any]) -> Message:
        """
        Créer un nouveau message avec validation.
        
        Args:
            message_data (Dict[str, Any]): Données du message
            
        Returns:
            Message: Le message créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(message_data)
        
        return self.message_repository.create(**message_data)

    def update(self, message_id: int, message_data: Dict[str, Any], partial: bool = False) -> Optional[Message]:
        """
        Mettre à jour un message existant.
        
        Args:
            message_id (int): L'ID du message
            message_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Message]: Le message mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        message = self.message_repository.get_by_id(message_id)
        if not message:
            return None

        # Validation des données
        if not partial:
            self.validate_data(message_data)

        return self.message_repository.update(message, **message_data)

    def delete(self, message_id: int) -> bool:
        """
        Supprimer un message.
        
        Args:
            message_id (int): L'ID du message
            
        Returns:
            bool: True si supprimé avec succès, False si message non trouvé
        """
        message = self.message_repository.get_by_id(message_id)
        if not message:
            return False

        return self.message_repository.delete(message)

    def validate_data(self, message_data: Dict[str, Any]):
        """
        Valider les données du message.
        
        Args:
            message_data (Dict[str, Any]): Données du message à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins