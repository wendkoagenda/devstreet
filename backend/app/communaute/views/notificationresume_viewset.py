"""
ViewSet pour la gestion des notification_resumes.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import NotificationResume
from app.communaute.serializers import NotificationResumeSerializer
from app.communaute.services.notificationresume_service import NotificationResumeService
from app.communaute.permissions.notificationresume_permissions import (
    CanViewNotificationResume,
    CanCreateNotificationResume,
    CanUpdateNotificationResume,
    CanDeleteNotificationResume
)


class NotificationResumeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les notification_resumes.
    """
    swagger_tags = ['V1 - NotificationResume']
    queryset = NotificationResume.objects.all()
    serializer_class = NotificationResumeSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notificationresume_service = NotificationResumeService()

    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action in ('actuel', 'lire'):
            permission_classes = [IsAuthenticated]
        elif self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewNotificationResume]
        elif self.action == 'create':
            permission_classes = [CanCreateNotificationResume]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateNotificationResume]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteNotificationResume]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description=(
            "Résumé quotidien non lu du membre connecté "
            "(génère celui d'hier si besoin)."
        ),
        responses={200: NotificationResumeSerializer, 204: "Aucun résumé"},
        security=[{'Bearer': []}],
        tags=['V1 - NotificationResume'],
    )
    @action(detail=False, methods=['get'], url_path='actuel')
    def actuel(self, request):
        resume = self.notificationresume_service.get_actuel_non_lu(
            membre=request.user
        )
        if resume is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self.get_serializer(resume).data)

    @swagger_auto_schema(
        operation_description="Marquer un résumé quotidien comme lu.",
        responses={
            200: NotificationResumeSerializer,
            400: "Données invalides",
            404: "Résumé introuvable",
        },
        security=[{'Bearer': []}],
        tags=['V1 - NotificationResume'],
    )
    @action(detail=True, methods=['post'], url_path='lire')
    def lire(self, request, pk=None):
        try:
            resume = self.notificationresume_service.mark_read(
                resume_id=int(pk), membre=request.user
            )
        except ValidationError as exc:
            return Response(
                {'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.get_serializer(resume).data)

    @swagger_auto_schema(
        operation_description="Lister les notification_resumes (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: NotificationResumeSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - NotificationResume']
    )
    def list(self, request):
        """
        Retourne une page de notification_resumes (format : count, next, previous, results).
        """
        try:
            notification_resumes = self.notificationresume_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(notification_resumes)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un notification_resume par son ID",
        responses={
            200: NotificationResumeSerializer,
            404: "NotificationResume non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - NotificationResume']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un notification_resume spécifique.
        """
        notification_resume = self.notificationresume_service.get_by_id(pk)
        if not notification_resume:
            return Response(
                {'error': 'NotificationResume non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(notification_resume)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau notification_resume",
        request_body=NotificationResumeSerializer,
        responses={
            201: NotificationResumeSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - NotificationResume']
    )
    def create(self, request):
        """
        Crée un nouveau notification_resume.
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
            if 'destinataire' in data and 'destinataire_id' not in data:
                data['destinataire_id'] = data.pop('destinataire')
            notification_resume = self.notificationresume_service.create(data)
            serializer = self.get_serializer(notification_resume)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un notification_resume",
        request_body=NotificationResumeSerializer,
        responses={
            200: NotificationResumeSerializer,
            400: "Données invalides",
            404: "NotificationResume non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - NotificationResume']
    )
    def update(self, request, pk=None):
        """
        Met à jour un notification_resume existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            notification_resume = self.notificationresume_service.update(pk, data)
            if notification_resume is None:
                return Response(
                    {'error': 'NotificationResume non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(notification_resume)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un notification_resume",
        request_body=NotificationResumeSerializer,
        responses={
            200: NotificationResumeSerializer,
            400: "Données invalides",
            404: "NotificationResume non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - NotificationResume']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un notification_resume existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            notification_resume = self.notificationresume_service.update(pk, data, partial=True)
            if notification_resume is None:
                return Response(
                    {'error': 'NotificationResume non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(notification_resume)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un notification_resume",
        responses={
            204: "NotificationResume supprimé avec succès",
            404: "NotificationResume non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - NotificationResume']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un notification_resume.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.notificationresume_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'NotificationResume non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )