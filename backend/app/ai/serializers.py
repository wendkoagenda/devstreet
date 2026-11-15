from rest_framework import serializers

from app.ai.models import AiConversation, AiMessage


class AiMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiMessage
        fields = (
            "id",
            "role",
            "content",
            "provider",
            "failover_reason",
            "created_at",
        )
        read_only_fields = fields


class AiConversationSerializer(serializers.ModelSerializer):
    messages = AiMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AiConversation
        fields = (
            "id",
            "consumer",
            "title",
            "created_at",
            "updated_at",
            "messages",
        )
        read_only_fields = fields


class AiConversationCreateSerializer(serializers.Serializer):
    consumer = serializers.ChoiceField(
        choices=("hub", "generic", "selina"), default="generic", required=False
    )
    title = serializers.CharField(max_length=180, required=False, allow_blank=True)


class AiConversationListSerializer(serializers.ModelSerializer):
    """Liste légère sans messages (historique Selina / Récents)."""

    class Meta:
        model = AiConversation
        fields = ("id", "consumer", "title", "created_at", "updated_at")
        read_only_fields = fields


class AiMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=8000)
    context_text = serializers.CharField(
        max_length=16000, required=False, allow_blank=True, default=""
    )


class AiChatResponseSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    user_message = serializers.CharField()
    assistant_message = serializers.CharField()
    provider = serializers.CharField()
    model = serializers.CharField()
    failover_reason = serializers.CharField(allow_null=True, required=False)
    message_id = serializers.IntegerField()
