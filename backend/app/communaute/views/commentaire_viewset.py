"""
ViewSet pour la gestion des commentaires.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import Commentaire
from app.communaute.serializers import CommentaireSerializer
from app.communaute.services.commentaire_service import CommentaireService
from app.communaute.permissions.commentaire_permissions import (
    CanViewCommentaire,
    CanCreateCommentaire,
    CanUpdateCommentaire,
    CanDeleteCommentaire
)


class CommentaireViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les commentaires.
    """
    swagger_tags = ['V1 - Commentaire']
    queryset = Commentaire.objects.all()
    serializer_class = CommentaireSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commentaire_service = CommentaireService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewCommentaire]
        elif self.action == 'create':
            permission_classes = [CanCreateCommentaire]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateCommentaire]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteCommentaire]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les commentaires (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: CommentaireSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Commentaire']
    )
    def list(self, request):
        """
        Retourne une page de commentaires (format : count, next, previous, results).
        """
        try:
            commentaires = self.commentaire_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(commentaires)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un commentaire par son ID",
        responses={
            200: CommentaireSerializer,
            404: "Commentaire non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Commentaire']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un commentaire spécifique.
        """
        commentaire = self.commentaire_service.get_by_id(pk)
        if not commentaire:
            return Response(
                {'error': 'Commentaire non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(commentaire)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau commentaire",
        request_body=CommentaireSerializer,
        responses={
            201: CommentaireSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Commentaire']
    )
    def create(self, request):
        """
        Crée un nouveau commentaire.
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
            commentaire = self.commentaire_service.create(data)
            serializer = self.get_serializer(commentaire)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un commentaire",
        request_body=CommentaireSerializer,
        responses={
            200: CommentaireSerializer,
            400: "Données invalides",
            404: "Commentaire non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Commentaire']
    )
    def update(self, request, pk=None):
        """
        Met à jour un commentaire existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            commentaire = self.commentaire_service.update(pk, data)
            if commentaire is None:
                return Response(
                    {'error': 'Commentaire non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(commentaire)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un commentaire",
        request_body=CommentaireSerializer,
        responses={
            200: CommentaireSerializer,
            400: "Données invalides",
            404: "Commentaire non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Commentaire']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un commentaire existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            commentaire = self.commentaire_service.update(pk, data, partial=True)
            if commentaire is None:
                return Response(
                    {'error': 'Commentaire non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(commentaire)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un commentaire",
        responses={
            204: "Commentaire supprimé avec succès",
            404: "Commentaire non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Commentaire']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un commentaire.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.commentaire_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Commentaire non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )