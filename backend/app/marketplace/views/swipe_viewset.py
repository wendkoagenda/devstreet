"""
ViewSet pour la gestion des swipes.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import Swipe
from app.marketplace.serializers import SwipeSerializer
from app.marketplace.services.swipe_service import SwipeService
from app.marketplace.permissions.swipe_permissions import (
    CanViewSwipe,
    CanCreateSwipe,
    CanUpdateSwipe,
    CanDeleteSwipe
)


class SwipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les swipes.
    """
    swagger_tags = ['V1 - Swipe']
    queryset = Swipe.objects.all()
    serializer_class = SwipeSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.swipe_service = SwipeService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewSwipe]
        elif self.action == 'create':
            permission_classes = [CanCreateSwipe]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateSwipe]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteSwipe]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les swipes (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: SwipeSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Swipe']
    )
    def list(self, request):
        """
        Retourne une page de swipes (format : count, next, previous, results).
        """
        try:
            swipes = self.swipe_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(swipes)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un swipe par son ID",
        responses={
            200: SwipeSerializer,
            404: "Swipe non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Swipe']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un swipe spécifique.
        """
        swipe = self.swipe_service.get_by_id(pk)
        if not swipe:
            return Response(
                {'error': 'Swipe non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(swipe)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau swipe",
        request_body=SwipeSerializer,
        responses={
            201: SwipeSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Swipe']
    )
    def create(self, request):
        """
        Crée un nouveau swipe.
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
            swipe = self.swipe_service.create(data)
            serializer = self.get_serializer(swipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un swipe",
        request_body=SwipeSerializer,
        responses={
            200: SwipeSerializer,
            400: "Données invalides",
            404: "Swipe non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Swipe']
    )
    def update(self, request, pk=None):
        """
        Met à jour un swipe existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            swipe = self.swipe_service.update(pk, data)
            if swipe is None:
                return Response(
                    {'error': 'Swipe non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(swipe)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un swipe",
        request_body=SwipeSerializer,
        responses={
            200: SwipeSerializer,
            400: "Données invalides",
            404: "Swipe non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Swipe']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un swipe existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            swipe = self.swipe_service.update(pk, data, partial=True)
            if swipe is None:
                return Response(
                    {'error': 'Swipe non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(swipe)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un swipe",
        responses={
            204: "Swipe supprimé avec succès",
            404: "Swipe non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Swipe']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un swipe.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.swipe_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Swipe non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )