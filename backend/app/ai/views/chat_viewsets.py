from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from app.ai.serializers import (
    AiChatResponseSerializer,
    AiConversationCreateSerializer,
    AiConversationListSerializer,
    AiConversationSerializer,
    AiMessageCreateSerializer,
)
from app.ai.services.chat_service import ChatService


def validated(serializer_class, data):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class AiConversationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = AiConversationSerializer
    lookup_value_regex = "[0-9]+"
    swagger_tags = ["V1 - AiConversation"]

    def get_queryset(self):
        return []

    @swagger_auto_schema(
        responses={200: AiConversationListSerializer(many=True)},
        tags=["V1 - AiConversation"],
        manual_parameters=[],
    )
    def list(self, request, *args, **kwargs):
        consumer = (request.query_params.get("consumer") or "").strip() or None
        conversations = ChatService().list_conversations(
            request.user, consumer=consumer
        )
        page = self.paginate_queryset(conversations)
        serializer = AiConversationListSerializer(
            page if page is not None else conversations, many=True
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=AiConversationCreateSerializer,
        responses={201: AiConversationSerializer},
        tags=["V1 - AiConversation"],
    )
    def create(self, request, *args, **kwargs):
        data = validated(AiConversationCreateSerializer, request.data)
        conversation = ChatService().create_conversation(
            request.user,
            consumer=data.get("consumer") or "generic",
            title=data.get("title") or "",
        )
        return Response(
            AiConversationSerializer(conversation).data, status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(responses={200: AiConversationSerializer}, tags=["V1 - AiConversation"])
    def retrieve(self, request, *args, **kwargs):
        conversation = ChatService().get_conversation(request.user, int(kwargs["pk"]))
        return Response(AiConversationSerializer(conversation).data)

    @swagger_auto_schema(
        method="post",
        request_body=AiMessageCreateSerializer,
        responses={200: AiChatResponseSerializer},
        tags=["V1 - AiConversation"],
    )
    @action(detail=True, methods=["post"], url_path="messages")
    def messages(self, request, pk=None):
        data = validated(AiMessageCreateSerializer, request.data)
        result = ChatService().send_message(
            request.user,
            int(pk),
            content=data["content"],
            context_text=data.get("context_text") or "",
        )
        return Response(AiChatResponseSerializer(result).data)
