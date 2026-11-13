"""
ViewSet pour la gestion des like_commentaires.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import LikeCommentaire
from app.communaute.serializers import LikeCommentaireSerializer
from app.communaute.services.likecommentaire_service import LikeCommentaireService
from app.communaute.permissions.likecommentaire_permissions import (
    CanViewLikeCommentaire,
    CanCreateLikeCommentaire,
    CanUpdateLikeCommentaire,
    CanDeleteLikeCommentaire
)


class LikeCommentaireViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les like_commentaires.
    """
    swagger_tags = ['V1 - LikeCommentaire']
    queryset = LikeCommentaire.objects.all()
    serializer_class = LikeCommentaireSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.likecommentaire_service = LikeCommentaireService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewLikeCommentaire]
        elif self.action == 'create':
            permission_classes = [CanCreateLikeCommentaire]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateLikeCommentaire]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteLikeCommentaire]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les like_commentaires (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: LikeCommentaireSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - LikeCommentaire']
    )
    def list(self, request):
        """
        Retourne une page de like_commentaires (format : count, next, previous, results).
        """
        try:
            like_commentaires = self.likecommentaire_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(like_commentaires)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un like_commentaire par son ID",
        responses={
            200: LikeCommentaireSerializer,
            404: "LikeCommentaire non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikeCommentaire']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un like_commentaire spécifique.
        """
        like_commentaire = self.likecommentaire_service.get_by_id(pk)
        if not like_commentaire:
            return Response(
                {'error': 'LikeCommentaire non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(like_commentaire)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau like_commentaire",
        request_body=LikeCommentaireSerializer,
        responses={
            201: LikeCommentaireSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikeCommentaire']
    )
    def create(self, request):
        """
        Crée un nouveau like_commentaire.
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
            like_commentaire = self.likecommentaire_service.create(data)
            serializer = self.get_serializer(like_commentaire)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un like_commentaire",
        request_body=LikeCommentaireSerializer,
        responses={
            200: LikeCommentaireSerializer,
            400: "Données invalides",
            404: "LikeCommentaire non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikeCommentaire']
    )
    def update(self, request, pk=None):
        """
        Met à jour un like_commentaire existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            like_commentaire = self.likecommentaire_service.update(pk, data)
            if like_commentaire is None:
                return Response(
                    {'error': 'LikeCommentaire non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(like_commentaire)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un like_commentaire",
        request_body=LikeCommentaireSerializer,
        responses={
            200: LikeCommentaireSerializer,
            400: "Données invalides",
            404: "LikeCommentaire non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikeCommentaire']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un like_commentaire existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            like_commentaire = self.likecommentaire_service.update(pk, data, partial=True)
            if like_commentaire is None:
                return Response(
                    {'error': 'LikeCommentaire non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(like_commentaire)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un like_commentaire",
        responses={
            204: "LikeCommentaire supprimé avec succès",
            404: "LikeCommentaire non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - LikeCommentaire']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un like_commentaire.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.likecommentaire_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'LikeCommentaire non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )