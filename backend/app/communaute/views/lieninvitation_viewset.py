"""
ViewSet pour la gestion des lien_invitations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import LienInvitation
from app.communaute.serializers import LienInvitationSerializer
from app.communaute.services.lieninvitation_service import LienInvitationService
from app.communaute.permissions.lieninvitation_permissions import (
    CanViewLienInvitation,
    CanCreateLienInvitation,
    CanUpdateLienInvitation,
    CanDeleteLienInvitation
)


class LienInvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les lien_invitations.
    """
    swagger_tags = ['V1 - LienInvitation']
    queryset = LienInvitation.objects.all()
    serializer_class = LienInvitationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lieninvitation_service = LienInvitationService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewLienInvitation]
        elif self.action == 'create':
            permission_classes = [CanCreateLienInvitation]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateLienInvitation]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteLienInvitation]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les lien_invitations (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: LienInvitationSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - LienInvitation']
    )
    def list(self, request):
        """
        Retourne une page de lien_invitations (format : count, next, previous, results).
        """
        try:
            lien_invitations = self.lieninvitation_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(lien_invitations)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un lien_invitation par son ID",
        responses={
            200: LienInvitationSerializer,
            404: "LienInvitation non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LienInvitation']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un lien_invitation spécifique.
        """
        lien_invitation = self.lieninvitation_service.get_by_id(pk)
        if not lien_invitation:
            return Response(
                {'error': 'LienInvitation non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(lien_invitation)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau lien_invitation",
        request_body=LienInvitationSerializer,
        responses={
            201: LienInvitationSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LienInvitation']
    )
    def create(self, request):
        """
        Crée un nouveau lien_invitation.
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
            lien_invitation = self.lieninvitation_service.create(data)
            serializer = self.get_serializer(lien_invitation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un lien_invitation",
        request_body=LienInvitationSerializer,
        responses={
            200: LienInvitationSerializer,
            400: "Données invalides",
            404: "LienInvitation non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LienInvitation']
    )
    def update(self, request, pk=None):
        """
        Met à jour un lien_invitation existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            lien_invitation = self.lieninvitation_service.update(pk, data)
            if lien_invitation is None:
                return Response(
                    {'error': 'LienInvitation non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(lien_invitation)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un lien_invitation",
        request_body=LienInvitationSerializer,
        responses={
            200: LienInvitationSerializer,
            400: "Données invalides",
            404: "LienInvitation non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LienInvitation']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un lien_invitation existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            lien_invitation = self.lieninvitation_service.update(pk, data, partial=True)
            if lien_invitation is None:
                return Response(
                    {'error': 'LienInvitation non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(lien_invitation)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un lien_invitation",
        responses={
            204: "LienInvitation supprimé avec succès",
            404: "LienInvitation non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LienInvitation']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un lien_invitation.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.lieninvitation_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'LienInvitation non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )