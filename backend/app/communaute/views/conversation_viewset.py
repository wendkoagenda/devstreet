"""
ViewSet pour les conversations privées (paire unique entre deux membres).
"""
from django.core.exceptions import ValidationError
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.communaute.models import Conversation
from app.communaute.serializers import ConversationSerializer
from app.communaute.services.conversation_service import ConversationService
from app.core.pagination import StandardPagination


class ConversationViewSet(viewsets.ViewSet):
    """Liste, ouverture et détail des conversations du membre connecté."""

    swagger_tags = ['V1 - Conversation']
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_service = ConversationService()
        self._paginator = None

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', {'request': self.request})
        return ConversationSerializer(*args, **kwargs)

    @property
    def paginator(self):
        if self._paginator is None:
            self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)

    @swagger_auto_schema(
        operation_description="Lister mes conversations privées",
        responses={200: ConversationSerializer(many=True)},
        security=[{'Bearer': []}],
        tags=['V1 - Conversation'],
    )
    def list(self, request):
        conversations = self.conversation_service.list_for_user(request.user)
        page = self.paginate_queryset(conversations)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(conversations, many=True).data)

    @swagger_auto_schema(
        operation_description="Ouvrir ou retrouver la conversation avec un destinataire",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['destinataire_id'],
            properties={
                'destinataire_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={
            200: ConversationSerializer,
            201: ConversationSerializer,
            400: 'Données invalides',
        },
        security=[{'Bearer': []}],
        tags=['V1 - Conversation'],
    )
    def create(self, request):
        destinataire_raw = request.data.get('destinataire_id')
        try:
            destinataire_id = int(destinataire_raw)
        except (TypeError, ValueError):
            return Response(
                {'error': 'destinataire_id invalide.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            id_1, id_2 = min(request.user.id, destinataire_id), max(
                request.user.id, destinataire_id
            )
            existed = Conversation.objects.filter(
                membre_1_id=id_1, membre_2_id=id_2
            ).exists()
            conversation = self.conversation_service.get_or_create_with(
                initiateur=request.user,
                destinataire_id=destinataire_id,
            )
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            self.get_serializer(conversation).data,
            status=status.HTTP_200_OK if existed else status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_description="Détail d'une conversation (participants uniquement)",
        responses={
            200: ConversationSerializer,
            403: 'Accès refusé',
            404: 'Conversation introuvable',
        },
        security=[{'Bearer': []}],
        tags=['V1 - Conversation'],
    )
    def retrieve(self, request, pk=None):
        try:
            conversation = self.conversation_service.get_for_user(
                int(pk), request.user
            )
        except Http404:
            return Response(
                {'error': 'Conversation introuvable'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError:
            return Response(
                {'error': "Tu n'as pas accès à cette conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except (TypeError, ValueError):
            return Response(
                {'error': 'Identifiant invalide'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.get_serializer(conversation).data)
