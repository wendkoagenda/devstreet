"""
ViewSet pour les messages privés d'une conversation.
"""
import logging

from django.core.exceptions import ValidationError
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.communaute.serializers import MessageSerializer
from app.communaute.services.conversation_service import ConversationService
from app.communaute.services.message_service import MessageService
from app.core.pagination import StandardPagination


logger = logging.getLogger(__name__)


class MessageViewSet(viewsets.ViewSet):
    """Liste et envoi de messages (participants uniquement)."""

    swagger_tags = ['V1 - Message']
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_service = MessageService()
        self.conversation_service = ConversationService()
        self._paginator = None

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', {'request': self.request})
        return MessageSerializer(*args, **kwargs)

    @property
    def paginator(self):
        if self._paginator is None:
            self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)

    def _access_error_response(self, exc):
        if isinstance(exc, Http404):
            return Response(
                {'error': 'Conversation introuvable'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if isinstance(exc, ValidationError):
            message = str(exc)
            if 'accès' in message.lower():
                return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        raise exc

    @swagger_auto_schema(
        operation_description="Lister les messages d'une conversation (?conversation=ID)",
        manual_parameters=[
            openapi.Parameter(
                'conversation',
                openapi.IN_QUERY,
                description='ID de la conversation',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={200: MessageSerializer(many=True), 403: 'Accès refusé'},
        security=[{'Bearer': []}],
        tags=['V1 - Message'],
    )
    def list(self, request):
        conversation_raw = request.query_params.get('conversation')
        try:
            conversation_id = int(conversation_raw)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Paramètre conversation requis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            messages = self.message_service.list_for_conversation(
                conversation_id=conversation_id,
                membre=request.user,
            )
            conversation = self.conversation_service.get_for_user(
                conversation_id, request.user
            )
            from app.communaute.services.activity_service import ActivityService

            ActivityService().mark_conversation_read(
                conversation=conversation, acteur=request.user
            )
        except (Http404, ValidationError) as e:
            return self._access_error_response(e)

        page = self.paginate_queryset(messages)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(messages, many=True).data)

    @swagger_auto_schema(
        operation_description="Envoyer un message dans une conversation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['conversation_id', 'texte'],
            properties={
                'conversation_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'texte': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: MessageSerializer,
            400: 'Données invalides',
            403: 'Accès refusé',
        },
        security=[{'Bearer': []}],
        tags=['V1 - Message'],
    )
    def create(self, request):
        conversation_raw = request.data.get('conversation_id')
        texte = request.data.get('texte', '')
        try:
            conversation_id = int(conversation_raw)
        except (TypeError, ValueError):
            return Response(
                {'error': 'conversation_id invalide.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            message = self.message_service.create_message(
                conversation_id=conversation_id,
                auteur=request.user,
                texte=texte,
            )
        except (Http404, ValidationError) as e:
            return self._access_error_response(e)

        payload = self.get_serializer(message).data
        try:
            from app.communaute.socketio_app import emit_message_new

            emit_message_new(conversation_id, payload)
        except Exception:
            # L'envoi REST reste valide même si le push temps réel échoue
            logger.exception(
                "Push temps réel du message impossible (conversation %s)", conversation_id
            )

        return Response(payload, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Détail d'un message (participants uniquement)",
        responses={200: MessageSerializer, 403: 'Accès refusé', 404: 'Introuvable'},
        security=[{'Bearer': []}],
        tags=['V1 - Message'],
    )
    def retrieve(self, request, pk=None):
        try:
            message_id = int(pk)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Identifiant invalide'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = self.message_service.get_by_id(message_id)
        if message is None:
            return Response(
                {'error': 'Message introuvable'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            self.conversation_service.get_for_user(
                message.conversation_id, request.user
            )
        except (Http404, ValidationError) as e:
            return self._access_error_response(e)

        return Response(self.get_serializer(message).data)
