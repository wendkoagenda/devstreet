"""
ViewSet pour la gestion des messages.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import Message
from app.communaute.serializers import MessageSerializer
from app.communaute.services.message_service import MessageService
from app.communaute.permissions.message_permissions import (
    CanViewMessage,
    CanCreateMessage,
    CanUpdateMessage,
    CanDeleteMessage
)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les messages.
    """
    swagger_tags = ['V1 - Message']
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_service = MessageService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewMessage]
        elif self.action == 'create':
            permission_classes = [CanCreateMessage]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateMessage]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteMessage]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les messages (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: MessageSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Message']
    )
    def list(self, request):
        """
        Retourne une page de messages (format : count, next, previous, results).
        """
        try:
            messages = self.message_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(messages)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un message par son ID",
        responses={
            200: MessageSerializer,
            404: "Message non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Message']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un message spécifique.
        """
        message = self.message_service.get_by_id(pk)
        if not message:
            return Response(
                {'error': 'Message non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(message)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau message",
        request_body=MessageSerializer,
        responses={
            201: MessageSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Message']
    )
    def create(self, request):
        """
        Crée un nouveau message.
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
            message = self.message_service.create(data)
            serializer = self.get_serializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un message",
        request_body=MessageSerializer,
        responses={
            200: MessageSerializer,
            400: "Données invalides",
            404: "Message non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Message']
    )
    def update(self, request, pk=None):
        """
        Met à jour un message existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            message = self.message_service.update(pk, data)
            if message is None:
                return Response(
                    {'error': 'Message non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(message)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un message",
        request_body=MessageSerializer,
        responses={
            200: MessageSerializer,
            400: "Données invalides",
            404: "Message non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Message']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un message existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            message = self.message_service.update(pk, data, partial=True)
            if message is None:
                return Response(
                    {'error': 'Message non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(message)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un message",
        responses={
            204: "Message supprimé avec succès",
            404: "Message non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Message']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un message.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.message_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Message non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )