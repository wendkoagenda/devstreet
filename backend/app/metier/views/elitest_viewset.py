"""
ViewSet pour la gestion des elitests.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.metier.models import Elitest
from app.metier.serializers import ElitestSerializer
from app.metier.services.elitest_service import ElitestService
from app.metier.permissions.elitest_permissions import (
    CanViewElitest,
    CanCreateElitest,
    CanUpdateElitest,
    CanDeleteElitest
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from app.metier.utils.file_field_utils import process_uploaded_files
from app.metier.utils.request_data_utils import flatten_request_data


class ElitestViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les elitests.
    """
    swagger_tags = ['V1 - Elitest']
    queryset = Elitest.objects.all()
    serializer_class = ElitestSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    FILE_FIELD_CONFIG = {
        "document": {
            "upload_folder": "elitest_documents",
            "allowed_extensions": ['.pdf', '.png'],
            "max_size_mb": 5,
        },
    }
    FILE_FIELD_NAMES = ["document"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elitest_service = ElitestService()

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
            permission_classes = [CanViewElitest]
        elif self.action == 'create':
            permission_classes = [CanCreateElitest]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateElitest]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteElitest]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les elitests (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ElitestSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Elitest']
    )
    def list(self, request):
        """
        Retourne une page de elitests (format : count, next, previous, results).
        """
        try:
            elitests = self.elitest_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(elitests)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un elitest par son ID",
        responses={
            200: ElitestSerializer,
            404: "Elitest non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Elitest']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un elitest spécifique.
        """
        elitest = self.elitest_service.get_by_id(pk)
        if not elitest:
            return Response(
                {'error': 'Elitest non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(elitest)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau elitest",
        request_body=ElitestSerializer,
        responses={
            201: ElitestSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Elitest']
    )
    def create(self, request):
        """
        Crée un nouveau elitest.
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
            elitest = self.elitest_service.create(data)
            serializer = self.get_serializer(elitest)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un elitest",
        request_body=ElitestSerializer,
        responses={
            200: ElitestSerializer,
            400: "Données invalides",
            404: "Elitest non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Elitest']
    )
    def update(self, request, pk=None):
        """
        Met à jour un elitest existant.
        """
        try:
            data = request.data.copy()
            data = self._prepare_write_data(request)
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            elitest = self.elitest_service.update(pk, data)
            if elitest is None:
                return Response(
                    {'error': 'Elitest non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(elitest)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un elitest",
        request_body=ElitestSerializer,
        responses={
            200: ElitestSerializer,
            400: "Données invalides",
            404: "Elitest non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Elitest']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un elitest existant.
        """
        try:
            data = request.data.copy()
            data = self._prepare_write_data(request)
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            elitest = self.elitest_service.update(pk, data, partial=True)
            if elitest is None:
                return Response(
                    {'error': 'Elitest non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(elitest)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un elitest",
        responses={
            204: "Elitest supprimé avec succès",
            404: "Elitest non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Elitest']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un elitest.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.elitest_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Elitest non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )