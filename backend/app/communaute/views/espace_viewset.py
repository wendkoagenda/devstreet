"""
ViewSet pour la gestion des espaces.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import Espace
from app.communaute.serializers import EspaceSerializer
from app.communaute.services.espace_service import EspaceService
from app.communaute.permissions.espace_permissions import (
    CanViewEspace,
    CanCreateEspace,
    CanUpdateEspace,
    CanDeleteEspace
)


class EspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les espaces.
    """
    swagger_tags = ['V1 - Espace']
    queryset = Espace.objects.all()
    serializer_class = EspaceSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.espace_service = EspaceService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewEspace]
        elif self.action == 'create':
            permission_classes = [CanCreateEspace]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateEspace]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteEspace]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les espaces (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: EspaceSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Espace']
    )
    def list(self, request):
        """
        Retourne une page de espaces (format : count, next, previous, results).
        """
        try:
            espaces = self.espace_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(espaces)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un espace par son ID",
        responses={
            200: EspaceSerializer,
            404: "Espace non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Espace']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un espace spécifique.
        """
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(espace)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau espace",
        request_body=EspaceSerializer,
        responses={
            201: EspaceSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Espace']
    )
    def create(self, request):
        """
        Crée un nouveau espace.
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
            espace = self.espace_service.create(data)
            serializer = self.get_serializer(espace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un espace",
        request_body=EspaceSerializer,
        responses={
            200: EspaceSerializer,
            400: "Données invalides",
            404: "Espace non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Espace']
    )
    def update(self, request, pk=None):
        """
        Met à jour un espace existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            espace = self.espace_service.update(pk, data)
            if espace is None:
                return Response(
                    {'error': 'Espace non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(espace)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un espace",
        request_body=EspaceSerializer,
        responses={
            200: EspaceSerializer,
            400: "Données invalides",
            404: "Espace non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Espace']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un espace existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            espace = self.espace_service.update(pk, data, partial=True)
            if espace is None:
                return Response(
                    {'error': 'Espace non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(espace)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un espace",
        responses={
            204: "Espace supprimé avec succès",
            404: "Espace non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Espace']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un espace.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.espace_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Espace non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )