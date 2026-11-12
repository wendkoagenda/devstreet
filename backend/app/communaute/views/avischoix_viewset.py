"""
ViewSet pour la gestion des avis_choixs.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import AvisChoix
from app.communaute.serializers import AvisChoixSerializer
from app.communaute.services.avischoix_service import AvisChoixService
from app.communaute.permissions.avischoix_permissions import (
    CanViewAvisChoix,
    CanCreateAvisChoix,
    CanUpdateAvisChoix,
    CanDeleteAvisChoix
)


class AvisChoixViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les avis_choixs.
    """
    swagger_tags = ['V1 - AvisChoix']
    queryset = AvisChoix.objects.all()
    serializer_class = AvisChoixSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.avischoix_service = AvisChoixService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewAvisChoix]
        elif self.action == 'create':
            permission_classes = [CanCreateAvisChoix]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateAvisChoix]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteAvisChoix]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les avis_choixs (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: AvisChoixSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - AvisChoix']
    )
    def list(self, request):
        """
        Retourne une page de avis_choixs (format : count, next, previous, results).
        """
        try:
            avis_choixs = self.avischoix_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(avis_choixs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un avis_choix par son ID",
        responses={
            200: AvisChoixSerializer,
            404: "AvisChoix non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - AvisChoix']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un avis_choix spécifique.
        """
        avis_choix = self.avischoix_service.get_by_id(pk)
        if not avis_choix:
            return Response(
                {'error': 'AvisChoix non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(avis_choix)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau avis_choix",
        request_body=AvisChoixSerializer,
        responses={
            201: AvisChoixSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - AvisChoix']
    )
    def create(self, request):
        """
        Crée un nouveau avis_choix.
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
            avis_choix = self.avischoix_service.create(data)
            serializer = self.get_serializer(avis_choix)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un avis_choix",
        request_body=AvisChoixSerializer,
        responses={
            200: AvisChoixSerializer,
            400: "Données invalides",
            404: "AvisChoix non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - AvisChoix']
    )
    def update(self, request, pk=None):
        """
        Met à jour un avis_choix existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            avis_choix = self.avischoix_service.update(pk, data)
            if avis_choix is None:
                return Response(
                    {'error': 'AvisChoix non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(avis_choix)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un avis_choix",
        request_body=AvisChoixSerializer,
        responses={
            200: AvisChoixSerializer,
            400: "Données invalides",
            404: "AvisChoix non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - AvisChoix']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un avis_choix existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            avis_choix = self.avischoix_service.update(pk, data, partial=True)
            if avis_choix is None:
                return Response(
                    {'error': 'AvisChoix non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(avis_choix)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un avis_choix",
        responses={
            204: "AvisChoix supprimé avec succès",
            404: "AvisChoix non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - AvisChoix']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un avis_choix.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.avischoix_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'AvisChoix non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )