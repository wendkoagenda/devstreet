"""
API tags forum : liste, tags suivis, toggle suivi.
"""
from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.communaute.models import Tag
from app.communaute.serializers import TagSerializer
from app.communaute.services.tag_service import TagService


class TagLimitPagination(LimitOffsetPagination):
    """Borne la taille des listes de tags (paramètre ?limit=, 100 au plus) ; la réponse reste un tableau."""

    default_limit = 30
    max_limit = 100


class TagSuivisPagination(TagLimitPagination):
    default_limit = 100


class TagViewSet(viewsets.ViewSet):
    """Endpoints tags (thèmes de publication)."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tag_service = TagService()

    def get_serializer_context(self):
        return {'request': self.request}

    @swagger_auto_schema(
        operation_description="Lister les tags (recherche optionnelle)",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={200: TagSerializer(many=True)},
        security=[{'Bearer': []}],
        tags=['V1 - Tag'],
    )
    def list(self, request):
        tags = self.tag_service.list_tags(
            search=request.query_params.get('search'),
            limit=TagLimitPagination.max_limit,
        )
        paginator = TagLimitPagination()
        page = paginator.paginate_queryset(tags, request, view=self)
        serializer = TagSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Tags suivis par l'utilisateur (Mes favoris thèmes)",
        responses={200: TagSerializer(many=True)},
        security=[{'Bearer': []}],
        tags=['V1 - Tag'],
    )
    @action(detail=False, methods=['get'], url_path='suivis')
    def suivis(self, request):
        tags = self.tag_service.list_suivis(request.user)
        paginator = TagSuivisPagination()
        page = paginator.paginate_queryset(tags, request, view=self)
        serializer = TagSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Suivre ou ne plus suivre un tag",
        responses={200: openapi.Response('État du suivi'), 400: 'Erreur'},
        security=[{'Bearer': []}],
        tags=['V1 - Tag'],
    )
    @action(detail=True, methods=['post'], url_path='suivre')
    def suivre(self, request, pk=None):
        """pk = slug du tag."""
        try:
            result = self.tag_service.toggle_suivi(
                membre=request.user, slug=pk
            )
            return Response(result)
        except ValidationError as exc:
            return Response(
                {'error': str(exc.message if hasattr(exc, 'message') else exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_description="Détail d'un tag par slug",
        responses={200: TagSerializer, 404: 'Introuvable'},
        security=[{'Bearer': []}],
        tags=['V1 - Tag'],
    )
    def retrieve(self, request, pk=None):
        tag = Tag.objects.filter(slug=(pk or '').strip().lower()).first()
        if tag is None:
            return Response(
                {'error': 'Tag introuvable'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            TagSerializer(tag, context=self.get_serializer_context()).data
        )
