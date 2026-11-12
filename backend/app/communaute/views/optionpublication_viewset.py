"""
ViewSet pour la gestion des option_publications.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import OptionPublication
from app.communaute.serializers import OptionPublicationSerializer
from app.communaute.services.optionpublication_service import OptionPublicationService
from app.communaute.permissions.optionpublication_permissions import (
    CanViewOptionPublication,
    CanCreateOptionPublication,
    CanUpdateOptionPublication,
    CanDeleteOptionPublication
)


class OptionPublicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les option_publications.
    """
    swagger_tags = ['V1 - OptionPublication']
    queryset = OptionPublication.objects.all()
    serializer_class = OptionPublicationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optionpublication_service = OptionPublicationService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewOptionPublication]
        elif self.action == 'create':
            permission_classes = [CanCreateOptionPublication]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateOptionPublication]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteOptionPublication]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les option_publications (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: OptionPublicationSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - OptionPublication']
    )
    def list(self, request):
        """
        Retourne une page de option_publications (format : count, next, previous, results).
        """
        try:
            option_publications = self.optionpublication_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(option_publications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un option_publication par son ID",
        responses={
            200: OptionPublicationSerializer,
            404: "OptionPublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - OptionPublication']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un option_publication spécifique.
        """
        option_publication = self.optionpublication_service.get_by_id(pk)
        if not option_publication:
            return Response(
                {'error': 'OptionPublication non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(option_publication)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau option_publication",
        request_body=OptionPublicationSerializer,
        responses={
            201: OptionPublicationSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - OptionPublication']
    )
    def create(self, request):
        """
        Crée un nouveau option_publication.
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
            option_publication = self.optionpublication_service.create(data)
            serializer = self.get_serializer(option_publication)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un option_publication",
        request_body=OptionPublicationSerializer,
        responses={
            200: OptionPublicationSerializer,
            400: "Données invalides",
            404: "OptionPublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - OptionPublication']
    )
    def update(self, request, pk=None):
        """
        Met à jour un option_publication existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            option_publication = self.optionpublication_service.update(pk, data)
            if option_publication is None:
                return Response(
                    {'error': 'OptionPublication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(option_publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un option_publication",
        request_body=OptionPublicationSerializer,
        responses={
            200: OptionPublicationSerializer,
            400: "Données invalides",
            404: "OptionPublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - OptionPublication']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un option_publication existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            option_publication = self.optionpublication_service.update(pk, data, partial=True)
            if option_publication is None:
                return Response(
                    {'error': 'OptionPublication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(option_publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un option_publication",
        responses={
            204: "OptionPublication supprimé avec succès",
            404: "OptionPublication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - OptionPublication']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un option_publication.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.optionpublication_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'OptionPublication non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )