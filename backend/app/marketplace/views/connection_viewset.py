"""
ViewSet pour la gestion des connections.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import Connection
from app.marketplace.serializers import ConnectionSerializer
from app.marketplace.services.connection_service import ConnectionService
from app.marketplace.permissions.connection_permissions import (
    CanViewConnection,
    CanCreateConnection,
    CanUpdateConnection,
    CanDeleteConnection
)


class ConnectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les connections.
    """
    swagger_tags = ['V1 - Connection']
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection_service = ConnectionService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewConnection]
        elif self.action == 'create':
            permission_classes = [CanCreateConnection]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateConnection]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteConnection]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les connections (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ConnectionSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Connection']
    )
    def list(self, request):
        """
        Retourne une page de connections (format : count, next, previous, results).
        """
        try:
            connections = self.connection_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(connections)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un connection par son ID",
        responses={
            200: ConnectionSerializer,
            404: "Connection non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Connection']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un connection spécifique.
        """
        connection = self.connection_service.get_by_id(pk)
        if not connection:
            return Response(
                {'error': 'Connection non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(connection)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau connection",
        request_body=ConnectionSerializer,
        responses={
            201: ConnectionSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Connection']
    )
    def create(self, request):
        """
        Crée un nouveau connection.
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
            connection = self.connection_service.create(data)
            serializer = self.get_serializer(connection)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un connection",
        request_body=ConnectionSerializer,
        responses={
            200: ConnectionSerializer,
            400: "Données invalides",
            404: "Connection non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Connection']
    )
    def update(self, request, pk=None):
        """
        Met à jour un connection existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            connection = self.connection_service.update(pk, data)
            if connection is None:
                return Response(
                    {'error': 'Connection non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(connection)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un connection",
        request_body=ConnectionSerializer,
        responses={
            200: ConnectionSerializer,
            400: "Données invalides",
            404: "Connection non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Connection']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un connection existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            connection = self.connection_service.update(pk, data, partial=True)
            if connection is None:
                return Response(
                    {'error': 'Connection non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(connection)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un connection",
        responses={
            204: "Connection supprimé avec succès",
            404: "Connection non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Connection']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un connection.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.connection_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Connection non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )