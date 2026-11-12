"""
ViewSet pour la gestion des offers.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.marketplace.models import Offer
from app.marketplace.serializers import OfferSerializer
from app.marketplace.services.offer_service import OfferService
from app.marketplace.permissions.offer_permissions import (
    CanViewOffer,
    CanCreateOffer,
    CanUpdateOffer,
    CanDeleteOffer
)


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les offers.
    """
    swagger_tags = ['V1 - Offer']
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offer_service = OfferService()


    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewOffer]
        elif self.action == 'create':
            permission_classes = [CanCreateOffer]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateOffer]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteOffer]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister les offers (paginé : 20 par page, 100 au maximum)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Numéro de page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Taille de page (100 au maximum)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Champ de tri, préfixé par - pour décroissant", type=openapi.TYPE_STRING),
        ],
        responses={200: OfferSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Offer']
    )
    def list(self, request):
        """
        Retourne une page de offers (format : count, next, previous, results).
        """
        try:
            offers = self.offer_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
            )
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(offers)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un offer par son ID",
        responses={
            200: OfferSerializer,
            404: "Offer non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Offer']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un offer spécifique.
        """
        offer = self.offer_service.get_by_id(pk)
        if not offer:
            return Response(
                {'error': 'Offer non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(offer)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau offer",
        request_body=OfferSerializer,
        responses={
            201: OfferSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Offer']
    )
    def create(self, request):
        """
        Crée un nouveau offer.
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
            offer = self.offer_service.create(data)
            serializer = self.get_serializer(offer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un offer",
        request_body=OfferSerializer,
        responses={
            200: OfferSerializer,
            400: "Données invalides",
            404: "Offer non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Offer']
    )
    def update(self, request, pk=None):
        """
        Met à jour un offer existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            offer = self.offer_service.update(pk, data)
            if offer is None:
                return Response(
                    {'error': 'Offer non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(offer)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un offer",
        request_body=OfferSerializer,
        responses={
            200: OfferSerializer,
            400: "Données invalides",
            404: "Offer non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Offer']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un offer existant.
        """
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            offer = self.offer_service.update(pk, data, partial=True)
            if offer is None:
                return Response(
                    {'error': 'Offer non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(offer)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un offer",
        responses={
            204: "Offer supprimé avec succès",
            404: "Offer non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Offer']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un offer.
        """
        # Une vraie erreur (base de données, stockage) remonte : DRF répond 500 sans exposer le détail interne
        success = self.offer_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Offer non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )