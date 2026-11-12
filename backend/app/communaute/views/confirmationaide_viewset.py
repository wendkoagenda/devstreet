"""
ViewSet pour la gestion des confirmation_aides.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import ConfirmationAide
from app.communaute.serializers import ConfirmationAideSerializer
from app.communaute.services.confirmationaide_service import ConfirmationAideService
from app.communaute.permissions.confirmationaide_permissions import (
    CanViewConfirmationAide,
    CanCreateConfirmationAide,
    CanUpdateConfirmationAide,
    CanDeleteConfirmationAide
)


class ConfirmationAideViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les confirmation_aides.
    """
    swagger_tags = ['V1 - ConfirmationAide']
    queryset = ConfirmationAide.objects.all()
    serializer_class = ConfirmationAideSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirmationaide_service = ConfirmationAideService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewConfirmationAide]
        elif self.action == 'create':
            permission_classes = [CanCreateConfirmationAide]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateConfirmationAide]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteConfirmationAide]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les confirmation_aides (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ConfirmationAideSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - ConfirmationAide']
    )
    def list(self, request):
        """
        Retourne une page de confirmation_aides (format : count, next, previous, results).
        """
        try:
            confirmation_aides = self.confirmationaide_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(confirmation_aides)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un confirmation_aide par son ID",
        responses={
            200: ConfirmationAideSerializer,
            404: "ConfirmationAide non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ConfirmationAide']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un confirmation_aide spécifique.
        """
        confirmation_aide = self.confirmationaide_service.get_by_id(pk)
        if not confirmation_aide:
            return Response(
                {'error': 'ConfirmationAide non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(confirmation_aide)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau confirmation_aide",
        request_body=ConfirmationAideSerializer,
        responses={
            201: ConfirmationAideSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ConfirmationAide']
    )
    def create(self, request):
        """
        Crée un nouveau confirmation_aide.
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
            confirmation_aide = self.confirmationaide_service.create(data)
            serializer = self.get_serializer(confirmation_aide)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un confirmation_aide",
        request_body=ConfirmationAideSerializer,
        responses={
            200: ConfirmationAideSerializer,
            400: "Données invalides",
            404: "ConfirmationAide non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ConfirmationAide']
    )
    def update(self, request, pk=None):
        """
        Met à jour un confirmation_aide existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            confirmation_aide = self.confirmationaide_service.update(pk, data)
            if confirmation_aide is None:
                return Response(
                    {'error': 'ConfirmationAide non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(confirmation_aide)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un confirmation_aide",
        request_body=ConfirmationAideSerializer,
        responses={
            200: ConfirmationAideSerializer,
            400: "Données invalides",
            404: "ConfirmationAide non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ConfirmationAide']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un confirmation_aide existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            confirmation_aide = self.confirmationaide_service.update(pk, data, partial=True)
            if confirmation_aide is None:
                return Response(
                    {'error': 'ConfirmationAide non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(confirmation_aide)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un confirmation_aide",
        responses={
            204: "ConfirmationAide supprimé avec succès",
            404: "ConfirmationAide non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ConfirmationAide']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un confirmation_aide.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.confirmationaide_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'ConfirmationAide non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )