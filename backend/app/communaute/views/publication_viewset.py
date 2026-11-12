"""
ViewSet pour la gestion des publications.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import Publication
from app.communaute.serializers import PublicationSerializer
from app.communaute.services.publication_service import PublicationService
from app.communaute.permissions.publication_permissions import (
    CanViewPublication,
    CanCreatePublication,
    CanUpdatePublication,
    CanDeletePublication
)


class PublicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les publications.
    """
    swagger_tags = ['V1 - Publication']
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publication_service = PublicationService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewPublication]
        elif self.action == 'create':
            permission_classes = [CanCreatePublication]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdatePublication]
        elif self.action == 'destroy':
            permission_classes = [CanDeletePublication]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les publications (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: PublicationSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def list(self, request):
        """
        Retourne une page de publications (format : count, next, previous, results).
        """
        try:
            publications = self.publication_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(publications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un publication par son ID",
        responses={
            200: PublicationSerializer,
            404: "Publication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un publication spécifique.
        """
        publication = self.publication_service.get_by_id(pk)
        if not publication:
            return Response(
                {'error': 'Publication non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(publication)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau publication",
        request_body=PublicationSerializer,
        responses={
            201: PublicationSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def create(self, request):
        """
        Crée un nouveau publication.
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
            publication = self.publication_service.create(data)
            serializer = self.get_serializer(publication)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un publication",
        request_body=PublicationSerializer,
        responses={
            200: PublicationSerializer,
            400: "Données invalides",
            404: "Publication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def update(self, request, pk=None):
        """
        Met à jour un publication existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            publication = self.publication_service.update(pk, data)
            if publication is None:
                return Response(
                    {'error': 'Publication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un publication",
        request_body=PublicationSerializer,
        responses={
            200: PublicationSerializer,
            400: "Données invalides",
            404: "Publication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un publication existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            publication = self.publication_service.update(pk, data, partial=True)
            if publication is None:
                return Response(
                    {'error': 'Publication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un publication",
        responses={
            204: "Publication supprimé avec succès",
            404: "Publication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un publication.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.publication_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Publication non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )