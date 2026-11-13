"""
ViewSet pour la gestion des vote_sondages.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import VoteSondage
from app.communaute.serializers import VoteSondageSerializer
from app.communaute.services.votesondage_service import VoteSondageService
from app.communaute.permissions.votesondage_permissions import (
    CanViewVoteSondage,
    CanCreateVoteSondage,
    CanUpdateVoteSondage,
    CanDeleteVoteSondage
)


class VoteSondageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les vote_sondages.
    """
    swagger_tags = ['V1 - VoteSondage']
    queryset = VoteSondage.objects.all()
    serializer_class = VoteSondageSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.votesondage_service = VoteSondageService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewVoteSondage]
        elif self.action == 'create':
            permission_classes = [CanCreateVoteSondage]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateVoteSondage]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteVoteSondage]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les vote_sondages (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: VoteSondageSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - VoteSondage']
    )
    def list(self, request):
        """
        Retourne une page de vote_sondages (format : count, next, previous, results).
        """
        try:
            vote_sondages = self.votesondage_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(vote_sondages)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un vote_sondage par son ID",
        responses={
            200: VoteSondageSerializer,
            404: "VoteSondage non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - VoteSondage']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un vote_sondage spécifique.
        """
        vote_sondage = self.votesondage_service.get_by_id(pk)
        if not vote_sondage:
            return Response(
                {'error': 'VoteSondage non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(vote_sondage)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau vote_sondage",
        request_body=VoteSondageSerializer,
        responses={
            201: VoteSondageSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - VoteSondage']
    )
    def create(self, request):
        """
        Crée un nouveau vote_sondage.
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
            vote_sondage = self.votesondage_service.create(data)
            serializer = self.get_serializer(vote_sondage)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un vote_sondage",
        request_body=VoteSondageSerializer,
        responses={
            200: VoteSondageSerializer,
            400: "Données invalides",
            404: "VoteSondage non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - VoteSondage']
    )
    def update(self, request, pk=None):
        """
        Met à jour un vote_sondage existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            vote_sondage = self.votesondage_service.update(pk, data)
            if vote_sondage is None:
                return Response(
                    {'error': 'VoteSondage non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(vote_sondage)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un vote_sondage",
        request_body=VoteSondageSerializer,
        responses={
            200: VoteSondageSerializer,
            400: "Données invalides",
            404: "VoteSondage non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - VoteSondage']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un vote_sondage existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            vote_sondage = self.votesondage_service.update(pk, data, partial=True)
            if vote_sondage is None:
                return Response(
                    {'error': 'VoteSondage non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(vote_sondage)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un vote_sondage",
        responses={
            204: "VoteSondage supprimé avec succès",
            404: "VoteSondage non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - VoteSondage']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un vote_sondage.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.votesondage_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'VoteSondage non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )