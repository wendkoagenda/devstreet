"""
Service des résumés quotidiens d'abonnements.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone

from app.communaute.models import NotificationResume
from app.communaute.repositories.notificationresume_repository import (
    NotificationResumeRepository,
)
from app.communaute.services.publication_service import PublicationService

User = get_user_model()


class NotificationResumeService:
    """Logique métier des résumés quotidiens."""

    def __init__(self):
        self.notificationresume_repository = NotificationResumeRepository()

    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        return self.notificationresume_repository.get_all(
            search=search, ordering=ordering
        )

    def get_by_id(
        self, notification_resume_id: int
    ) -> Optional[NotificationResume]:
        return self.notificationresume_repository.get_by_id(
            notification_resume_id
        )

    def create(
        self, notification_resume_data: Dict[str, Any]
    ) -> NotificationResume:
        self.validate_data(notification_resume_data)
        return self.notificationresume_repository.create(
            **notification_resume_data
        )

    def update(
        self,
        notification_resume_id: int,
        notification_resume_data: Dict[str, Any],
        partial: bool = False,
    ) -> Optional[NotificationResume]:
        notification_resume = self.notificationresume_repository.get_by_id(
            notification_resume_id
        )
        if not notification_resume:
            return None
        if not partial:
            self.validate_data(notification_resume_data)
        return self.notificationresume_repository.update(
            notification_resume, **notification_resume_data
        )

    def delete(self, notification_resume_id: int) -> bool:
        notification_resume = self.notificationresume_repository.get_by_id(
            notification_resume_id
        )
        if not notification_resume:
            return False
        return self.notificationresume_repository.delete(notification_resume)

    def validate_data(self, notification_resume_data: Dict[str, Any]):
        return

    def covered_day(self, now: Optional[datetime] = None) -> date:
        """Journée couverte : la veille (timezone locale Django)."""
        current = timezone.localtime(now or timezone.now())
        return (current - timedelta(days=1)).date()

    def count_nouveautes(
        self, *, membre: User, jour: date
    ) -> int:
        """
        Compte les pubs d'abonnements du jour, sans doublon,
        via la même visibilité que le fil Abonnements.
        """
        qs = PublicationService().get_feed_abonnements(membre=membre)
        start = timezone.make_aware(datetime.combine(jour, time.min))
        end = timezone.make_aware(
            datetime.combine(jour + timedelta(days=1), time.min)
        )
        return qs.filter(created_at__gte=start, created_at__lt=end).count()

    def ensure_for_day(
        self, *, membre: User, jour: Optional[date] = None
    ) -> Optional[NotificationResume]:
        """
        Crée ou met à jour le résumé du jour couvert.
        Ne crée rien si 0 nouveauté (évite le bruit).
        """
        day = jour or self.covered_day()
        count = self.count_nouveautes(membre=membre, jour=day)
        existing = NotificationResume.objects.filter(
            destinataire=membre, periode_debut=day
        ).first()

        if existing is not None:
            if existing.nombre_nouveautes != count and existing.read_at is None:
                existing.nombre_nouveautes = count
                existing.periode_fin = day
                existing.updated_by = membre.id
                existing.save(
                    update_fields=[
                        'nombre_nouveautes',
                        'periode_fin',
                        'updated_by',
                        'updated_at',
                    ]
                )
            return existing if existing.nombre_nouveautes > 0 else None

        if count <= 0:
            return None

        try:
            with transaction.atomic():
                return NotificationResume.objects.create(
                    destinataire=membre,
                    periode_debut=day,
                    periode_fin=day,
                    nombre_nouveautes=count,
                    created_by=membre.id,
                    updated_by=membre.id,
                )
        except IntegrityError:
            return (
                NotificationResume.objects.filter(
                    destinataire=membre, periode_debut=day
                ).first()
            )

    def get_actuel_non_lu(
        self, *, membre: User
    ) -> Optional[NotificationResume]:
        """Dernier résumé non lu (génère celui d'hier si besoin)."""
        self.ensure_for_day(membre=membre)
        return (
            NotificationResume.objects.filter(
                destinataire=membre,
                read_at__isnull=True,
                nombre_nouveautes__gt=0,
            )
            .order_by('-periode_debut', '-id')
            .first()
        )

    def mark_read(
        self, *, resume_id: int, membre: User
    ) -> NotificationResume:
        resume = NotificationResume.objects.filter(
            id=resume_id, destinataire=membre
        ).first()
        if resume is None:
            raise ValidationError('Résumé introuvable.')
        if resume.read_at is None:
            resume.read_at = timezone.now()
            resume.updated_by = membre.id
            resume.save(
                update_fields=['read_at', 'updated_by', 'updated_at']
            )
        return resume

    def generate_for_all_active_users(
        self, *, jour: Optional[date] = None
    ) -> int:
        """Produit les résumés pour tous les users actifs. Retourne le nombre créés/maj."""
        day = jour or self.covered_day()
        created = 0
        for user in User.objects.filter(is_active=True).iterator():
            before = NotificationResume.objects.filter(
                destinataire=user, periode_debut=day
            ).exists()
            resume = self.ensure_for_day(membre=user, jour=day)
            if resume is not None and not before:
                created += 1
        return created
