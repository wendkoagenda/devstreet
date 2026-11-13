"""
ViewSet pour la gestion des image_publications.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import ImagePublication
from app.communaute.serializers import ImagePublicationSerializer
from app.communaute.services.imagepublication_service import ImagePublicationService
from app.communaute.permissions.imagepublication_permissions import (
    CanViewImagePublication,
    CanCreateImagePublication,
    CanUpdateImagePublication,
    CanDeleteImagePublication
)


class ImagePublicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les image_publications.
    """
    swagger_tags = ['V1 - ImagePublication']
    queryset = ImagePublication.objects.all()
    serializer_class = ImagePublicationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.imagepublication_service = ImagePublicationService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewImagePublication]
        elif self.action == 'create':
            permission_classes = [CanCreateImagePublication]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateImagePublication]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteImagePublication]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les image_publications (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ImagePublicationSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - ImagePublication']
    )
    def list(self, request):
        """
        Retourne une page de image_publications (format : count, next, previous, results).
        """
        try:
            image_publications = self.imagepublication_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(image_publications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un image_publication par son ID",
        responses={
            200: ImagePublicationSerializer,
            404: "ImagePublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ImagePublication']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un image_publication spécifique.
        """
        image_publication = self.imagepublication_service.get_by_id(pk)
        if not image_publication:
            return Response(
                {'error': 'ImagePublication non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(image_publication)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau image_publication",
        request_body=ImagePublicationSerializer,
        responses={
            201: ImagePublicationSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ImagePublication']
    )
    def create(self, request):
        """
        Crée un nouveau image_publication.
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
            image_publication = self.imagepublication_service.create(data)
            serializer = self.get_serializer(image_publication)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un image_publication",
        request_body=ImagePublicationSerializer,
        responses={
            200: ImagePublicationSerializer,
            400: "Données invalides",
            404: "ImagePublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ImagePublication']
    )
    def update(self, request, pk=None):
        """
        Met à jour un image_publication existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            image_publication = self.imagepublication_service.update(pk, data)
            if image_publication is None:
                return Response(
                    {'error': 'ImagePublication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(image_publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un image_publication",
        request_body=ImagePublicationSerializer,
        responses={
            200: ImagePublicationSerializer,
            400: "Données invalides",
            404: "ImagePublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ImagePublication']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un image_publication existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            image_publication = self.imagepublication_service.update(pk, data, partial=True)
            if image_publication is None:
                return Response(
                    {'error': 'ImagePublication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(image_publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un image_publication",
        responses={
            204: "ImagePublication supprimé avec succès",
            404: "ImagePublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ImagePublication']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un image_publication.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.imagepublication_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'ImagePublication non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )