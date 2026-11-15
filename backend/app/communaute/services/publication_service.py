"""
Publication service layer pour les opérations de logique métier.
"""
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from django.db import transaction
from django.db.models import (
    BooleanField,
    Case,
    Count,
    Exists,
    IntegerField,
    OuterRef,
    Prefetch,
    Q,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.core.exceptions import ValidationError
from django.http import Http404
from django.contrib.auth import get_user_model

from django.utils import timezone

from app.communaute.models import (
    AvisChoix,
    Commentaire,
    ImagePublication,
    OptionPublication,
    ParticipationEspace,
    Publication,
    SuiviUtilisateur,
)
from app.communaute.repositories.publication_repository import PublicationRepository

User = get_user_model()


class PublicationService:
    """
    Classe de service pour la logique métier liée aux publications.
    """

    DISCUSSION_TYPE = 'DISCUSSION'
    APPLICATION_TYPE = 'APPLICATION'
    ENTRAIDE_TYPE = 'ENTRAIDE'
    CHOIX_TYPE = 'CHOIX'
    SONDAGE_TYPE = 'SONDAGE'
    PLATEFORMES_APP = ('WEB', 'MOBILE', 'LES_DEUX')
    MEDIA_KINDS = (ImagePublication.KIND_IMAGE, ImagePublication.KIND_VIDEO)

    def __init__(self):
        self.publication_repository = PublicationRepository()

    def _attach_medias(
        self,
        *,
        publication: Publication,
        images: List[Dict[str, Any]],
        created_by: int,
        updated_by: int,
        label: str = 'publication',
    ) -> None:
        """Attache images/vidéos à une publication (max 10)."""
        if len(images) > 10:
            raise ValidationError(
                f'Une {label} accepte au plus 10 médias (images/vidéos).'
            )
        for index, image in enumerate(images):
            url = (image.get('url') or '').strip()
            if not url:
                raise ValidationError('Chaque média doit avoir une URL.')
            kind = str(image.get('kind') or ImagePublication.KIND_IMAGE).upper()
            if kind not in self.MEDIA_KINDS:
                raise ValidationError('Type de média invalide (IMAGE ou VIDEO).')
            ImagePublication.objects.create(
                publication=publication,
                kind=kind,
                url=url,
                texte_alternatif=(image.get('texte_alternatif') or '').strip(),
                position=image.get('position', index),
                created_by=created_by,
                updated_by=updated_by,
            )

    def _with_engagement(self, queryset: QuerySet, membre: Optional[User] = None) -> QuerySet:
        """Ajoute compteurs likes/commentaires et l'état liked_by_me."""
        annotations = {
            'likes_count': Count('likes', distinct=True),
            'comments_count': Count('commentaires', distinct=True),
        }
        if membre and getattr(membre, 'is_authenticated', False) and getattr(membre, 'id', None):
            annotations['liked_by_me'] = Count(
                'likes',
                filter=Q(likes__membre_id=membre.id),
                distinct=True,
            )
            annotations['saved_by_me'] = Count(
                'favoris',
                filter=Q(favoris__membre_id=membre.id),
                distinct=True,
            )
            annotations['following_auteur'] = Exists(
                SuiviUtilisateur.objects.filter(
                    suiveur_id=membre.id,
                    suivi_id=OuterRef('auteur_id'),
                )
            )
            annotations['joined_espace'] = Exists(
                ParticipationEspace.objects.filter(
                    membre_id=membre.id,
                    espace_id=OuterRef('espace_id'),
                )
            )
            annotations['espace_mon_role'] = Subquery(
                ParticipationEspace.objects.filter(
                    membre_id=membre.id,
                    espace_id=OuterRef('espace_id'),
                ).values('role')[:1]
            )
        options_qs = (
            OptionPublication.objects.order_by('position', 'id')
            .annotate(avis_count=Count('avis', distinct=True))
        )
        return (
            queryset.select_related(
                'auteur',
                'espace',
                'reponse_acceptee',
                'reponse_acceptee__auteur',
                'option_retenue',
            )
            .prefetch_related(
                Prefetch('images', queryset=ImagePublication.objects.order_by('position', 'id')),
                Prefetch('options', queryset=options_qs),
                'tags',
            )
            .annotate(**annotations)
        )

    def get_all(
        self,
        search: Optional[str] = None,
        ordering: Optional[str] = None,
        membre: Optional[User] = None,
        type_filter: Optional[str] = None,
        auteur_id: Optional[int] = None,
        espace_id: Optional[int] = None,
        general_only: bool = False,
        pour_vous: bool = False,
        abonnements: bool = False,
        favoris: bool = False,
        populaires: bool = False,
        tag_slug: Optional[str] = None,
        tags_suivis: bool = False,
    ) -> QuerySet:
        """
        Fil d'actualité : publications chronologiques avec auteur, images et engagement.
        Mode pour_vous : priorise thèmes suivis + abonnements, puis le reste.
        Mode abonnements : uniquement suivis + chaînes (hors contenus hors abonnement).
        Mode favoris : bookmarks de l'utilisateur.
        Mode populaires : tri par likes puis commentaires.
        """
        if type_filter:
            type_filter = type_filter.strip().upper()
            if type_filter not in (
                self.DISCUSSION_TYPE,
                self.APPLICATION_TYPE,
                self.ENTRAIDE_TYPE,
                'CHOIX',
                'SONDAGE',
            ):
                raise ValueError(f'Type invalide : {type_filter}')
        if favoris:
            qs = self.get_feed_favoris(
                membre=membre,
                search=search,
                type_filter=type_filter or None,
            )
            return self._apply_tag_filters(
                qs, tag_slug=tag_slug, tags_suivis=tags_suivis, membre=membre
            )
        if populaires:
            qs = self.get_feed_populaires(
                membre=membre,
                search=search,
                type_filter=type_filter or None,
            )
            return self._apply_tag_filters(
                qs, tag_slug=tag_slug, tags_suivis=tags_suivis, membre=membre
            )
        if abonnements:
            qs = self.get_feed_abonnements(
                membre=membre,
                search=search,
                type_filter=type_filter or None,
            )
            return self._apply_tag_filters(
                qs, tag_slug=tag_slug, tags_suivis=tags_suivis, membre=membre
            )
        if pour_vous:
            # Tag = boost de priorité, pas un filtre exclusif (le reste du fil suit).
            return self.get_feed_pour_vous(
                membre=membre,
                search=search,
                type_filter=type_filter or None,
                prefer_tag_slug=tag_slug,
            )
        queryset = self.publication_repository.get_all(
            search=search,
            ordering=ordering,
            type_filter=type_filter or None,
            auteur_id=auteur_id,
            espace_id=espace_id,
            general_only=general_only,
        )
        queryset = self._with_engagement(queryset, membre=membre)
        return self._apply_tag_filters(
            queryset, tag_slug=tag_slug, tags_suivis=tags_suivis, membre=membre
        )

    def _apply_tag_filters(
        self,
        queryset: QuerySet,
        *,
        tag_slug: Optional[str] = None,
        tags_suivis: bool = False,
        membre: Optional[User] = None,
    ) -> QuerySet:
        from app.communaute.services.tag_service import TagService

        slug = (tag_slug or '').strip().lower()
        if slug:
            return queryset.filter(tags__slug=slug).distinct()
        if tags_suivis:
            # Mode legacy : boost de priorité (pas un mur exclusif).
            tag_ids = TagService().ids_suivis(membre)
            if not tag_ids:
                return queryset
            through = Publication.tags.through
            priorite = Case(
                When(
                    Exists(
                        through.objects.filter(
                            publication_id=OuterRef('pk'),
                            tag_id__in=tag_ids,
                        )
                    ),
                    then=Value(2),
                ),
                default=Value(0),
                output_field=IntegerField(),
            )
            return queryset.annotate(priorite_tags=priorite).order_by(
                '-priorite_tags', '-created_at', '-id'
            )
        return queryset

    def _subscription_ids(
        self, membre: Optional[User]
    ) -> tuple[List[int], List[int]]:
        """Retourne (followed_ids, channel_ids) pour le membre connecté."""
        from app.communaute.services.suiviutilisateur_service import (
            SuiviUtilisateurService,
        )

        if membre is None or not getattr(membre, 'id', None):
            return [], []
        followed_ids = list(SuiviUtilisateurService().ids_suivis_par(membre))
        channel_ids = list(
            ParticipationEspace.objects.filter(
                membre_id=membre.id,
                espace__type='CHAINE',
            ).values_list('espace_id', flat=True)
        )
        return followed_ids, channel_ids

    def _apply_text_filters(
        self,
        queryset: QuerySet,
        *,
        search: Optional[str] = None,
        type_filter: Optional[str] = None,
    ) -> QuerySet:
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        if search:
            condition = Q()
            for field_name in (
                'type',
                'titre',
                'description',
                'lien_app',
                'plateforme_app',
                'contraintes',
                'justification_finale',
                'mode_vote',
            ):
                condition |= Q(**{f'{field_name}__icontains': search})
            queryset = queryset.filter(condition)
        return queryset

    def get_feed_pour_vous(
        self,
        *,
        membre: Optional[User],
        search: Optional[str] = None,
        type_filter: Optional[str] = None,
        prefer_tag_slug: Optional[str] = None,
    ) -> QuerySet:
        """
        Fil personnalisé : pubs générales + chaînes abonnées.

        Ordre (sans masquer le reste) :
        1. thème explicitement choisi (favori cliqué), s'il y en a un
        2. thèmes suivis + membres suivis + chaînes abonnées
        3. le reste du fil
        """
        from app.communaute.models import Tag
        from app.communaute.services.tag_service import TagService

        followed_ids, channel_ids = self._subscription_ids(membre)
        tag_ids = TagService().ids_suivis(membre)

        prefer_slug = (prefer_tag_slug or '').strip().lower()
        prefer_tag_id = None
        if prefer_slug:
            prefer_tag_id = (
                Tag.objects.filter(slug=prefer_slug)
                .values_list('id', flat=True)
                .first()
            )

        visibility = Q(espace__isnull=True)
        if channel_ids:
            visibility |= Q(espace_id__in=channel_ids, espace__type='CHAINE')

        queryset = Publication.objects.filter(visibility).select_related(
            'espace', 'auteur'
        )
        queryset = self._apply_text_filters(
            queryset, search=search, type_filter=type_filter
        )

        # Exists évite les doublons M2M (pas de DISTINCT, compatible curseur).
        through = Publication.tags.through
        whens: List[When] = []
        if prefer_tag_id is not None:
            whens.append(
                When(
                    Exists(
                        through.objects.filter(
                            publication_id=OuterRef('pk'),
                            tag_id=prefer_tag_id,
                        )
                    ),
                    then=Value(3),
                )
            )
        if followed_ids:
            whens.append(
                When(
                    Q(auteur_id__in=followed_ids, espace__isnull=True),
                    then=Value(2),
                )
            )
        if channel_ids:
            whens.append(When(Q(espace_id__in=channel_ids), then=Value(2)))
        if tag_ids:
            whens.append(
                When(
                    Exists(
                        through.objects.filter(
                            publication_id=OuterRef('pk'),
                            tag_id__in=tag_ids,
                        )
                    ),
                    then=Value(2),
                )
            )

        if whens:
            priorite = Case(
                *whens,
                default=Value(0),
                output_field=IntegerField(),
            )
        else:
            priorite = Value(0, output_field=IntegerField())

        queryset = queryset.annotate(priorite=priorite).order_by(
            '-priorite', '-created_at', '-id'
        )
        return self._with_engagement(queryset, membre=membre)

    def get_feed_abonnements(
        self,
        *,
        membre: Optional[User],
        search: Optional[str] = None,
        type_filter: Optional[str] = None,
    ) -> QuerySet:
        """
        Fil « Abonnements » : uniquement pubs générales des membres suivis
        et pubs des chaînes abonnées. Aucun espace privé non accessible.
        Dedup naturelle (une pub = une ligne).
        """
        followed_ids, channel_ids = self._subscription_ids(membre)

        if not followed_ids and not channel_ids:
            return self._with_engagement(
                Publication.objects.none(), membre=membre
            )

        visibility = Q()
        if followed_ids:
            # Fil général seulement — jamais une pub d'espace LIEN non joint
            visibility |= Q(auteur_id__in=followed_ids, espace__isnull=True)
        if channel_ids:
            visibility |= Q(espace_id__in=channel_ids, espace__type='CHAINE')

        queryset = (
            Publication.objects.filter(visibility)
            .select_related('espace', 'auteur')
            .distinct()
        )
        queryset = self._apply_text_filters(
            queryset, search=search, type_filter=type_filter
        )
        return self._with_engagement(
            queryset.order_by('-created_at', '-id'), membre=membre
        )

    def get_feed_favoris(
        self,
        *,
        membre: Optional[User],
        search: Optional[str] = None,
        type_filter: Optional[str] = None,
    ) -> QuerySet:
        """Publications mises en favori par l'utilisateur connecté."""
        if membre is None or not getattr(membre, 'id', None):
            return self._with_engagement(
                Publication.objects.none(), membre=membre
            )
        queryset = (
            Publication.objects.filter(favoris__membre_id=membre.id)
            .select_related('espace', 'auteur')
            .distinct()
        )
        queryset = self._apply_text_filters(
            queryset, search=search, type_filter=type_filter
        )
        return self._with_engagement(
            queryset.order_by('-created_at', '-id'), membre=membre
        )

    def get_feed_populaires(
        self,
        *,
        membre: Optional[User],
        search: Optional[str] = None,
        type_filter: Optional[str] = None,
    ) -> QuerySet:
        """Fil général trié par engagement (likes, commentaires)."""
        queryset = Publication.objects.filter(espace__isnull=True).select_related(
            'espace', 'auteur'
        )
        queryset = self._apply_text_filters(
            queryset, search=search, type_filter=type_filter
        )
        queryset = self._with_engagement(queryset, membre=membre)
        return queryset.order_by(
            '-likes_count', '-comments_count', '-created_at', '-id'
        )

    def get_by_id(
        self, publication_id: int, membre: Optional[User] = None
    ) -> Optional[Publication]:
        """Obtenir une publication par ID avec ses relations."""
        return (
            self._with_engagement(Publication.objects.filter(id=publication_id), membre=membre)
            .first()
        )

    def create(self, publication_data: Dict[str, Any]) -> Publication:
        """Créer une publication générique (CRUD généré)."""
        self.validate_data(publication_data)
        return self.publication_repository.create(**publication_data)

    def _resolve_espace_for_publish(
        self, *, auteur: User, espace_id: Optional[int]
    ):
        if espace_id in (None, ''):
            return None
        try:
            espace_pk = int(espace_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError('espace_id invalide.') from exc
        if espace_pk <= 0:
            raise ValidationError('espace_id invalide.')

        from app.communaute.models import Espace
        from app.communaute.services.espace_service import EspaceService

        espace = Espace.objects.filter(pk=espace_pk).first()
        if espace is None:
            raise ValidationError('Espace introuvable.')
        EspaceService().assert_can_publish(espace=espace, membre=auteur)
        return espace

    def create_discussion(
        self,
        *,
        auteur: User,
        titre: str,
        description: str,
        images: Optional[List[Dict[str, Any]]] = None,
        created_by: int,
        updated_by: int,
        espace_id: Optional[int] = None,
    ) -> Publication:
        """
        Créer une discussion (fil général ou espace) avec images facultatives.
        """
        titre = (titre or '').strip()
        description = (description or '').strip()
        if not titre:
            raise ValidationError('Le titre est obligatoire.')
        if not description:
            raise ValidationError('La description est obligatoire.')

        images = images or []

        espace = self._resolve_espace_for_publish(auteur=auteur, espace_id=espace_id)

        with transaction.atomic():
            publication = self.publication_repository.create(
                auteur=auteur,
                type=self.DISCUSSION_TYPE,
                titre=titre,
                description=description,
                espace=espace,
                created_by=created_by,
                updated_by=updated_by,
            )
            self._attach_medias(
                publication=publication,
                images=images,
                created_by=created_by,
                updated_by=updated_by,
            )

        return self.get_by_id(publication.id, membre=auteur)

    def _validate_http_url(self, url: str) -> str:
        """Refuse tout lien non HTTP(S)."""
        cleaned = (url or '').strip()
        if not cleaned:
            raise ValidationError('Le lien de l\'application est obligatoire.')
        parsed = urlparse(cleaned)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise ValidationError('Le lien doit être une URL HTTP ou HTTPS valide.')
        return cleaned

    def create_application(
        self,
        *,
        auteur: User,
        titre: str,
        description: str,
        lien_app: str,
        plateforme_app: str = 'WEB',
        images: Optional[List[Dict[str, Any]]] = None,
        created_by: int,
        updated_by: int,
    ) -> Publication:
        """Créer une publication APPLICATION avec lien d'essai HTTP(S)."""
        titre = (titre or '').strip()
        description = (description or '').strip()
        if not titre:
            raise ValidationError('Le titre est obligatoire.')
        if not description:
            raise ValidationError('La description est obligatoire.')

        lien = self._validate_http_url(lien_app)
        plateforme = (plateforme_app or 'WEB').strip().upper()
        if plateforme not in self.PLATEFORMES_APP:
            raise ValidationError('Plateforme d\'application invalide.')

        images = images or []

        with transaction.atomic():
            publication = self.publication_repository.create(
                auteur=auteur,
                type=self.APPLICATION_TYPE,
                titre=titre,
                description=description,
                lien_app=lien,
                plateforme_app=plateforme,
                created_by=created_by,
                updated_by=updated_by,
            )
            self._attach_medias(
                publication=publication,
                images=images,
                created_by=created_by,
                updated_by=updated_by,
            )

        return self.get_by_id(publication.id, membre=auteur)

    def create_entraide(
        self,
        *,
        auteur: User,
        titre: str,
        description: str,
        images: Optional[List[Dict[str, Any]]] = None,
        created_by: int,
        updated_by: int,
    ) -> Publication:
        """Créer une demande d'entraide technique (texte/code + captures facultatives)."""
        titre = (titre or '').strip()
        description = (description or '').strip()
        if not titre:
            raise ValidationError('Le titre est obligatoire.')
        if not description:
            raise ValidationError('La description est obligatoire.')

        images = images or []

        with transaction.atomic():
            publication = self.publication_repository.create(
                auteur=auteur,
                type=self.ENTRAIDE_TYPE,
                titre=titre,
                description=description,
                created_by=created_by,
                updated_by=updated_by,
            )
            self._attach_medias(
                publication=publication,
                images=images,
                created_by=created_by,
                updated_by=updated_by,
            )

        return self.get_by_id(publication.id, membre=auteur)

    def create_choix(
        self,
        *,
        auteur: User,
        titre: str,
        description: str,
        options: List[Dict[str, Any]],
        contraintes: str = '',
        images: Optional[List[Dict[str, Any]]] = None,
        created_by: int,
        updated_by: int,
    ) -> Publication:
        """Créer une aide au choix avec au moins deux options."""
        titre = (titre or '').strip()
        description = (description or '').strip()
        if not titre:
            raise ValidationError('Le titre est obligatoire.')
        if not description:
            raise ValidationError('La description est obligatoire.')

        cleaned_options: List[Dict[str, Any]] = []
        for index, raw in enumerate(options or []):
            libelle = (raw.get('libelle') or '').strip()
            if not libelle:
                raise ValidationError('Chaque option doit avoir un libellé.')
            cleaned_options.append(
                {
                    'libelle': libelle,
                    'description': (raw.get('description') or '').strip(),
                    'image_url': (raw.get('image_url') or '').strip(),
                    'position': raw.get('position', index),
                }
            )
        if len(cleaned_options) < 2:
            raise ValidationError('Une aide au choix exige au moins deux options.')

        images = images or []

        with transaction.atomic():
            publication = self.publication_repository.create(
                auteur=auteur,
                type=self.CHOIX_TYPE,
                titre=titre,
                description=description,
                contraintes=(contraintes or '').strip(),
                created_by=created_by,
                updated_by=updated_by,
            )
            self._attach_medias(
                publication=publication,
                images=images,
                created_by=created_by,
                updated_by=updated_by,
            )
            for option in cleaned_options:
                OptionPublication.objects.create(
                    publication=publication,
                    libelle=option['libelle'],
                    description=option['description'],
                    image_url=option['image_url'],
                    position=option['position'],
                    created_by=created_by,
                    updated_by=updated_by,
                )

        return self.get_by_id(publication.id, membre=auteur)

    def create_sondage(
        self,
        *,
        auteur: User,
        titre: str,
        description: str,
        options: List[Dict[str, Any]],
        images: Optional[List[Dict[str, Any]]] = None,
        created_by: int,
        updated_by: int,
    ) -> Publication:
        """Créer un sondage avec au moins deux options de vote."""
        titre = (titre or '').strip()
        description = (description or '').strip()
        if not titre:
            raise ValidationError('Le titre est obligatoire.')
        if not description:
            raise ValidationError('La description est obligatoire.')

        cleaned_options: List[Dict[str, Any]] = []
        for index, raw in enumerate(options or []):
            libelle = (raw.get('libelle') or '').strip()
            if not libelle:
                raise ValidationError('Chaque option doit avoir un libellé.')
            cleaned_options.append(
                {
                    'libelle': libelle,
                    'description': (raw.get('description') or '').strip(),
                    'image_url': (raw.get('image_url') or '').strip(),
                    'position': raw.get('position', index),
                }
            )
        if len(cleaned_options) < 2:
            raise ValidationError('Un sondage exige au moins deux options.')

        images = images or []

        with transaction.atomic():
            publication = self.publication_repository.create(
                auteur=auteur,
                type=self.SONDAGE_TYPE,
                titre=titre,
                description=description,
                created_by=created_by,
                updated_by=updated_by,
            )
            self._attach_medias(
                publication=publication,
                images=images,
                created_by=created_by,
                updated_by=updated_by,
            )
            for option in cleaned_options:
                OptionPublication.objects.create(
                    publication=publication,
                    libelle=option['libelle'],
                    description=option['description'],
                    image_url=option['image_url'],
                    position=option['position'],
                    created_by=created_by,
                    updated_by=updated_by,
                )

        return self.get_by_id(publication.id, membre=auteur)

    def upsert_avis_choix(
        self,
        *,
        publication_id: int,
        option_id: int,
        membre: User,
        explication: str,
    ) -> AvisChoix:
        """Créer ou modifier l'avis / le vote du membre (aide au choix ou sondage)."""
        publication = Publication.objects.filter(id=publication_id).first()
        if publication is None:
            raise Http404('Publication introuvable.')
        if publication.type not in (self.CHOIX_TYPE, self.SONDAGE_TYPE):
            raise ValidationError(
                'Les votes ne concernent que les aides au choix et les sondages.'
            )
        if publication.decided_at is not None:
            raise ValidationError('La décision est déjà publiée : les avis sont fermés.')

        # L'explication est facultative : un clic sur l'option suffit
        explication = (explication or '').strip()

        option = OptionPublication.objects.filter(id=option_id).first()
        if option is None:
            raise Http404('Option introuvable.')
        if option.publication_id != publication.id:
            raise ValidationError('L\'option doit appartenir à cette publication.')

        existing = (
            AvisChoix.objects.filter(membre_id=membre.id, option__publication_id=publication.id)
            .select_related('option')
            .first()
        )
        # Un seul vote définitif par membre : pas de changement après validation
        if existing:
            raise ValidationError('Vous avez déjà validé votre choix sur cette publication.')

        return AvisChoix.objects.create(
            membre=membre,
            option=option,
            explication=explication,
            created_by=membre.id,
            updated_by=membre.id,
        )

    def decider_choix(
        self,
        *,
        publication_id: int,
        option_id: int,
        justification_finale: str,
        auteur: User,
    ) -> Publication:
        """Publier l'option retenue (auteur seul)."""
        publication = Publication.objects.filter(id=publication_id).select_related('auteur').first()
        if publication is None:
            raise Http404('Publication introuvable.')
        if publication.type != self.CHOIX_TYPE:
            raise ValidationError('Seule une aide au choix peut recevoir une décision.')
        if publication.auteur_id != auteur.id:
            raise ValidationError('Seul l\'auteur peut publier la décision.')

        justification = (justification_finale or '').strip()
        if not justification:
            raise ValidationError('La justification finale est obligatoire.')

        option = OptionPublication.objects.filter(id=option_id).first()
        if option is None:
            raise Http404('Option introuvable.')
        if option.publication_id != publication.id:
            raise ValidationError('L\'option retenue doit appartenir à cette publication.')

        publication.option_retenue = option
        publication.justification_finale = justification
        publication.decided_at = timezone.now()
        publication.updated_by = auteur.id
        publication.save(
            update_fields=[
                'option_retenue',
                'justification_finale',
                'decided_at',
                'updated_by',
                'updated_at',
            ]
        )
        return self.get_by_id(publication.id, membre=auteur)

    def list_avis_choix(
        self, *, publication_id: int, membre: Optional[User] = None
    ) -> List[AvisChoix]:
        """Liste les avis d'une aide au choix."""
        publication = Publication.objects.filter(id=publication_id).first()
        if publication is None:
            return []
        return list(
            AvisChoix.objects.filter(option__publication_id=publication_id)
            .select_related('membre', 'option')
            .order_by('created_at', 'id')
        )

    def accepter_reponse(
        self,
        *,
        publication_id: int,
        commentaire_id: Optional[int],
        auteur: User,
    ) -> Publication:
        """
        Accepter, changer ou retirer la réponse technique retenue.
        Seul l'auteur de la publication ENTRAIDE peut le faire.
        """
        publication = Publication.objects.filter(id=publication_id).select_related('auteur').first()
        if publication is None:
            raise Http404('Publication introuvable.')
        if publication.type != self.ENTRAIDE_TYPE:
            raise ValidationError('Seule une entraide technique peut accepter une réponse.')
        if publication.auteur_id != auteur.id:
            raise ValidationError('Seul l\'auteur peut accepter une réponse.')

        if commentaire_id is None:
            publication.reponse_acceptee = None
            publication.updated_by = auteur.id
            publication.save(update_fields=['reponse_acceptee', 'updated_by', 'updated_at'])
            return self.get_by_id(publication.id, membre=auteur)

        commentaire = Commentaire.objects.filter(id=commentaire_id).first()
        if commentaire is None:
            raise Http404('Réponse introuvable.')
        if commentaire.publication_id != publication.id:
            raise ValidationError('La réponse doit appartenir à cette publication.')
        if commentaire.nature != 'REPONSE_TECHNIQUE':
            raise ValidationError('Seule une réponse technique peut être acceptée.')
        if commentaire.parent_id is not None:
            raise ValidationError('Seule une réponse technique racine peut être acceptée.')

        publication.reponse_acceptee = commentaire
        publication.updated_by = auteur.id
        publication.save(update_fields=['reponse_acceptee', 'updated_by', 'updated_at'])
        return self.get_by_id(publication.id, membre=auteur)

    def update(
        self, publication_id: int, publication_data: Dict[str, Any], partial: bool = False
    ) -> Optional[Publication]:
        """Mettre à jour une publication existante."""
        publication = self.publication_repository.get_by_id(publication_id)
        if not publication:
            return None

        if not partial:
            self.validate_data(publication_data)

        # L'auteur et le type restent figés après création
        publication_data.pop('auteur', None)
        publication_data.pop('auteur_id', None)
        publication_data.pop('type', None)
        publication_data.pop('images_data', None)
        publication_data.pop('reponse_acceptee', None)
        publication_data.pop('reponse_acceptee_id', None)
        publication_data.pop('option_retenue', None)
        publication_data.pop('option_retenue_id', None)
        publication_data.pop('options_data', None)

        if 'lien_app' in publication_data and publication.type == self.APPLICATION_TYPE:
            publication_data['lien_app'] = self._validate_http_url(publication_data['lien_app'])

        self.publication_repository.update(publication, **publication_data)
        return self.get_by_id(publication_id)

    def delete(self, publication_id: int) -> bool:
        """Supprimer une publication."""
        publication = self.publication_repository.get_by_id(publication_id)
        if not publication:
            return False
        return self.publication_repository.delete(publication)

    def validate_data(self, publication_data: Dict[str, Any]):
        """Valider les données du publication."""
        if 'type' in publication_data:
            _valid_type = ['DISCUSSION', 'APPLICATION', 'ENTRAIDE', 'CHOIX', 'SONDAGE']
            if publication_data['type'] not in _valid_type:
                raise ValidationError('Valeur invalide pour le champ type')
        if 'plateforme_app' in publication_data and publication_data['plateforme_app']:
            _valid_plateforme_app = ['WEB', 'MOBILE', 'LES_DEUX']
            if publication_data['plateforme_app'] not in _valid_plateforme_app:
                raise ValidationError('Valeur invalide pour le champ plateforme_app')
        if 'mode_vote' in publication_data and publication_data['mode_vote']:
            _valid_mode_vote = ['UNIQUE', 'MULTIPLE']
            if publication_data['mode_vote'] not in _valid_mode_vote:
                raise ValidationError('Valeur invalide pour le champ mode_vote')
