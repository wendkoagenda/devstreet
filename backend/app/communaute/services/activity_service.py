"""
Compteurs d'activité non lue (messages, communautés, chaînes).
"""
from __future__ import annotations

from typing import Dict

from django.db.models import Q
from django.utils import timezone

from app.communaute.models import (
    Conversation,
    Message,
    MessageGroupe,
    ParticipationEspace,
    Publication,
)
from app.core.models import User


class ActivityService:
    """Agrège les badges de nouveaux contenus pour la sidebar."""

    def badges_for(self, acteur: User) -> Dict[str, int]:
        return {
            'messages': self._unread_dm_conversations(acteur),
            'communautes': self._unread_communautes(acteur),
            'chaines': self._unread_chaines(acteur),
        }

    def mark_conversation_read(
        self, *, conversation: Conversation, acteur: User
    ) -> None:
        now = timezone.now()
        if conversation.membre_1_id == acteur.id:
            Conversation.objects.filter(pk=conversation.pk).update(
                membre_1_lu_at=now
            )
        elif conversation.membre_2_id == acteur.id:
            Conversation.objects.filter(pk=conversation.pk).update(
                membre_2_lu_at=now
            )

    def mark_espace_read(self, *, espace_id: int, acteur: User) -> None:
        ParticipationEspace.objects.filter(
            espace_id=espace_id, membre_id=acteur.id
        ).update(lu_at=timezone.now())

    def conversation_has_unread(
        self, *, conversation: Conversation, acteur: User
    ) -> bool:
        """True s'il reste au moins un message reçu non lu dans la conversation."""
        lu_at = (
            conversation.membre_1_lu_at
            if conversation.membre_1_id == acteur.id
            else conversation.membre_2_lu_at
        )
        qs = Message.objects.filter(conversation_id=conversation.id).exclude(
            auteur_id=acteur.id
        )
        if lu_at is not None:
            qs = qs.filter(sent_at__gt=lu_at)
        return qs.exists()

    def espace_has_unread(
        self, *, espace_id: int, espace_type: str, acteur: User
    ) -> bool:
        """True s'il reste de l'activité non lue sur cet espace pour le membre."""
        part = (
            ParticipationEspace.objects.filter(
                espace_id=espace_id, membre_id=acteur.id
            )
            .only('lu_at')
            .first()
        )
        if part is None:
            return False
        if espace_type == 'COMMUNAUTE':
            qs = MessageGroupe.objects.filter(espace_id=espace_id).exclude(
                auteur_id=acteur.id
            ).filter(supprime_at__isnull=True)
            if part.lu_at is not None:
                qs = qs.filter(sent_at__gt=part.lu_at)
            return qs.exists()
        if espace_type == 'CHAINE':
            qs = Publication.objects.filter(espace_id=espace_id).exclude(
                auteur_id=acteur.id
            )
            if part.lu_at is not None:
                qs = qs.filter(created_at__gt=part.lu_at)
            return qs.exists()
        return False

    def _unread_dm_conversations(self, acteur: User) -> int:
        """Nombre de conversations avec au moins 1 message non lu."""
        total = 0
        conversations = Conversation.objects.filter(
            Q(membre_1=acteur) | Q(membre_2=acteur)
        ).only('id', 'membre_1_id', 'membre_2_id', 'membre_1_lu_at', 'membre_2_lu_at')
        for conv in conversations:
            lu_at = (
                conv.membre_1_lu_at
                if conv.membre_1_id == acteur.id
                else conv.membre_2_lu_at
            )
            qs = Message.objects.filter(conversation_id=conv.id).exclude(
                auteur_id=acteur.id
            )
            if lu_at is not None:
                qs = qs.filter(sent_at__gt=lu_at)
            if qs.exists():
                total += 1
        return total

    def _unread_communautes(self, acteur: User) -> int:
        """Nombre de communautés avec messages de groupe non lus."""
        parts = ParticipationEspace.objects.filter(
            membre=acteur, espace__type='COMMUNAUTE'
        ).select_related('espace')
        total = 0
        for part in parts:
            qs = MessageGroupe.objects.filter(espace_id=part.espace_id).exclude(
                auteur_id=acteur.id
            ).filter(supprime_at__isnull=True)
            if part.lu_at is not None:
                qs = qs.filter(sent_at__gt=part.lu_at)
            if qs.exists():
                total += 1
        return total

    def _unread_chaines(self, acteur: User) -> int:
        """Nombre de chaînes avec publications plus récentes que lu_at."""
        parts = ParticipationEspace.objects.filter(
            membre=acteur, espace__type='CHAINE'
        )
        total = 0
        for part in parts:
            qs = Publication.objects.filter(espace_id=part.espace_id).exclude(
                auteur_id=acteur.id
            )
            if part.lu_at is not None:
                qs = qs.filter(created_at__gt=part.lu_at)
            if qs.exists():
                total += 1
        return total
