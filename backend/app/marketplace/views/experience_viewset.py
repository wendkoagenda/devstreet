"""
ViewSet pour la gestion des experiences.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import Experience
from app.marketplace.serializers import ExperienceSerializer
from app.marketplace.services.experience_service import ExperienceService
from app.marketplace.permissions.experience_permissions import (
    CanViewExperience,
    CanCreateExperience,
    CanUpdateExperience,
    CanDeleteExperience
)


class ExperienceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les experiences.
    """
    swagger_tags = ['V1 - Experience']
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.experience_service = ExperienceService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewExperience]
        elif self.action == 'create':
            permission_classes = [CanCreateExperience]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateExperience]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteExperience]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les experiences (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ExperienceSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Experience']
    )
    def list(self, request):
        """
        Retourne une page de experiences (format : count, next, previous, results).
        """
        try:
            experiences = self.experience_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(experiences)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un experience par son ID",
        responses={
            200: ExperienceSerializer,
            404: "Experience non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Experience']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un experience spécifique.
        """
        experience = self.experience_service.get_by_id(pk)
        if not experience:
            return Response(
                {'error': 'Experience non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(experience)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau experience",
        request_body=ExperienceSerializer,
        responses={
            201: ExperienceSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Experience']
    )
    def create(self, request):
        """
        Crée un nouveau experience.
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
            experience = self.experience_service.create(data)
            serializer = self.get_serializer(experience)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un experience",
        request_body=ExperienceSerializer,
        responses={
            200: ExperienceSerializer,
            400: "Données invalides",
            404: "Experience non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Experience']
    )
    def update(self, request, pk=None):
        """
        Met à jour un experience existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            experience = self.experience_service.update(pk, data)
            if experience is None:
                return Response(
                    {'error': 'Experience non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(experience)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un experience",
        request_body=ExperienceSerializer,
        responses={
            200: ExperienceSerializer,
            400: "Données invalides",
            404: "Experience non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Experience']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un experience existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            experience = self.experience_service.update(pk, data, partial=True)
            if experience is None:
                return Response(
                    {'error': 'Experience non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(experience)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un experience",
        responses={
            204: "Experience supprimé avec succès",
            404: "Experience non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Experience']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un experience.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.experience_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Experience non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )