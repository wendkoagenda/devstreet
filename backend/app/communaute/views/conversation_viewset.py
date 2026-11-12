"""
ViewSet pour la gestion des conversations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import Conversation
from app.communaute.serializers import ConversationSerializer
from app.communaute.services.conversation_service import ConversationService
from app.communaute.permissions.conversation_permissions import (
    CanViewConversation,
    CanCreateConversation,
    CanUpdateConversation,
    CanDeleteConversation
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les conversations.
    """
    swagger_tags = ['V1 - Conversation']
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_service = ConversationService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewConversation]
        elif self.action == 'create':
            permission_classes = [CanCreateConversation]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateConversation]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteConversation]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les conversations (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ConversationSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Conversation']
    )
    def list(self, request):
        """
        Retourne une page de conversations (format : count, next, previous, results).
        """
        try:
            conversations = self.conversation_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(conversations)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un conversation par son ID",
        responses={
            200: ConversationSerializer,
            404: "Conversation non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Conversation']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un conversation spécifique.
        """
        conversation = self.conversation_service.get_by_id(pk)
        if not conversation:
            return Response(
                {'error': 'Conversation non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau conversation",
        request_body=ConversationSerializer,
        responses={
            201: ConversationSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Conversation']
    )
    def create(self, request):
        """
        Crée un nouveau conversation.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('updated_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['created_by'] = request.user.id
                data['updated_by'] = request.user.id
            conversation = self.conversation_service.create(data)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un conversation",
        request_body=ConversationSerializer,
        responses={
            200: ConversationSerializer,
            400: "Données invalides",
            404: "Conversation non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Conversation']
    )
    def update(self, request, pk=None):
        """
        Met à jour un conversation existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            conversation = self.conversation_service.update(pk, data)
            if conversation is None:
                return Response(
                    {'error': 'Conversation non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un conversation",
        request_body=ConversationSerializer,
        responses={
            200: ConversationSerializer,
            400: "Données invalides",
            404: "Conversation non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Conversation']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un conversation existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            conversation = self.conversation_service.update(pk, data, partial=True)
            if conversation is None:
                return Response(
                    {'error': 'Conversation non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un conversation",
        responses={
            204: "Conversation supprimé avec succès",
            404: "Conversation non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Conversation']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un conversation.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.conversation_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Conversation non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )