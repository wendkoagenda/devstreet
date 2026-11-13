"""
ViewSet pour la gestion des participation_espaces.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import ParticipationEspace
from app.communaute.serializers import ParticipationEspaceSerializer
from app.communaute.services.participationespace_service import ParticipationEspaceService
from app.communaute.permissions.participationespace_permissions import (
    CanViewParticipationEspace,
    CanCreateParticipationEspace,
    CanUpdateParticipationEspace,
    CanDeleteParticipationEspace
)


class ParticipationEspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les participation_espaces.
    """
    swagger_tags = ['V1 - ParticipationEspace']
    queryset = ParticipationEspace.objects.all()
    serializer_class = ParticipationEspaceSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.participationespace_service = ParticipationEspaceService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewParticipationEspace]
        elif self.action == 'create':
            permission_classes = [CanCreateParticipationEspace]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateParticipationEspace]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteParticipationEspace]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les participation_espaces (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ParticipationEspaceSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - ParticipationEspace']
    )
    def list(self, request):
        """
        Retourne une page de participation_espaces (format : count, next, previous, results).
        """
        try:
            participation_espaces = self.participationespace_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(participation_espaces)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un participation_espace par son ID",
        responses={
            200: ParticipationEspaceSerializer,
            404: "ParticipationEspace non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ParticipationEspace']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un participation_espace spécifique.
        """
        participation_espace = self.participationespace_service.get_by_id(pk)
        if not participation_espace:
            return Response(
                {'error': 'ParticipationEspace non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(participation_espace)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau participation_espace",
        request_body=ParticipationEspaceSerializer,
        responses={
            201: ParticipationEspaceSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ParticipationEspace']
    )
    def create(self, request):
        """
        Crée un nouveau participation_espace.
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
            participation_espace = self.participationespace_service.create(data)
            serializer = self.get_serializer(participation_espace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un participation_espace",
        request_body=ParticipationEspaceSerializer,
        responses={
            200: ParticipationEspaceSerializer,
            400: "Données invalides",
            404: "ParticipationEspace non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ParticipationEspace']
    )
    def update(self, request, pk=None):
        """
        Met à jour un participation_espace existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            participation_espace = self.participationespace_service.update(pk, data)
            if participation_espace is None:
                return Response(
                    {'error': 'ParticipationEspace non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(participation_espace)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un participation_espace",
        request_body=ParticipationEspaceSerializer,
        responses={
            200: ParticipationEspaceSerializer,
            400: "Données invalides",
            404: "ParticipationEspace non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ParticipationEspace']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un participation_espace existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            participation_espace = self.participationespace_service.update(pk, data, partial=True)
            if participation_espace is None:
                return Response(
                    {'error': 'ParticipationEspace non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(participation_espace)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un participation_espace",
        responses={
            204: "ParticipationEspace supprimé avec succès",
            404: "ParticipationEspace non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ParticipationEspace']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un participation_espace.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.participationespace_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'ParticipationEspace non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )