from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from app.ai.models import AiConversation, AiMessage


class ChatRepository:
    def create_conversation(self, user, *, consumer: str, title: str = "") -> AiConversation:
        return AiConversation.objects.create(
            user=user, consumer=consumer, title=title[:180]
        )

    def get_conversation_for_user(self, user, pk: int) -> AiConversation:
        return get_object_or_404(AiConversation.objects.filter(user=user), pk=pk)

    def list_messages(self, conversation: AiConversation):
        return conversation.messages.all()

    def add_message(
        self,
        conversation: AiConversation,
        *,
        role: str,
        content: str,
        provider: str = "",
        failover_reason: str = "",
    ) -> AiMessage:
        message = AiMessage.objects.create(
            conversation=conversation,
            role=role,
            content=content,
            provider=provider,
            failover_reason=failover_reason,
        )
        conversation.save(update_fields=["updated_at"])
        return message

    def messages_today_count(self, user) -> int:
        start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return AiMessage.objects.filter(
            conversation__user=user,
            role=AiMessage.ROLE_USER,
            created_at__gte=start,
        ).count()

    def conversation_with_messages(self, conversation: AiConversation) -> AiConversation:
        return (
            AiConversation.objects.filter(pk=conversation.pk)
            .annotate(message_count=Count("messages", filter=Q(messages__isnull=False)))
            .prefetch_related("messages")
            .get()
        )
