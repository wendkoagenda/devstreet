"""
ViewSet pour la gestion des dragons.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.metier.models import Dragon
from app.metier.serializers import DragonSerializer
from app.metier.services.dragon_service import DragonService
from app.metier.permissions.dragon_permissions import (
    CanViewDragon,
    CanCreateDragon,
    CanUpdateDragon,
    CanDeleteDragon
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from app.metier.utils.file_field_utils import process_uploaded_files
from app.metier.utils.request_data_utils import flatten_request_data


class DragonViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les dragons.
    """
    swagger_tags = ['V1 - Dragon']
    queryset = Dragon.objects.all()
    serializer_class = DragonSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    FILE_FIELD_CONFIG = {
        "document": {
            "upload_folder": "dragon_documents",
            "allowed_extensions": ['.pdf', '.png'],
            "max_size_mb": 5,
        },
    }
    FILE_FIELD_NAMES = ["document"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dragon_service = DragonService()

    def _prepare_write_data(self, request):
        data = flatten_request_data(request.data)
        for field_name in self.FILE_FIELD_NAMES:
            data.pop(f"{field_name}_path", None)
        uploaded_paths = process_uploaded_files(request, self.FILE_FIELD_CONFIG)
        data.update(uploaded_paths)
        return data

    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewDragon]
        elif self.action == 'create':
            permission_classes = [CanCreateDragon]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateDragon]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteDragon]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les dragons (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: DragonSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Dragon']
    )
    def list(self, request):
        """
        Retourne une page de dragons (format : count, next, previous, results).
        """
        try:
            dragons = self.dragon_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(dragons)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un dragon par son ID",
        responses={
            200: DragonSerializer,
            404: "Dragon non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Dragon']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un dragon spécifique.
        """
        dragon = self.dragon_service.get_by_id(pk)
        if not dragon:
            return Response(
                {'error': 'Dragon non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(dragon)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau dragon",
        request_body=DragonSerializer,
        responses={
            201: DragonSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Dragon']
    )
    def create(self, request):
        """
        Crée un nouveau dragon.
        """
        try:
            data = request.data.copy()
            data = self._prepare_write_data(request)
            data.pop('created_by', None)
            data.pop('updated_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['created_by'] = request.user.id
                data['updated_by'] = request.user.id
            dragon = self.dragon_service.create(data)
            serializer = self.get_serializer(dragon)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un dragon",
        request_body=DragonSerializer,
        responses={
            200: DragonSerializer,
            400: "Données invalides",
            404: "Dragon non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Dragon']
    )
    def update(self, request, pk=None):
        """
        Met à jour un dragon existant.
        """
        try:
            data = request.data.copy()
            data = self._prepare_write_data(request)
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            dragon = self.dragon_service.update(pk, data)
            if dragon is None:
                return Response(
                    {'error': 'Dragon non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(dragon)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un dragon",
        request_body=DragonSerializer,
        responses={
            200: DragonSerializer,
            400: "Données invalides",
            404: "Dragon non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Dragon']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un dragon existant.
        """
        try:
            data = request.data.copy()
            data = self._prepare_write_data(request)
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            dragon = self.dragon_service.update(pk, data, partial=True)
            if dragon is None:
                return Response(
                    {'error': 'Dragon non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(dragon)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un dragon",
        responses={
            204: "Dragon supprimé avec succès",
            404: "Dragon non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Dragon']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un dragon.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.dragon_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Dragon non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )