"""
ViewSet pour la gestion des commentaires.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.communaute.models import Commentaire
from app.communaute.serializers import CommentaireSerializer
from app.communaute.services.commentaire_service import CommentaireService
from app.communaute.services.likecommentaire_service import LikeCommentaireService
from app.communaute.services.confirmationaide_service import ConfirmationAideService
from app.communaute.permissions.commentaire_permissions import (
    CanViewCommentaire,
    CanCreateCommentaire,
    CanUpdateCommentaire,
    CanDeleteCommentaire
)
from app.communaute.permissions.likecommentaire_permissions import CanCreateLikeCommentaire
from app.communaute.permissions.confirmationaide_permissions import CanCreateConfirmationAide


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
        self.like_commentaire_service = LikeCommentaireService()
        self.confirmation_aide_service = ConfirmationAideService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewCommentaire]
        elif self.action == 'create':
            permission_classes = [CanCreateCommentaire]
        elif self.action == 'like':
            permission_classes = [CanCreateLikeCommentaire]
        elif self.action == 'confirmation_aide':
            permission_classes = [CanCreateConfirmationAide]
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
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated = serializer.validated_data
            publication_id = validated.get('publication_id')
            if publication_id is None:
                raise ValidationError('publication_id est obligatoire.')
            commentaire = self.commentaire_service.create_commentaire(
                publication_id=publication_id,
                auteur=request.user,
                texte=validated.get('texte', ''),
                parent_id=validated.get('parent_id'),
                nature=validated.get('nature') or CommentaireService.NATURE_COMMENTAIRE,
                est_anonyme=bool(validated.get('est_anonyme', False)),
                created_by=request.user.id,
                updated_by=request.user.id,
            )
            return Response(
                self.get_serializer(commentaire).data,
                status=status.HTTP_201_CREATED,
            )
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

    @swagger_auto_schema(
        method='post',
        operation_description="Ajouter ou retirer son like sur le commentaire",
        responses={200: openapi.Response('État du like'), 400: 'Erreur'},
        security=[{'Bearer': []}],
        tags=['V1 - Commentaire'],
    )
    @action(detail=True, methods=['post'], url_path='like')
    def like(self, request, pk=None):
        """Toggle du like sur un commentaire."""
        try:
            result = self.like_commentaire_service.toggle(
                commentaire_id=int(pk),
                membre=request.user,
            )
            return Response(result)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Identifiant invalide'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        operation_description="Ajouter ou retirer « Ça m'a aidé aussi » sur une réponse technique",
        responses={200: openapi.Response('État de la confirmation'), 400: 'Erreur'},
        security=[{'Bearer': []}],
        tags=['V1 - Commentaire'],
    )
    @action(detail=True, methods=['post'], url_path='confirmation-aide')
    def confirmation_aide(self, request, pk=None):
        """Toggle de « Ça m'a aidé aussi »."""
        try:
            result = self.confirmation_aide_service.toggle(
                commentaire_id=int(pk),
                membre=request.user,
            )
            return Response(result)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Identifiant invalide'}, status=status.HTTP_400_BAD_REQUEST)