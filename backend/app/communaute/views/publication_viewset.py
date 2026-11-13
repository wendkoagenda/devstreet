"""
ViewSet pour la gestion des publications.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.communaute.models import Publication
from app.communaute.serializers import (
    AvisChoixSerializer,
    PublicationSerializer,
    CommentaireSerializer,
)
from app.communaute.services.publication_service import PublicationService
from app.communaute.services.commentaire_service import CommentaireService
from app.communaute.services.favoripublication_service import FavoriPublicationService
from app.communaute.services.likepublication_service import LikePublicationService
from app.communaute.permissions.publication_permissions import (
    CanViewPublication,
    CanCreatePublication,
    CanUpdatePublication,
    CanDeletePublication,
)
from app.communaute.permissions.commentaire_permissions import (
    CanViewCommentaire,
    CanCreateCommentaire,
)
from app.communaute.permissions.likepublication_permissions import CanCreateLikePublication
from app.communaute.permissions.avischoix_permissions import (
    CanCreateAvisChoix,
    CanViewAvisChoix,
)
from app.core.pagination import FeedCursorPagination, PourVousCursorPagination


class PublicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les publications.
    """
    swagger_tags = ['V1 - Publication']
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FeedCursorPagination

    def get_paginator(self):
        """Pagination adaptée au fil « Pour vous » (prioritaire + date)."""
        if getattr(self, '_use_pour_vous_pagination', False):
            if not hasattr(self, '_pour_vous_paginator'):
                self._pour_vous_paginator = PourVousCursorPagination()
            return self._pour_vous_paginator
        return super().paginator

    @property
    def paginator(self):
        return self.get_paginator()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publication_service = PublicationService()
        self.commentaire_service = CommentaireService()
        self.like_publication_service = LikePublicationService()
        self.favori_publication_service = FavoriPublicationService()

    def get_permissions(self):
        """Retourne les permissions requises selon l'action."""
        if self.action in ('list', 'retrieve', 'commentaires'):
            if self.action == 'commentaires' and self.request.method == 'POST':
                permission_classes = [CanCreateCommentaire]
            elif self.action == 'commentaires':
                permission_classes = [CanViewCommentaire]
            else:
                permission_classes = [CanViewPublication]
        elif self.action == 'like':
            permission_classes = [CanCreateLikePublication]
        elif self.action in ('accepter_reponse', 'decider'):
            permission_classes = [CanUpdatePublication]
        elif self.action == 'avis':
            if self.request.method == 'POST':
                permission_classes = [CanCreateAvisChoix]
            else:
                permission_classes = [CanViewAvisChoix]
        elif self.action in ('create', 'upload_image', 'upload_media'):
            permission_classes = [CanCreatePublication]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdatePublication]
        elif self.action == 'destroy':
            permission_classes = [CanDeletePublication]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description=(
            "Lister les publications (scroll infini via curseur : 20 par page, 100 au maximum). "
            "Réponse : next, previous, results (pas de count)."
        ),
        manual_parameters=[
            openapi.Parameter(
                'cursor',
                openapi.IN_QUERY,
                description="Curseur opaque pour la page suivante / précédente",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Taille de page (100 au maximum)",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter('search', openapi.IN_QUERY, description="Recherche textuelle", type=openapi.TYPE_STRING),
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="Filtrer par type (DISCUSSION, APPLICATION, ENTRAIDE, CHOIX, SONDAGE)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'auteur',
                openapi.IN_QUERY,
                description="Filtrer par ID d'auteur",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                'espace',
                openapi.IN_QUERY,
                description="Filtrer par ID d'espace (communauté/chaîne)",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={200: PublicationSerializer(many=True), 400: "Tri invalide"},
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def list(self, request):
        """Retourne une page de publications (format curseur : next, previous, results)."""
        auteur_raw = request.query_params.get('auteur')
        auteur_id = None
        if auteur_raw not in (None, ''):
            try:
                auteur_id = int(auteur_raw)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'Paramètre auteur invalide'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if auteur_id <= 0:
                return Response(
                    {'error': 'Paramètre auteur invalide'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        espace_raw = request.query_params.get('espace')
        espace_id = None
        general_only = False
        feed_mode = (request.query_params.get('feed') or '').strip().lower()
        pour_vous = feed_mode in ('pour-vous', 'pour_vous', 'foryou')
        abonnements = feed_mode in (
            'abonnements',
            'following',
            'subscriptions',
        )
        self._use_pour_vous_pagination = pour_vous
        if espace_raw not in (None, ''):
            try:
                espace_id = int(espace_raw)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'Paramètre espace invalide'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if espace_id <= 0:
                return Response(
                    {'error': 'Paramètre espace invalide'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif auteur_id is None and not pour_vous and not abonnements:
            # Fil général : hors publications rattachées à un espace
            general_only = True
        if espace_id is not None:
            from app.communaute.services.espace_service import EspaceService

            espace = EspaceService().get_by_id(espace_id)
            if espace is None:
                return Response(
                    {'error': 'Espace introuvable'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                EspaceService().assert_can_read(
                    espace=espace,
                    acteur=request.user,
                    invite_code=request.query_params.get('invite'),
                )
                from app.communaute.services.activity_service import (
                    ActivityService,
                )

                ActivityService().mark_espace_read(
                    espace_id=espace.id, acteur=request.user
                )
            except ValidationError as e:
                return Response(
                    {
                        'error': str(
                            e.message if hasattr(e, 'message') else e
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        try:
            publications = self.publication_service.get_all(
                search=request.query_params.get('search'),
                # Le tri est imposé par FeedCursorPagination / PourVousCursorPagination
                ordering=None,
                type_filter=request.query_params.get('type'),
                auteur_id=auteur_id,
                espace_id=espace_id,
                general_only=general_only,
                pour_vous=pour_vous,
                abonnements=abonnements,
                membre=request.user,
            )
        except ValueError:
            return Response({'error': 'Tri ou type invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(publications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer un publication par son ID",
        responses={
            200: PublicationSerializer,
            404: "Publication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def retrieve(self, request, pk=None):
        """Retourne les détails d'un publication spécifique."""
        publication = self.publication_service.get_by_id(pk, membre=request.user)
        if not publication:
            return Response(
                {'error': 'Publication non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(publication)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau publication",
        request_body=PublicationSerializer,
        responses={
            201: PublicationSerializer,
            400: "Données invalides"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def create(self, request):
        """Crée une discussion ou une application partagée."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated = serializer.validated_data
            publication_type = validated.get('type') or PublicationService.DISCUSSION_TYPE

            if publication_type == PublicationService.DISCUSSION_TYPE:
                publication = self.publication_service.create_discussion(
                    auteur=request.user,
                    titre=validated.get('titre', ''),
                    description=validated.get('description', ''),
                    images=validated.get('images_data') or [],
                    created_by=request.user.id,
                    updated_by=request.user.id,
                    espace_id=validated.get('espace_id'),
                )
            elif publication_type == PublicationService.APPLICATION_TYPE:
                publication = self.publication_service.create_application(
                    auteur=request.user,
                    titre=validated.get('titre', ''),
                    description=validated.get('description', ''),
                    lien_app=validated.get('lien_app', ''),
                    plateforme_app=validated.get('plateforme_app') or 'WEB',
                    images=validated.get('images_data') or [],
                    created_by=request.user.id,
                    updated_by=request.user.id,
                )
            elif publication_type == PublicationService.ENTRAIDE_TYPE:
                publication = self.publication_service.create_entraide(
                    auteur=request.user,
                    titre=validated.get('titre', ''),
                    description=validated.get('description', ''),
                    images=validated.get('images_data') or [],
                    created_by=request.user.id,
                    updated_by=request.user.id,
                )
            elif publication_type == PublicationService.CHOIX_TYPE:
                publication = self.publication_service.create_choix(
                    auteur=request.user,
                    titre=validated.get('titre', ''),
                    description=validated.get('description', ''),
                    contraintes=validated.get('contraintes', ''),
                    options=validated.get('options_data') or [],
                    images=validated.get('images_data') or [],
                    created_by=request.user.id,
                    updated_by=request.user.id,
                )
            else:
                return Response(
                    {
                        'error': (
                            'Types acceptés pour le moment : '
                            'DISCUSSION, APPLICATION, ENTRAIDE, CHOIX.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                self.get_serializer(publication).data,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour un publication",
        request_body=PublicationSerializer,
        responses={
            200: PublicationSerializer,
            400: "Données invalides",
            404: "Publication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def update(self, request, pk=None):
        """Met à jour un publication existant."""
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            publication = self.publication_service.update(pk, data)
            if publication is None:
                return Response(
                    {'error': 'Publication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un publication",
        request_body=PublicationSerializer,
        responses={
            200: PublicationSerializer,
            400: "Données invalides",
            404: "Publication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def partial_update(self, request, pk=None):
        """Met à jour partiellement un publication existant."""
        try:
            data = request.data.copy()
            data.pop('created_by', None)
            data.pop('created_at', None)
            data.pop('updated_at', None)
            if hasattr(request, 'user') and request.user and getattr(request.user, 'id', None) is not None:
                data['updated_by'] = request.user.id
            publication = self.publication_service.update(pk, data, partial=True)
            if publication is None:
                return Response(
                    {'error': 'Publication non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(publication)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Supprimer un publication",
        responses={
            204: "Publication supprimé avec succès",
            404: "Publication non trouvé"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication']
    )
    def destroy(self, request, pk=None):
        """Supprime un publication."""
        success = self.publication_service.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Publication non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )

    @swagger_auto_schema(
        method='post',
        operation_description="Ajouter ou retirer son like sur la publication",
        responses={200: openapi.Response('État du like'), 400: 'Erreur', 404: 'Introuvable'},
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @action(detail=True, methods=['post'], url_path='like')
    def like(self, request, pk=None):
        """Toggle du like sur une publication."""
        try:
            result = self.like_publication_service.toggle(
                publication_id=int(pk),
                membre=request.user,
            )
            return Response(result)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Identifiant invalide'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        operation_description="Ajouter ou retirer la publication des favoris",
        responses={200: openapi.Response('État du favori'), 400: 'Erreur'},
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @action(detail=True, methods=['post'], url_path='favori')
    def favori(self, request, pk=None):
        """Toggle du favori (bookmark) sur une publication."""
        try:
            result = self.favori_publication_service.toggle(
                publication_id=int(pk),
                membre=request.user,
            )
            return Response(result)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Identifiant invalide'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        operation_description=(
            "Accepter, changer ou retirer la réponse technique "
            "(body: {commentaire_id: number|null})"
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'commentaire_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    x_nullable=True,
                    description='ID de la réponse technique, ou null pour retirer',
                ),
            },
        ),
        responses={200: PublicationSerializer, 400: 'Erreur'},
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @action(detail=True, methods=['post'], url_path='accepter-reponse')
    def accepter_reponse(self, request, pk=None):
        """Accepte ou retire la réponse technique retenue."""
        try:
            raw_id = request.data.get('commentaire_id', None)
            commentaire_id = None if raw_id in (None, '', 'null') else int(raw_id)
            publication = self.publication_service.accepter_reponse(
                publication_id=int(pk),
                commentaire_id=commentaire_id,
                auteur=request.user,
            )
            return Response(self.get_serializer(publication).data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Identifiant invalide'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        operation_description="Lister les avis d'une aide au choix",
        responses={200: AvisChoixSerializer(many=True)},
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @swagger_auto_schema(
        method='post',
        operation_description="Créer ou modifier son avis sur une option",
        request_body=AvisChoixSerializer,
        responses={200: AvisChoixSerializer, 400: 'Erreur'},
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @action(detail=True, methods=['get', 'post'], url_path='avis')
    def avis(self, request, pk=None):
        """Liste ou upsert l'avis du membre sur une aide au choix."""
        if request.method == 'GET':
            avis_list = self.publication_service.list_avis_choix(
                publication_id=int(pk),
                membre=request.user,
            )
            return Response(AvisChoixSerializer(avis_list, many=True).data)

        try:
            serializer = AvisChoixSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated = serializer.validated_data
            avis = self.publication_service.upsert_avis_choix(
                publication_id=int(pk),
                option_id=int(validated.get('option_id')),
                membre=request.user,
                explication=validated.get('explication', ''),
            )
            return Response(
                AvisChoixSerializer(avis).data,
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Identifiant invalide'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        operation_description="Publier la décision finale (auteur seul)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['option_id', 'justification_finale'],
            properties={
                'option_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'justification_finale': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: PublicationSerializer, 400: 'Erreur'},
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @action(detail=True, methods=['post'], url_path='decider')
    def decider(self, request, pk=None):
        """Publie l'option retenue et la justification."""
        try:
            publication = self.publication_service.decider_choix(
                publication_id=int(pk),
                option_id=int(request.data.get('option_id')),
                justification_finale=request.data.get('justification_finale', ''),
                auteur=request.user,
            )
            return Response(self.get_serializer(publication).data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Identifiant invalide'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        operation_description=(
            "Téléverser une image pour une publication ou une option de débat. "
            "Multipart : champ `image` + `image_path` (ex. forum_images/nom.jpg)."
        ),
        responses={
            201: openapi.Response(
                'Image téléversée',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'url': openapi.Schema(type=openapi.TYPE_STRING),
                        'path': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: 'Fichier invalide',
        },
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @action(detail=False, methods=['post'], url_path='upload-image')
    def upload_image(self, request):
        """Compat : upload image (délègue à upload-media)."""
        return self.upload_media(request)

    @action(detail=False, methods=['post'], url_path='upload-media')
    def upload_media(self, request):
        """Enregistre un média forum (image, vidéo ou audio) et retourne son URL."""
        from app.metier.services.storage_service import get_storage_service
        from app.metier.utils.file_field_utils import _validate_upload

        uploaded = (
            request.FILES.get('file')
            or request.FILES.get('image')
            or request.FILES.get('media')
        )
        if uploaded is None:
            return Response(
                {'error': 'Fichier manquant (champ file).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        kind = str(request.data.get('kind') or 'IMAGE').strip().upper()
        profiles = {
            'IMAGE': {
                'folder': 'forum_images',
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
                'max_size_mb': 5,
            },
            'VIDEO': {
                'folder': 'forum_videos',
                'extensions': ['.mp4', '.webm', '.mov', '.m4v'],
                'max_size_mb': 50,
            },
            'AUDIO': {
                'folder': 'forum_audios',
                'extensions': ['.mp3', '.ogg', '.wav', '.m4a', '.webm'],
                'max_size_mb': 15,
            },
        }
        profile = profiles.get(kind)
        if profile is None:
            return Response(
                {'error': 'Type invalide : IMAGE, VIDEO ou AUDIO.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        relative_path = str(
            request.data.get('path')
            or request.data.get('image_path')
            or ''
        ).strip().lstrip('/')
        if not relative_path.startswith(f"{profile['folder']}/"):
            return Response(
                {
                    'error': (
                        f"Chemin invalide : doit commencer par "
                        f"{profile['folder']}/."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            _validate_upload(
                uploaded,
                allowed_extensions=profile['extensions'],
                max_size_mb=profile['max_size_mb'],
            )
            storage = get_storage_service()
            saved_path = storage.save(relative_path, uploaded)
            media_url = storage.url(saved_path)
            if media_url.startswith('http://') or media_url.startswith('https://'):
                absolute_url = media_url
            else:
                absolute_url = request.build_absolute_uri(media_url)
            return Response(
                {'url': absolute_url, 'path': saved_path, 'kind': kind},
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {'error': "Impossible d'enregistrer le média."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        method='get',
        operation_description="Lister les commentaires d'une publication",
        responses={200: CommentaireSerializer(many=True)},
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @swagger_auto_schema(
        method='post',
        operation_description="Créer un commentaire ou une réponse sur la publication",
        request_body=CommentaireSerializer,
        responses={201: CommentaireSerializer, 400: 'Données invalides'},
        security=[{'Bearer': []}],
        tags=['V1 - Publication'],
    )
    @action(detail=True, methods=['get', 'post'], url_path='commentaires')
    def commentaires(self, request, pk=None):
        """Liste ou crée les commentaires d'une publication."""
        if request.method == 'GET':
            commentaires = self.commentaire_service.list_for_publication(
                publication_id=int(pk),
                membre=request.user,
            )
            return Response(CommentaireSerializer(commentaires, many=True).data)

        try:
            payload = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            payload['publication_id'] = int(pk)
            serializer = CommentaireSerializer(data=payload)
            serializer.is_valid(raise_exception=True)
            validated = serializer.validated_data
            commentaire = self.commentaire_service.create_commentaire(
                publication_id=int(pk),
                auteur=request.user,
                texte=validated.get('texte', ''),
                parent_id=validated.get('parent_id'),
                option_id=validated.get('option_id'),
                nature=validated.get('nature') or CommentaireService.NATURE_COMMENTAIRE,
                est_anonyme=bool(validated.get('est_anonyme', False)),
                medias=list(validated.get('medias_data') or []),
                created_by=request.user.id,
                updated_by=request.user.id,
            )
            return Response(
                CommentaireSerializer(commentaire).data,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Identifiant invalide'}, status=status.HTTP_400_BAD_REQUEST)
