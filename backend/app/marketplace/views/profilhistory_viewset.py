"""
ViewSet pour la gestion des profil_historys.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import ProfilHistory
from app.marketplace.serializers import ProfilHistorySerializer
from app.marketplace.services.profilhistory_service import ProfilHistoryService
from app.marketplace.permissions.profilhistory_permissions import (
    CanViewProfilHistory,
    CanCreateProfilHistory,
    CanUpdateProfilHistory,
    CanDeleteProfilHistory
)


class ProfilHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les profil_historys.
    """
    swagger_tags = ['V1 - ProfilHistory']
    queryset = ProfilHistory.objects.all()
    serializer_class = ProfilHistorySerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profilhistory_service = ProfilHistoryService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewProfilHistory]
        elif self.action == 'create':
            permission_classes = [CanCreateProfilHistory]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateProfilHistory]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteProfilHistory]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les profil_historys (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ProfilHistorySerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - ProfilHistory']
    )
    def list(self, request):
        """
        Retourne une page de profil_historys (format : count, next, previous, results).
        """
        try:
            profil_historys = self.profilhistory_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(profil_historys)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un profil_history par son ID",
        responses={
            200: ProfilHistorySerializer,
            404: "ProfilHistory non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ProfilHistory']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un profil_history spécifique.
        """
        profil_history = self.profilhistory_service.get_by_id(pk)
        if not profil_history:
            return Response(
                {'error': 'ProfilHistory non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(profil_history)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau profil_history",
        request_body=ProfilHistorySerializer,
        responses={
            201: ProfilHistorySerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ProfilHistory']
    )
    def create(self, request):
        """
        Crée un nouveau profil_history.
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
            profil_history = self.profilhistory_service.create(data)
            serializer = self.get_serializer(profil_history)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un profil_history",
        request_body=ProfilHistorySerializer,
        responses={
            200: ProfilHistorySerializer,
            400: "Données invalides",
            404: "ProfilHistory non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ProfilHistory']
    )
    def update(self, request, pk=None):
        """
        Met à jour un profil_history existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            profil_history = self.profilhistory_service.update(pk, data)
            if profil_history is None:
                return Response(
                    {'error': 'ProfilHistory non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(profil_history)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un profil_history",
        request_body=ProfilHistorySerializer,
        responses={
            200: ProfilHistorySerializer,
            400: "Données invalides",
            404: "ProfilHistory non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ProfilHistory']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un profil_history existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            profil_history = self.profilhistory_service.update(pk, data, partial=True)
            if profil_history is None:
                return Response(
                    {'error': 'ProfilHistory non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(profil_history)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un profil_history",
        responses={
            204: "ProfilHistory supprimé avec succès",
            404: "ProfilHistory non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - ProfilHistory']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un profil_history.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.profilhistory_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'ProfilHistory non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )