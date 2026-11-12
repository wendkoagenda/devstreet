"""
ViewSet pour la gestion des availabilitys.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import Availability
from app.marketplace.serializers import AvailabilitySerializer
from app.marketplace.services.availability_service import AvailabilityService
from app.marketplace.permissions.availability_permissions import (
    CanViewAvailability,
    CanCreateAvailability,
    CanUpdateAvailability,
    CanDeleteAvailability
)


class AvailabilityViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les availabilitys.
    """
    swagger_tags = ['V1 - Availability']
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.availability_service = AvailabilityService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewAvailability]
        elif self.action == 'create':
            permission_classes = [CanCreateAvailability]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateAvailability]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteAvailability]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les availabilitys (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: AvailabilitySerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Availability']
    )
    def list(self, request):
        """
        Retourne une page de availabilitys (format : count, next, previous, results).
        """
        try:
            availabilitys = self.availability_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(availabilitys)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un availability par son ID",
        responses={
            200: AvailabilitySerializer,
            404: "Availability non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Availability']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un availability spécifique.
        """
        availability = self.availability_service.get_by_id(pk)
        if not availability:
            return Response(
                {'error': 'Availability non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(availability)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau availability",
        request_body=AvailabilitySerializer,
        responses={
            201: AvailabilitySerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Availability']
    )
    def create(self, request):
        """
        Crée un nouveau availability.
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
            availability = self.availability_service.create(data)
            serializer = self.get_serializer(availability)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un availability",
        request_body=AvailabilitySerializer,
        responses={
            200: AvailabilitySerializer,
            400: "Données invalides",
            404: "Availability non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Availability']
    )
    def update(self, request, pk=None):
        """
        Met à jour un availability existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            availability = self.availability_service.update(pk, data)
            if availability is None:
                return Response(
                    {'error': 'Availability non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(availability)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un availability",
        request_body=AvailabilitySerializer,
        responses={
            200: AvailabilitySerializer,
            400: "Données invalides",
            404: "Availability non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Availability']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un availability existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            availability = self.availability_service.update(pk, data, partial=True)
            if availability is None:
                return Response(
                    {'error': 'Availability non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(availability)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un availability",
        responses={
            204: "Availability supprimé avec succès",
            404: "Availability non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Availability']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un availability.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.availability_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Availability non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )