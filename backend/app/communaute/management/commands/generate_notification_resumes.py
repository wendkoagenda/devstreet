"""
Produit les résumés quotidiens d'abonnements (veille calendaire).

À planifier (cron / task) après minuit locale, idéalement vers 08:00.
L'API `actuel` régénère aussi à la demande pour le membre connecté.
"""
from django.core.management.base import BaseCommand

from app.communaute.services.notificationresume_service import (
    NotificationResumeService,
)


class Command(BaseCommand):
    help = 'Génère les résumés quotidiens NotificationResume pour la veille'

    def handle(self, *args, **options):
        service = NotificationResumeService()
        jour = service.covered_day()
        created = service.generate_for_all_active_users(jour=jour)
        self.stdout.write(
            self.style.SUCCESS(
                f'Résumés du {jour.isoformat()} : {created} nouveau(x).'
            )
        )
