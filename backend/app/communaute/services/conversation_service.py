"""
Conversation service layer pour les opérations de logique métier.
"""
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.http import Http404

from app.communaute.models import Conversation
from app.communaute.repositories.conversation_repository import ConversationRepository

User = get_user_model()


class ConversationService:
    """Logique métier des conversations privées (une paire = une conversation)."""

    def __init__(self):
        self.conversation_repository = ConversationRepository()

    @staticmethod
    def _paire_ordonnee(user_a_id: int, user_b_id: int) -> tuple[int, int]:
        if user_a_id == user_b_id:
            raise ValidationError('Impossible de démarrer une conversation avec soi-même.')
        return (min(user_a_id, user_b_id), max(user_a_id, user_b_id))

    def list_for_user(self, membre: User) -> QuerySet:
        """Conversations où le membre est partie prenante."""
        return (
            Conversation.objects.filter(Q(membre_1=membre) | Q(membre_2=membre))
            .select_related('membre_1', 'membre_2')
            .order_by('-updated_at', '-id')
        )

    def get_for_user(
        self, conversation_id: int, membre: User
    ) -> Conversation:
        conversation = (
            Conversation.objects.filter(id=conversation_id)
            .select_related('membre_1', 'membre_2')
            .first()
        )
        if conversation is None:
            raise Http404('Conversation introuvable.')
        if not conversation.implique(membre.id):
            raise ValidationError(
                'Tu n\'as pas accès à cette conversation.'
            )
        return conversation

    def get_or_create_with(
        self, *, initiateur: User, destinataire_id: int
    ) -> Conversation:
        """Ouvre ou retrouve la conversation unique entre deux membres."""
        destinataire = User.objects.filter(id=destinataire_id).first()
        if destinataire is None:
            raise ValidationError('Destinataire introuvable.')

        id_1, id_2 = self._paire_ordonnee(initiateur.id, destinataire.id)
        existing = (
            Conversation.objects.filter(membre_1_id=id_1, membre_2_id=id_2)
            .select_related('membre_1', 'membre_2')
            .first()
        )
        if existing:
            return existing

        return Conversation.objects.create(
            membre_1_id=id_1,
            membre_2_id=id_2,
            created_by=initiateur.id,
            updated_by=initiateur.id,
        )

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        return self.conversation_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        return self.conversation_repository.get_by_id(conversation_id)

    def create(self, conversation_data: Dict[str, Any]) -> Conversation:
        self.validate_data(conversation_data)
        return self.conversation_repository.create(**conversation_data)

    def update(
        self,
        conversation_id: int,
        conversation_data: Dict[str, Any],
        partial: bool = False,
    ) -> Optional[Conversation]:
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if not conversation:
            return None
        if not partial:
            self.validate_data(conversation_data)
        return self.conversation_repository.update(conversation, **conversation_data)

    def delete(self, conversation_id: int) -> bool:
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if not conversation:
            return False
        return self.conversation_repository.delete(conversation)

    def validate_data(self, conversation_data: Dict[str, Any]):
        return
