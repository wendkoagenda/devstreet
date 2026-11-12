"""
ViewSet pour la gestion des profils.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import Profil
from app.marketplace.serializers import ProfilSerializer
from app.marketplace.services.profil_service import ProfilService
from app.marketplace.permissions.profil_permissions import (
    CanViewProfil,
    CanCreateProfil,
    CanUpdateProfil,
    CanDeleteProfil
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from app.metier.utils.file_field_utils import process_uploaded_files
from app.metier.utils.request_data_utils import flatten_request_data


class ProfilViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les profils.
    """
    swagger_tags = ['V1 - Profil']
    queryset = Profil.objects.all()
    serializer_class = ProfilSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    FILE_FIELD_CONFIG = {
        "photo": {
            "upload_folder": "profils/photo",
            "allowed_extensions": ['.jpg', '.jpeg', '.png', '.webp'],
            "max_size_mb": 5,
        },
    }
    FILE_FIELD_NAMES = ["photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profil_service = ProfilService()

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
            permission_classes = [CanViewProfil]
        elif self.action == 'create':
            permission_classes = [CanCreateProfil]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateProfil]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteProfil]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les profils (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ProfilSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Profil']
    )
    def list(self, request):
        """
        Retourne une page de profils (format : count, next, previous, results).
        """
        try:
            profils = self.profil_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(profils)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un profil par son ID",
        responses={
            200: ProfilSerializer,
            404: "Profil non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Profil']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un profil spécifique.
        """
        profil = self.profil_service.get_by_id(pk)
        if not profil:
            return Response(
                {'error': 'Profil non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(profil)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau profil",
        request_body=ProfilSerializer,
        responses={
            201: ProfilSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Profil']
    )
    def create(self, request):
        """
        Crée un nouveau profil.
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
            profil = self.profil_service.create(data)
            serializer = self.get_serializer(profil)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un profil",
        request_body=ProfilSerializer,
        responses={
            200: ProfilSerializer,
            400: "Données invalides",
            404: "Profil non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Profil']
    )
    def update(self, request, pk=None):
        """
        Met à jour un profil existant.
        """
        try:
            data = request.data.copy()
            data = self._prepare_write_data(request)
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            profil = self.profil_service.update(pk, data)
            if profil is None:
                return Response(
                    {'error': 'Profil non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(profil)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un profil",
        request_body=ProfilSerializer,
        responses={
            200: ProfilSerializer,
            400: "Données invalides",
            404: "Profil non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Profil']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un profil existant.
        """
        try:
            data = request.data.copy()
            data = self._prepare_write_data(request)
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            profil = self.profil_service.update(pk, data, partial=True)
            if profil is None:
                return Response(
                    {'error': 'Profil non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(profil)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un profil",
        responses={
            204: "Profil supprimé avec succès",
            404: "Profil non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Profil']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un profil.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.profil_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Profil non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )