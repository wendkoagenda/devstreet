"""
ViewSet pour la gestion des reviews.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import Review
from app.marketplace.serializers import ReviewSerializer
from app.marketplace.services.review_service import ReviewService
from app.marketplace.permissions.review_permissions import (
    CanViewReview,
    CanCreateReview,
    CanUpdateReview,
    CanDeleteReview
)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les reviews.
    """
    swagger_tags = ['V1 - Review']
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.review_service = ReviewService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewReview]
        elif self.action == 'create':
            permission_classes = [CanCreateReview]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateReview]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteReview]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les reviews (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: ReviewSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Review']
    )
    def list(self, request):
        """
        Retourne une page de reviews (format : count, next, previous, results).
        """
        try:
            reviews = self.review_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(reviews)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un review par son ID",
        responses={
            200: ReviewSerializer,
            404: "Review non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Review']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un review spécifique.
        """
        review = self.review_service.get_by_id(pk)
        if not review:
            return Response(
                {'error': 'Review non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(review)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau review",
        request_body=ReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Review']
    )
    def create(self, request):
        """
        Crée un nouveau review.
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
            review = self.review_service.create(data)
            serializer = self.get_serializer(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un review",
        request_body=ReviewSerializer,
        responses={
            200: ReviewSerializer,
            400: "Données invalides",
            404: "Review non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Review']
    )
    def update(self, request, pk=None):
        """
        Met à jour un review existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            review = self.review_service.update(pk, data)
            if review is None:
                return Response(
                    {'error': 'Review non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(review)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un review",
        request_body=ReviewSerializer,
        responses={
            200: ReviewSerializer,
            400: "Données invalides",
            404: "Review non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Review']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un review existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            review = self.review_service.update(pk, data, partial=True)
            if review is None:
                return Response(
                    {'error': 'Review non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(review)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un review",
        responses={
            204: "Review supprimé avec succès",
            404: "Review non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Review']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un review.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.review_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Review non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )