"""
Commentaire service layer pour les opérations de logique métier.
"""
from typing import Optional, Dict, Any, List
from django.db.models import QuerySet, Prefetch, Count, Q
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from app.communaute.models import Commentaire, MediaCommentaire, Publication
from app.communaute.repositories.commentaire_repository import CommentaireRepository

User = get_user_model()


class CommentaireService:
    """Service métier des commentaires et réponses."""

    NATURE_COMMENTAIRE = 'COMMENTAIRE'
    NATURE_REPONSE_TECHNIQUE = 'REPONSE_TECHNIQUE'
    MEDIA_KINDS = (
        MediaCommentaire.KIND_IMAGE,
        MediaCommentaire.KIND_VIDEO,
        MediaCommentaire.KIND_AUDIO,
    )

    def __init__(self):
        self.commentaire_repository = CommentaireRepository()

    def _engagement_annotations(self, membre: Optional[User] = None) -> Dict[str, Any]:
        annotations = {
            'likes_count': Count('likes', distinct=True),
            'confirmations_count': Count('confirmations_aide', distinct=True),
        }
        if membre and getattr(membre, 'is_authenticated', False) and membre.id:
            annotations['liked_by_me'] = Count(
                'likes',
                filter=Q(likes__membre_id=membre.id),
                distinct=True,
            )
            annotations['confirmed_by_me'] = Count(
                'confirmations_aide',
                filter=Q(confirmations_aide__membre_id=membre.id),
                distinct=True,
            )
        return annotations

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        return self.commentaire_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, commentaire_id: int, membre: Optional[User] = None) -> Optional[Commentaire]:
        return (
            Commentaire.objects.filter(id=commentaire_id)
            .select_related('auteur', 'publication', 'parent', 'option')
            .prefetch_related('medias')
            .annotate(**self._engagement_annotations(membre))
            .first()
        )

    def list_for_publication(self, publication_id: int, membre: Optional[User] = None):
        """Retourne les commentaires racines d'une publication avec leurs réponses (QuerySet)."""
        if not Publication.objects.filter(id=publication_id).exists():
            return Commentaire.objects.none()

        annotations = self._engagement_annotations(membre)
        medias_qs = MediaCommentaire.objects.order_by('position', 'id')

        reponses_qs = (
            Commentaire.objects.filter(parent__isnull=False)
            .select_related('auteur', 'option')
            .prefetch_related(Prefetch('medias', queryset=medias_qs))
            .annotate(**annotations)
            .order_by('created_at', 'id')
        )
        return (
            Commentaire.objects.filter(publication_id=publication_id, parent__isnull=True)
            .select_related('auteur', 'option')
            .annotate(**annotations)
            .prefetch_related(
                Prefetch('medias', queryset=medias_qs),
                Prefetch('reponses', queryset=reponses_qs),
            )
            .order_by('created_at', 'id')
        )

    NATURE_RETOUR_APP = 'RETOUR_APP'

    def create_commentaire(
        self,
        *,
        publication_id: int,
        auteur: User,
        texte: str,
        parent_id: Optional[int] = None,
        option_id: Optional[int] = None,
        created_by: int,
        updated_by: int,
        nature: str = NATURE_COMMENTAIRE,
        est_anonyme: bool = False,
        medias: Optional[List[Dict[str, Any]]] = None,
    ) -> Commentaire:
        """Créer un commentaire, un retour d'app ou une réponse sur une publication."""
        from app.communaute.models import OptionPublication
        from django.db import transaction

        texte = (texte or '').strip()
        medias = medias or []
        if len(medias) > 4:
            raise ValidationError('Un commentaire accepte au plus 4 médias.')
        if not texte and not medias:
            raise ValidationError(
                'Le commentaire doit contenir un texte ou un média.'
            )

        publication = (
            Publication.objects.filter(id=publication_id)
            .select_related('espace')
            .first()
        )
        if publication is None:
            raise ValidationError('Publication introuvable.')
        if publication.espace_id:
            from app.communaute.services.espace_service import EspaceService

            EspaceService().assert_can_interact(
                espace=publication.espace, acteur=auteur
            )
            if (
                publication.espace.type == EspaceService.TYPE_CHAINE
                and not publication.espace.commentaires_ouverts
            ):
                raise ValidationError(
                    'Les commentaires sont fermés sur cette chaîne.'
                )

        parent = None
        if parent_id is not None:
            parent = Commentaire.objects.filter(id=parent_id).select_related('publication').first()
            if parent is None:
                raise ValidationError('Commentaire parent introuvable.')
            if parent.publication_id != publication.id:
                raise ValidationError(
                    'Le commentaire parent doit appartenir à la même publication.'
                )
            # Style Facebook : répondre à une réponse rattache toujours au commentaire racine
            if parent.parent_id is not None:
                root = Commentaire.objects.filter(id=parent.parent_id).first()
                if root is None or root.publication_id != publication.id:
                    raise ValidationError('Commentaire parent introuvable.')
                parent = root

        if nature not in ('COMMENTAIRE', 'RETOUR_APP', 'REPONSE_TECHNIQUE'):
            raise ValidationError('Nature de commentaire invalide.')

        # Les retours anonymes ne concernent que les publications APPLICATION, à la racine
        anonymat = bool(est_anonyme)
        if anonymat:
            if publication.type != 'APPLICATION':
                raise ValidationError(
                    'Le retour anonyme n\'est disponible que sur une application partagée.'
                )
            if parent is not None:
                raise ValidationError('Une réponse ne peut pas être anonyme.')
            nature = self.NATURE_RETOUR_APP

        if nature == self.NATURE_RETOUR_APP and publication.type != 'APPLICATION':
            raise ValidationError(
                'Un retour d\'application ne peut être posté que sur une publication APPLICATION.'
            )

        if nature == self.NATURE_REPONSE_TECHNIQUE:
            if publication.type != 'ENTRAIDE':
                raise ValidationError(
                    'Une réponse technique ne peut être postée que sur une entraide.'
                )
            if parent is not None:
                raise ValidationError(
                    'Une réponse technique doit être à la racine de la publication.'
                )

        # Les réponses imbriquées restent des commentaires ordinaires (non anonymes)
        if parent is not None and nature in (self.NATURE_RETOUR_APP, self.NATURE_REPONSE_TECHNIQUE):
            nature = self.NATURE_COMMENTAIRE

        option = None
        if option_id is not None:
            if publication.type != 'CHOIX':
                raise ValidationError(
                    'Une option ne peut être liée qu\'à un commentaire de débat.'
                )
            option = OptionPublication.objects.filter(
                id=option_id, publication_id=publication.id
            ).first()
            if option is None:
                raise ValidationError('Option introuvable pour cette publication.')
            # Les réponses héritent du contexte du fil ; pas d'option distincte
            if parent is not None:
                option = None

        with transaction.atomic():
            commentaire = self.commentaire_repository.create(
                publication=publication,
                auteur=auteur,
                parent=parent,
                option=option,
                nature=nature,
                texte=texte or '',
                est_anonyme=anonymat,
                created_by=created_by,
                updated_by=updated_by,
            )
            for index, media in enumerate(medias):
                url = (media.get('url') or '').strip()
                if not url:
                    raise ValidationError('Chaque média doit avoir une URL.')
                kind = str(
                    media.get('kind') or MediaCommentaire.KIND_IMAGE
                ).upper()
                if kind not in self.MEDIA_KINDS:
                    raise ValidationError(
                        'Type de média invalide (IMAGE, VIDEO ou AUDIO).'
                    )
                MediaCommentaire.objects.create(
                    commentaire=commentaire,
                    kind=kind,
                    url=url,
                    texte_alternatif=(media.get('texte_alternatif') or '').strip(),
                    position=media.get('position', index),
                    created_by=created_by,
                    updated_by=updated_by,
                )
        return self.get_by_id(commentaire.id, membre=auteur)

    def create(self, commentaire_data: Dict[str, Any]) -> Commentaire:
        self.validate_data(commentaire_data)
        return self.commentaire_repository.create(**commentaire_data)

    def update(
        self, commentaire_id: int, commentaire_data: Dict[str, Any], partial: bool = False
    ) -> Optional[Commentaire]:
        commentaire = self.commentaire_repository.get_by_id(commentaire_id)
        if not commentaire:
            return None
        if not partial:
            self.validate_data(commentaire_data)
        commentaire_data.pop('publication', None)
        commentaire_data.pop('auteur', None)
        commentaire_data.pop('parent', None)
        return self.commentaire_repository.update(commentaire, **commentaire_data)

    def delete(self, commentaire_id: int) -> bool:
        commentaire = self.commentaire_repository.get_by_id(commentaire_id)
        if not commentaire:
            return False
        return self.commentaire_repository.delete(commentaire)

    def validate_data(self, commentaire_data: Dict[str, Any]):
        if 'nature' in commentaire_data:
            valid = ['COMMENTAIRE', 'RETOUR_APP', 'REPONSE_TECHNIQUE']
            if commentaire_data['nature'] not in valid:
                raise ValidationError('Valeur invalide pour le champ nature')
