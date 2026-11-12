"""
ViewSet pour la gestion des suivi_utilisateurs.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import SuiviUtilisateur
from app.communaute.serializers import SuiviUtilisateurSerializer
from app.communaute.services.suiviutilisateur_service import SuiviUtilisateurService
from app.communaute.permissions.suiviutilisateur_permissions import (
    CanViewSuiviUtilisateur,
    CanCreateSuiviUtilisateur,
    CanUpdateSuiviUtilisateur,
    CanDeleteSuiviUtilisateur
)


class SuiviUtilisateurViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les suivi_utilisateurs.
    """
    swagger_tags = ['V1 - SuiviUtilisateur']
    queryset = SuiviUtilisateur.objects.all()
    serializer_class = SuiviUtilisateurSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suiviutilisateur_service = SuiviUtilisateurService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewSuiviUtilisateur]
        elif self.action == 'create':
            permission_classes = [CanCreateSuiviUtilisateur]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateSuiviUtilisateur]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteSuiviUtilisateur]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les suivi_utilisateurs (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: SuiviUtilisateurSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - SuiviUtilisateur']
    )
    def list(self, request):
        """
        Retourne une page de suivi_utilisateurs (format : count, next, previous, results).
        """
        try:
            suivi_utilisateurs = self.suiviutilisateur_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(suivi_utilisateurs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un suivi_utilisateur par son ID",
        responses={
            200: SuiviUtilisateurSerializer,
            404: "SuiviUtilisateur non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - SuiviUtilisateur']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un suivi_utilisateur spécifique.
        """
        suivi_utilisateur = self.suiviutilisateur_service.get_by_id(pk)
        if not suivi_utilisateur:
            return Response(
                {'error': 'SuiviUtilisateur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(suivi_utilisateur)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau suivi_utilisateur",
        request_body=SuiviUtilisateurSerializer,
        responses={
            201: SuiviUtilisateurSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - SuiviUtilisateur']
    )
    def create(self, request):
        """
        Crée un nouveau suivi_utilisateur.
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
            suivi_utilisateur = self.suiviutilisateur_service.create(data)
            serializer = self.get_serializer(suivi_utilisateur)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un suivi_utilisateur",
        request_body=SuiviUtilisateurSerializer,
        responses={
            200: SuiviUtilisateurSerializer,
            400: "Données invalides",
            404: "SuiviUtilisateur non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - SuiviUtilisateur']
    )
    def update(self, request, pk=None):
        """
        Met à jour un suivi_utilisateur existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            suivi_utilisateur = self.suiviutilisateur_service.update(pk, data)
            if suivi_utilisateur is None:
                return Response(
                    {'error': 'SuiviUtilisateur non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(suivi_utilisateur)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un suivi_utilisateur",
        request_body=SuiviUtilisateurSerializer,
        responses={
            200: SuiviUtilisateurSerializer,
            400: "Données invalides",
            404: "SuiviUtilisateur non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - SuiviUtilisateur']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un suivi_utilisateur existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            suivi_utilisateur = self.suiviutilisateur_service.update(pk, data, partial=True)
            if suivi_utilisateur is None:
                return Response(
                    {'error': 'SuiviUtilisateur non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(suivi_utilisateur)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un suivi_utilisateur",
        responses={
            204: "SuiviUtilisateur supprimé avec succès",
            404: "SuiviUtilisateur non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - SuiviUtilisateur']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un suivi_utilisateur.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.suiviutilisateur_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'SuiviUtilisateur non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )