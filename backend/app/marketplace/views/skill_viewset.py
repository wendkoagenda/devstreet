"""
ViewSet pour la gestion des skills.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import Skill
from app.marketplace.serializers import SkillSerializer
from app.marketplace.services.skill_service import SkillService
from app.marketplace.permissions.skill_permissions import (
    CanViewSkill,
    CanCreateSkill,
    CanUpdateSkill,
    CanDeleteSkill
)


class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les skills.
    """
    swagger_tags = ['V1 - Skill']
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skill_service = SkillService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewSkill]
        elif self.action == 'create':
            permission_classes = [CanCreateSkill]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateSkill]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteSkill]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les skills (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: SkillSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Skill']
    )
    def list(self, request):
        """
        Retourne une page de skills (format : count, next, previous, results).
        """
        try:
            skills = self.skill_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(skills)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un skill par son ID",
        responses={
            200: SkillSerializer,
            404: "Skill non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Skill']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un skill spécifique.
        """
        skill = self.skill_service.get_by_id(pk)
        if not skill:
            return Response(
                {'error': 'Skill non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(skill)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau skill",
        request_body=SkillSerializer,
        responses={
            201: SkillSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Skill']
    )
    def create(self, request):
        """
        Crée un nouveau skill.
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
            skill = self.skill_service.create(data)
            serializer = self.get_serializer(skill)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un skill",
        request_body=SkillSerializer,
        responses={
            200: SkillSerializer,
            400: "Données invalides",
            404: "Skill non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Skill']
    )
    def update(self, request, pk=None):
        """
        Met à jour un skill existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            skill = self.skill_service.update(pk, data)
            if skill is None:
                return Response(
                    {'error': 'Skill non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(skill)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un skill",
        request_body=SkillSerializer,
        responses={
            200: SkillSerializer,
            400: "Données invalides",
            404: "Skill non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Skill']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un skill existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            skill = self.skill_service.update(pk, data, partial=True)
            if skill is None:
                return Response(
                    {'error': 'Skill non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(skill)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un skill",
        responses={
            204: "Skill supprimé avec succès",
            404: "Skill non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Skill']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un skill.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.skill_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Skill non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )