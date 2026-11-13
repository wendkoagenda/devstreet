"""
ViewSet pour la gestion des like_publications.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import LikePublication
from app.communaute.serializers import LikePublicationSerializer
from app.communaute.services.likepublication_service import LikePublicationService
from app.communaute.permissions.likepublication_permissions import (
    CanViewLikePublication,
    CanCreateLikePublication,
    CanUpdateLikePublication,
    CanDeleteLikePublication
)


class LikePublicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les like_publications.
    """
    swagger_tags = ['V1 - LikePublication']
    queryset = LikePublication.objects.all()
    serializer_class = LikePublicationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.likepublication_service = LikePublicationService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewLikePublication]
        elif self.action == 'create':
            permission_classes = [CanCreateLikePublication]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateLikePublication]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteLikePublication]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les like_publications (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: LikePublicationSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - LikePublication']
    )
    def list(self, request):
        """
        Retourne une page de like_publications (format : count, next, previous, results).
        """
        try:
            like_publications = self.likepublication_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(like_publications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un like_publication par son ID",
        responses={
            200: LikePublicationSerializer,
            404: "LikePublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikePublication']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un like_publication spécifique.
        """
        like_publication = self.likepublication_service.get_by_id(pk)
        if not like_publication:
            return Response(
                {'error': 'LikePublication non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(like_publication)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau like_publication",
        request_body=LikePublicationSerializer,
        responses={
            201: LikePublicationSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikePublication']
    )
    def create(self, request):
        """
        Crée un nouveau like_publication.
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
            like_publication = self.likepublication_service.create(data)
            serializer = self.get_serializer(like_publication)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un like_publication",
        request_body=LikePublicationSerializer,
        responses={
            200: LikePublicationSerializer,
            400: "Données invalides",
            404: "LikePublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikePublication']
    )
    def update(self, request, pk=None):
        """
        Met à jour un like_publication existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            like_publication = self.likepublication_service.update(pk, data)
            if like_publication is None:
                return Response(
                    {'error': 'LikePublication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(like_publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un like_publication",
        request_body=LikePublicationSerializer,
        responses={
            200: LikePublicationSerializer,
            400: "Données invalides",
            404: "LikePublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikePublication']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un like_publication existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            like_publication = self.likepublication_service.update(pk, data, partial=True)
            if like_publication is None:
                return Response(
                    {'error': 'LikePublication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(like_publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un like_publication",
        responses={
            204: "LikePublication supprimé avec succès",
            404: "LikePublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikePublication']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un like_publication.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.likepublication_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'LikePublication non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )