"""
Espace service layer pour les opérations de logique métier.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone

from app.communaute.models import (
    Espace,
    LienInvitation,
    MessageGroupe,
    ParticipationEspace,
    ReactionMessageGroupe,
)
from app.communaute.repositories.espace_repository import EspaceRepository
from app.core.models import User


@dataclass(frozen=True)
class EspaceAccess:
    """Résultat du contrôle d'accès à un espace."""

    espace: Espace
    participation: Optional[ParticipationEspace]
    can_read: bool
    can_interact: bool
    can_publish: bool
    via_preview: bool


class EspaceService:
    """
    Classe de service pour la logique métier liée aux espaces.
    """

    TYPE_COMMUNAUTE = 'COMMUNAUTE'
    TYPE_CHAINE = 'CHAINE'
    ACCES_PUBLIC = 'PUBLIC'
    ACCES_LIEN = 'LIEN'

    def __init__(self):
        self.espace_repository = EspaceRepository()

    @staticmethod
    def hash_invite_code(code: str) -> str:
        return hashlib.sha256(str(code).strip().encode('utf-8')).hexdigest()

    def get_all(
        self,
        search: Optional[str] = None,
        ordering: Optional[str] = None,
        type_filter: Optional[str] = None,
        acces_filter: Optional[str] = None,
        visible_for: Optional[User] = None,
    ) -> QuerySet:
        """
        Liste des espaces. Par défaut : publics découvrables.
        Les espaces LIEN n'apparaissent que si l'acteur en est membre.
        Les espaces de l'acteur sont remontés en premier.
        """
        from django.db.models import BooleanField, Case, Exists, OuterRef, Q, Value, When

        qs = self.espace_repository.get_all(search=search, ordering=None)
        if type_filter:
            qs = qs.filter(type=type_filter)
        if acces_filter:
            qs = qs.filter(acces=acces_filter)
        elif visible_for is not None:
            qs = qs.filter(
                Q(acces=self.ACCES_PUBLIC)
                | Q(participations__membre_id=visible_for.id)
            ).distinct()
        else:
            qs = qs.filter(acces=self.ACCES_PUBLIC)

        extra_ordering = []
        if ordering:
            if ordering.lstrip('-') not in (
                'id',
                'type',
                'nom',
                'description',
                'acces',
                'created_at',
                'updated_at',
            ):
                raise ValueError(f'Tri non autorisé : {ordering}')
            extra_ordering = [ordering]

        if visible_for is not None and getattr(visible_for, 'id', None):
            member_exists = ParticipationEspace.objects.filter(
                espace_id=OuterRef('pk'),
                membre_id=visible_for.id,
            )
            qs = qs.annotate(
                est_membre=Case(
                    When(Exists(member_exists), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            return qs.order_by(
                '-est_membre', *(extra_ordering or ['-created_at']), 'id'
            )

        return qs.order_by(*(extra_ordering or ['-created_at']), 'id')

    def get_by_id(self, espace_id: int) -> Optional[Espace]:
        return self.espace_repository.get_by_id(espace_id)

    def get_participation(
        self, *, espace_id: int, membre_id: int
    ) -> Optional[ParticipationEspace]:
        return (
            ParticipationEspace.objects.filter(
                espace_id=espace_id, membre_id=membre_id
            )
            .select_related('espace', 'membre')
            .first()
        )

    def _assert_admin(self, *, espace: Espace, acteur: User) -> ParticipationEspace:
        participation = self.get_participation(
            espace_id=espace.id, membre_id=acteur.id
        )
        if participation is None or participation.role not in (
            ParticipationEspace.ROLE_SUPER_ADMIN,
            ParticipationEspace.ROLE_ADMIN,
        ):
            raise ValidationError('Réservé aux administrateurs de la communauté.')
        return participation

    def _assert_super_admin(
        self, *, espace: Espace, acteur: User
    ) -> ParticipationEspace:
        participation = self.get_participation(
            espace_id=espace.id, membre_id=acteur.id
        )
        if (
            participation is None
            or participation.role != ParticipationEspace.ROLE_SUPER_ADMIN
        ):
            raise ValidationError(
                'Réservé au super administrateur de la communauté.'
            )
        return participation

    def resolve_access(
        self,
        *,
        espace: Espace,
        acteur: User,
        invite_code: Optional[str] = None,
    ) -> EspaceAccess:
        participation = self.get_participation(
            espace_id=espace.id, membre_id=acteur.id
        )
        if participation is not None:
            can_publish = True
            if espace.type == self.TYPE_CHAINE:
                can_publish = participation.role in (
                    ParticipationEspace.ROLE_SUPER_ADMIN,
                    ParticipationEspace.ROLE_ADMIN,
                )
            elif not espace.membres_peuvent_publier:
                can_publish = participation.role in (
                    ParticipationEspace.ROLE_SUPER_ADMIN,
                    ParticipationEspace.ROLE_ADMIN,
                )
            return EspaceAccess(
                espace=espace,
                participation=participation,
                can_read=True,
                can_interact=True,
                can_publish=can_publish,
                via_preview=False,
            )

        if espace.acces == self.ACCES_PUBLIC:
            return EspaceAccess(
                espace=espace,
                participation=None,
                can_read=True,
                can_interact=False,
                can_publish=False,
                via_preview=False,
            )

        lien = self.find_active_lien(invite_code) if invite_code else None
        if lien is None or lien.espace_id != espace.id:
            return EspaceAccess(
                espace=espace,
                participation=None,
                can_read=False,
                can_interact=False,
                can_publish=False,
                via_preview=False,
            )

        return EspaceAccess(
            espace=espace,
            participation=None,
            can_read=bool(lien.previsualisation_autorisee),
            can_interact=False,
            can_publish=False,
            via_preview=bool(lien.previsualisation_autorisee),
        )

    def assert_can_read(
        self,
        *,
        espace: Espace,
        acteur: User,
        invite_code: Optional[str] = None,
    ) -> EspaceAccess:
        access = self.resolve_access(
            espace=espace, acteur=acteur, invite_code=invite_code
        )
        if not access.can_read:
            raise ValidationError('Tu n’as pas accès à cet espace.')
        return access

    def assert_can_interact(
        self, *, espace: Espace, acteur: User
    ) -> ParticipationEspace:
        access = self.resolve_access(espace=espace, acteur=acteur)
        if not access.can_interact or access.participation is None:
            raise ValidationError(
                'Tu dois être membre pour liker ou commenter ici.'
            )
        return access.participation

    def create_espace(
        self,
        *,
        createur: User,
        nom: str,
        description: str = '',
        type_espace: str = TYPE_COMMUNAUTE,
        membres_peuvent_publier: bool = True,
        acces: str = ACCES_PUBLIC,
        commentaires_ouverts: bool = True,
    ) -> Espace:
        """
        Crée une communauté ou une chaîne + participation SUPER_ADMIN du créateur.
        """
        nom = (nom or '').strip()
        if not nom:
            raise ValidationError('Le nom est obligatoire.')
        if len(nom) > 120:
            raise ValidationError('Le nom ne peut pas dépasser 120 caractères.')
        type_value = (type_espace or self.TYPE_COMMUNAUTE).strip().upper()
        if type_value not in (self.TYPE_COMMUNAUTE, self.TYPE_CHAINE):
            raise ValidationError('Type d’espace invalide.')
        acces_value = (acces or self.ACCES_PUBLIC).strip().upper()
        if acces_value not in (self.ACCES_PUBLIC, self.ACCES_LIEN):
            raise ValidationError('Accès invalide.')

        # Chaîne : seuls les admins publient (règle produit Phase 11)
        if type_value == self.TYPE_CHAINE:
            membres_peuvent_publier = False

        with transaction.atomic():
            espace = self.espace_repository.create(
                type=type_value,
                nom=nom,
                description=(description or '').strip(),
                acces=acces_value,
                membres_peuvent_publier=bool(membres_peuvent_publier),
                commentaires_ouverts=bool(commentaires_ouverts),
                created_by=createur.id,
                updated_by=createur.id,
            )
            ParticipationEspace.objects.create(
                espace=espace,
                membre=createur,
                role=ParticipationEspace.ROLE_SUPER_ADMIN,
                created_by=createur.id,
                updated_by=createur.id,
            )
            return espace

    def create_communaute(self, **kwargs) -> Espace:
        kwargs.setdefault('type_espace', self.TYPE_COMMUNAUTE)
        return self.create_espace(**kwargs)

    def create_chaine(
        self,
        *,
        createur: User,
        nom: str,
        description: str = '',
        acces: str = ACCES_PUBLIC,
        commentaires_ouverts: bool = True,
    ) -> Espace:
        """Crée une chaîne publique (ou par lien) — admins seuls publient."""
        return self.create_espace(
            createur=createur,
            nom=nom,
            description=description,
            type_espace=self.TYPE_CHAINE,
            membres_peuvent_publier=False,
            acces=acces,
            commentaires_ouverts=commentaires_ouverts,
        )

    def create_communaute_publique(self, **kwargs) -> Espace:
        kwargs.setdefault('acces', self.ACCES_PUBLIC)
        return self.create_communaute(**kwargs)

    def rejoindre_communaute_publique(
        self, *, espace: Espace, membre: User
    ) -> ParticipationEspace:
        if espace.type != self.TYPE_COMMUNAUTE:
            raise ValidationError('Seules les communautés peuvent être rejointes ainsi.')
        if espace.acces != self.ACCES_PUBLIC:
            raise ValidationError(
                'Cette communauté n’est pas publique. Utilise un lien d’invitation.'
            )
        return self._rejoindre(espace=espace, membre=membre)

    def s_abonner_chaine(
        self, *, espace: Espace, membre: User
    ) -> ParticipationEspace:
        """Abonnement idempotent à une chaîne publique."""
        if espace.type != self.TYPE_CHAINE:
            raise ValidationError('Cet espace n’est pas une chaîne.')
        if espace.acces != self.ACCES_PUBLIC:
            raise ValidationError(
                'Cette chaîne n’est pas publique. Utilise un lien d’invitation.'
            )
        return self._rejoindre(espace=espace, membre=membre)

    def se_desabonner(
        self, *, espace: Espace, membre: User
    ) -> None:
        """
        Quitte un espace (communauté ou chaîne).
        Le SUPER_ADMIN ne peut pas partir tant que l'espace existe.
        """
        participation = self.get_participation(
            espace_id=espace.id, membre_id=membre.id
        )
        if participation is None:
            return
        if participation.role == ParticipationEspace.ROLE_SUPER_ADMIN:
            raise ValidationError(
                'Le créateur super administrateur ne peut pas quitter cet espace.'
            )
        participation.delete()

    def exclure_membre(
        self, *, espace: Espace, acteur: User, membre_id: int
    ) -> None:
        """
        Retire un membre (style WhatsApp). Impossible sur le SUPER_ADMIN.
        Super admin : tout membre/admin. Admin : membres seulement.
        """
        acteur_part = self.get_participation(
            espace_id=espace.id, membre_id=acteur.id
        )
        if acteur_part is None or acteur_part.role not in (
            ParticipationEspace.ROLE_SUPER_ADMIN,
            ParticipationEspace.ROLE_ADMIN,
        ):
            raise ValidationError('Réservé aux administrateurs.')

        if int(membre_id) == acteur.id:
            raise ValidationError('Utilise « Quitter » pour partir toi-même.')

        cible = self.get_participation(
            espace_id=espace.id, membre_id=membre_id
        )
        if cible is None:
            raise ValidationError('Ce membre ne fait pas partie de l’espace.')
        if cible.role == ParticipationEspace.ROLE_SUPER_ADMIN:
            raise ValidationError(
                'Le créateur super administrateur ne peut pas être retiré.'
            )
        if (
            acteur_part.role == ParticipationEspace.ROLE_ADMIN
            and cible.role == ParticipationEspace.ROLE_ADMIN
        ):
            raise ValidationError(
                'Seul le super administrateur peut retirer un autre admin.'
            )
        cible.delete()

    def update_infos(
        self,
        *,
        espace: Espace,
        acteur: User,
        nom: Optional[str] = None,
        description: Optional[str] = None,
        photo: Optional[str] = None,
    ) -> Espace:
        """Met à jour nom / description / photo (admins)."""
        self._assert_admin(espace=espace, acteur=acteur)
        fields = ['updated_by', 'updated_at']
        if nom is not None:
            cleaned = nom.strip()
            if not cleaned:
                raise ValidationError('Le nom est obligatoire.')
            if len(cleaned) > 120:
                raise ValidationError('Le nom ne peut pas dépasser 120 caractères.')
            espace.nom = cleaned
            fields.append('nom')
        if description is not None:
            espace.description = description.strip()
            fields.append('description')
        if photo is not None:
            espace.photo = (photo or '').strip()[:500]
            fields.append('photo')
        espace.updated_by = acteur.id
        espace.save(update_fields=fields)
        return espace

    def _rejoindre(self, *, espace: Espace, membre: User) -> ParticipationEspace:
        existing = self.get_participation(espace_id=espace.id, membre_id=membre.id)
        if existing is not None:
            return existing
        try:
            with transaction.atomic():
                return ParticipationEspace.objects.create(
                    espace=espace,
                    membre=membre,
                    role=ParticipationEspace.ROLE_MEMBRE,
                    created_by=membre.id,
                    updated_by=membre.id,
                )
        except IntegrityError:
            raced = self.get_participation(espace_id=espace.id, membre_id=membre.id)
            if raced is not None:
                return raced
            raise

    def find_active_lien(self, code: Optional[str]) -> Optional[LienInvitation]:
        raw = (code or '').strip()
        if not raw:
            return None
        return (
            LienInvitation.objects.filter(
                code_hash=self.hash_invite_code(raw),
                revoked_at__isnull=True,
            )
            .select_related('espace')
            .first()
        )

    def create_lien(
        self,
        *,
        espace: Espace,
        acteur: User,
        previsualisation_autorisee: bool = False,
    ) -> Tuple[LienInvitation, str]:
        """
        Crée un lien d'invitation. Retourne (lien, code_brut) — le code n'est
        jamais stocké en clair.
        """
        self._assert_admin(espace=espace, acteur=acteur)
        if espace.acces != self.ACCES_LIEN:
            raise ValidationError(
                'Passe l’espace en accès « par lien » avant de créer une invitation.'
            )
        code = secrets.token_urlsafe(24)
        lien = LienInvitation.objects.create(
            espace=espace,
            cree_par=acteur,
            code_hash=self.hash_invite_code(code),
            previsualisation_autorisee=bool(previsualisation_autorisee),
            created_by=acteur.id,
            updated_by=acteur.id,
        )
        return lien, code

    def list_liens(self, *, espace: Espace, acteur: User) -> QuerySet:
        self._assert_admin(espace=espace, acteur=acteur)
        return LienInvitation.objects.filter(espace=espace).order_by('-created_at')

    def revoquer_lien(
        self, *, espace: Espace, acteur: User, lien_id: int
    ) -> LienInvitation:
        self._assert_admin(espace=espace, acteur=acteur)
        lien = LienInvitation.objects.filter(pk=lien_id, espace=espace).first()
        if lien is None:
            raise ValidationError('Lien introuvable.')
        if lien.revoked_at is None:
            lien.revoked_at = timezone.now()
            lien.updated_by = acteur.id
            lien.save(update_fields=['revoked_at', 'updated_by', 'updated_at'])
        return lien

    def preview_invitation(self, *, code: str, acteur: User) -> Dict[str, Any]:
        lien = self.find_active_lien(code)
        if lien is None:
            raise ValidationError('Lien d’invitation invalide ou révoqué.')
        participation = self.get_participation(
            espace_id=lien.espace_id, membre_id=acteur.id
        )
        return {
            'espace_id': lien.espace_id,
            'espace_nom': lien.espace.nom,
            'espace_description': lien.espace.description,
            'previsualisation_autorisee': lien.previsualisation_autorisee,
            'deja_membre': participation is not None,
            'mon_role': participation.role if participation else None,
        }

    def rejoindre_via_lien(
        self, *, code: str, membre: User
    ) -> ParticipationEspace:
        lien = self.find_active_lien(code)
        if lien is None:
            raise ValidationError('Lien d’invitation invalide ou révoqué.')
        if lien.espace.type not in (self.TYPE_COMMUNAUTE, self.TYPE_CHAINE):
            raise ValidationError('Invitation invalide pour ce type d’espace.')
        return self._rejoindre(espace=lien.espace, membre=membre)

    def set_membres_peuvent_publier(
        self, *, espace: Espace, acteur: User, value: bool
    ) -> Espace:
        self._assert_super_admin(espace=espace, acteur=acteur)
        if espace.type == self.TYPE_CHAINE:
            raise ValidationError(
                'Sur une chaîne, seuls les administrateurs publient.'
            )
        espace.membres_peuvent_publier = bool(value)
        espace.updated_by = acteur.id
        espace.save(
            update_fields=['membres_peuvent_publier', 'updated_by', 'updated_at']
        )
        return espace

    def set_acces(self, *, espace: Espace, acteur: User, acces: str) -> Espace:
        self._assert_super_admin(espace=espace, acteur=acteur)
        acces_value = (acces or '').strip().upper()
        if acces_value not in (self.ACCES_PUBLIC, self.ACCES_LIEN):
            raise ValidationError('Accès invalide.')
        espace.acces = acces_value
        espace.updated_by = acteur.id
        espace.save(update_fields=['acces', 'updated_by', 'updated_at'])
        return espace

    def set_commentaires_ouverts(
        self, *, espace: Espace, acteur: User, value: bool
    ) -> Espace:
        """Ouvre ou ferme les commentaires des publications d'une chaîne."""
        self._assert_super_admin(espace=espace, acteur=acteur)
        if espace.type != self.TYPE_CHAINE:
            raise ValidationError(
                'Le réglage des commentaires concerne uniquement les chaînes.'
            )
        espace.commentaires_ouverts = bool(value)
        espace.updated_by = acteur.id
        espace.save(
            update_fields=['commentaires_ouverts', 'updated_by', 'updated_at']
        )
        return espace

    def list_membres(self, *, espace: Espace, acteur: User) -> QuerySet:
        access = self.resolve_access(espace=espace, acteur=acteur)
        if not access.can_interact:
            raise ValidationError('Réservé aux membres de la communauté.')
        return (
            ParticipationEspace.objects.filter(espace=espace)
            .select_related('membre')
            .order_by('joined_at', 'id')
        )

    def set_membre_role(
        self,
        *,
        espace: Espace,
        acteur: User,
        membre_id: int,
        role: str,
    ) -> ParticipationEspace:
        """
        Nomme ou rétrograde un admin. Le SUPER_ADMIN ne peut jamais être modifié.
        """
        self._assert_super_admin(espace=espace, acteur=acteur)
        role_value = (role or '').strip().upper()
        if role_value not in (
            ParticipationEspace.ROLE_ADMIN,
            ParticipationEspace.ROLE_MEMBRE,
        ):
            raise ValidationError('Rôle invalide (ADMIN ou MEMBRE).')

        cible = self.get_participation(espace_id=espace.id, membre_id=membre_id)
        if cible is None:
            raise ValidationError('Ce membre ne fait pas partie de la communauté.')
        if cible.role == ParticipationEspace.ROLE_SUPER_ADMIN:
            raise ValidationError(
                'Le créateur super administrateur ne peut pas être modifié.'
            )
        if cible.membre_id == acteur.id:
            raise ValidationError('Tu ne peux pas modifier ton propre rôle.')

        cible.role = role_value
        cible.updated_by = acteur.id
        cible.save(update_fields=['role', 'updated_by', 'updated_at'])
        return cible

    EMOJIS_REACTION = frozenset({'👍', '❤️', '😂', '😮', '😢', '🙏'})

    def list_messages_groupe(
        self, *, espace: Espace, acteur: User
    ) -> QuerySet:
        """Messages du chat de communauté — réservé aux membres."""
        if espace.type != self.TYPE_COMMUNAUTE:
            raise ValidationError(
                'Le chat de groupe est réservé aux communautés.'
            )
        self.assert_can_interact(espace=espace, acteur=acteur)
        return (
            MessageGroupe.objects.filter(espace=espace)
            .select_related('auteur', 'reply_to', 'reply_to__auteur')
            .prefetch_related('reactions')
            .order_by('sent_at', 'id')
        )

    def envoyer_message_groupe(
        self,
        *,
        espace: Espace,
        auteur: User,
        texte: str,
        reply_to_id: Optional[int] = None,
    ) -> MessageGroupe:
        if espace.type != self.TYPE_COMMUNAUTE:
            raise ValidationError(
                'Le chat de groupe est réservé aux communautés.'
            )
        access = self.resolve_access(espace=espace, acteur=auteur)
        if not access.can_interact or access.participation is None:
            raise ValidationError(
                'Tu dois rejoindre cette communauté pour y écrire.'
            )
        if not access.can_publish:
            raise ValidationError(
                'Seuls les administrateurs peuvent écrire dans cette communauté.'
            )
        cleaned = (texte or '').strip()
        if not cleaned:
            raise ValidationError('Le message ne peut pas être vide.')
        if len(cleaned) > 5000:
            raise ValidationError('Message trop long (max 5000 caractères).')

        reply_to = None
        if reply_to_id is not None:
            reply_to = (
                MessageGroupe.objects.filter(
                    id=reply_to_id, espace=espace
                )
                .select_related('auteur')
                .first()
            )
            if reply_to is None:
                raise ValidationError(
                    'Le message auquel tu réponds est introuvable.'
                )

        return MessageGroupe.objects.create(
            espace=espace,
            auteur=auteur,
            texte=cleaned,
            reply_to=reply_to,
            created_by=auteur.id,
            updated_by=auteur.id,
        )

    def supprimer_message_groupe(
        self, *, espace: Espace, acteur: User, message_id: int
    ) -> MessageGroupe:
        """Suppression douce (auteur ou admin)."""
        self.assert_can_interact(espace=espace, acteur=acteur)
        message = (
            MessageGroupe.objects.filter(id=message_id, espace=espace)
            .select_related('auteur', 'reply_to', 'reply_to__auteur')
            .first()
        )
        if message is None:
            raise ValidationError('Message introuvable.')
        if message.supprime_at is not None:
            return message

        access = self.resolve_access(espace=espace, acteur=acteur)
        is_admin = bool(
            access.participation
            and access.participation.role
            in (
                ParticipationEspace.ROLE_SUPER_ADMIN,
                ParticipationEspace.ROLE_ADMIN,
            )
        )
        if message.auteur_id != acteur.id and not is_admin:
            raise ValidationError(
                'Tu ne peux supprimer que tes propres messages.'
            )

        message.texte = ''
        message.supprime_at = timezone.now()
        message.updated_by = acteur.id
        message.save(
            update_fields=['texte', 'supprime_at', 'updated_by', 'updated_at']
        )
        return message

    def toggle_reaction_message_groupe(
        self,
        *,
        espace: Espace,
        acteur: User,
        message_id: int,
        emoji: str,
    ) -> MessageGroupe:
        """Ajoute, change ou retire une réaction emoji sur un message."""
        self.assert_can_interact(espace=espace, acteur=acteur)
        cleaned = (emoji or '').strip()
        if cleaned not in self.EMOJIS_REACTION:
            raise ValidationError('Réaction non autorisée.')

        message = (
            MessageGroupe.objects.filter(id=message_id, espace=espace)
            .select_related('auteur', 'reply_to', 'reply_to__auteur')
            .prefetch_related('reactions')
            .first()
        )
        if message is None:
            raise ValidationError('Message introuvable.')
        if message.supprime_at is not None:
            raise ValidationError(
                'Impossible de réagir à un message supprimé.'
            )

        try:
            with transaction.atomic():
                existing = (
                    ReactionMessageGroupe.objects.select_for_update()
                    .filter(message=message, membre=acteur)
                    .first()
                )
                if existing is not None and existing.emoji == cleaned:
                    existing.delete()
                elif existing is not None:
                    existing.emoji = cleaned
                    existing.updated_by = acteur.id
                    existing.save(
                        update_fields=['emoji', 'updated_by', 'updated_at']
                    )
                else:
                    ReactionMessageGroupe.objects.create(
                        message=message,
                        membre=acteur,
                        emoji=cleaned,
                        created_by=acteur.id,
                        updated_by=acteur.id,
                    )
        except IntegrityError:
            # Double-clic concurrent : on retombe sur l'état final cohérent.
            raced = ReactionMessageGroupe.objects.filter(
                message=message, membre=acteur
            ).first()
            if raced is None:
                raise

        return (
            MessageGroupe.objects.filter(id=message.id)
            .select_related('auteur', 'reply_to', 'reply_to__auteur')
            .prefetch_related('reactions')
            .get()
        )

    def assert_can_publish(self, *, espace: Espace, membre: User) -> ParticipationEspace:
        access = self.resolve_access(espace=espace, acteur=membre)
        if not access.can_publish or access.participation is None:
            if access.participation is None:
                raise ValidationError(
                    'Tu dois rejoindre cette communauté pour y publier.'
                )
            raise ValidationError(
                'Seuls les administrateurs peuvent publier dans cette communauté.'
            )
        return access.participation

    def create(self, espace_data: Dict[str, Any]) -> Espace:
        self.validate_data(espace_data)
        return self.espace_repository.create(**espace_data)

    def update(
        self, espace_id: int, espace_data: Dict[str, Any], partial: bool = False
    ) -> Optional[Espace]:
        espace = self.espace_repository.get_by_id(espace_id)
        if not espace:
            return None
        if not partial:
            self.validate_data(espace_data)
        return self.espace_repository.update(espace, **espace_data)

    def delete(self, espace_id: int) -> bool:
        espace = self.espace_repository.get_by_id(espace_id)
        if not espace:
            return False
        return self.espace_repository.delete(espace)

    def validate_data(self, espace_data: Dict[str, Any]):
        if 'type' in espace_data:
            if espace_data['type'] not in [self.TYPE_COMMUNAUTE, self.TYPE_CHAINE]:
                raise ValidationError('Valeur invalide pour le champ type')
        if 'acces' in espace_data:
            if espace_data['acces'] not in [self.ACCES_PUBLIC, self.ACCES_LIEN]:
                raise ValidationError('Valeur invalide pour le champ acces')
