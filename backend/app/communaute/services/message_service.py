"""
Message service layer pour les opérations de logique métier.
"""
from typing import Any, Dict, List, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils import timezone

from app.communaute.models import Message
from app.communaute.repositories.message_repository import MessageRepository
from app.communaute.services.conversation_service import ConversationService

User = get_user_model()


class MessageService:
    """Logique métier des messages privés."""

    def __init__(self):
        self.message_repository = MessageRepository()
        self.conversation_service = ConversationService()

    def list_for_conversation(
        self, *, conversation_id: int, membre: User
    ) -> List[Message]:
        conversation = self.conversation_service.get_for_user(
            conversation_id, membre
        )
        return list(
            Message.objects.filter(conversation=conversation)
            .select_related('auteur', 'conversation')
            .order_by('sent_at', 'id')
        )

    def create_message(
        self,
        *,
        conversation_id: int,
        auteur: User,
        texte: str,
    ) -> Message:
        texte = (texte or '').strip()
        if not texte:
            raise ValidationError('Le texte du message est obligatoire.')

        conversation = self.conversation_service.get_for_user(
            conversation_id, auteur
        )
        message = Message.objects.create(
            conversation=conversation,
            auteur=auteur,
            texte=texte,
            created_by=auteur.id,
            updated_by=auteur.id,
        )
        conversation.updated_at = timezone.now()
        conversation.updated_by = auteur.id
        conversation.save(update_fields=['updated_at', 'updated_by'])
        return (
            Message.objects.filter(id=message.id)
            .select_related('auteur', 'conversation')
            .first()
        )

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        return self.message_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, message_id: int) -> Optional[Message]:
        return self.message_repository.get_by_id(message_id)

    def create(self, message_data: Dict[str, Any]) -> Message:
        self.validate_data(message_data)
        return self.message_repository.create(**message_data)

    def update(
        self, message_id: int, message_data: Dict[str, Any], partial: bool = False
    ) -> Optional[Message]:
        message = self.message_repository.get_by_id(message_id)
        if not message:
            return None
        if not partial:
            self.validate_data(message_data)
        return self.message_repository.update(message, **message_data)

    def delete(self, message_id: int) -> bool:
        message = self.message_repository.get_by_id(message_id)
        if not message:
            return False
        return self.message_repository.delete(message)

    def validate_data(self, message_data: Dict[str, Any]):
        return
