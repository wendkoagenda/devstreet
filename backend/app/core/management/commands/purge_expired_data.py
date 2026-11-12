"""
Purge des données périmées, à planifier une fois par jour (cron ou timer systemd) :

- jetons de rafraîchissement expirés de la liste noire SimpleJWT (sinon elle grossit sans fin) ;
- challenges de réinitialisation de mot de passe de plus de 7 jours ;
- entrées du journal d'audit plus anciennes que AUDIT_RETENTION_DAYS (config/settings.py).
"""
from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.core.repositories.password_reset_challenge_repository import PasswordResetChallengeRepository
from app.core.services import audit_service

RESET_CHALLENGE_RETENTION_DAYS = 7


class Command(BaseCommand):
    help = "Purge les jetons expirés, les challenges de réinitialisation et les anciennes entrées du journal d'audit"

    def handle(self, *args, **options):
        call_command('flushexpiredtokens', stdout=self.stdout)
        cutoff = timezone.now() - timedelta(days=RESET_CHALLENGE_RETENTION_DAYS)
        challenges = PasswordResetChallengeRepository().delete_expired(cutoff)
        self.stdout.write(f"{challenges} challenge(s) de réinitialisation supprimé(s).")
        entries = audit_service.purge_older_than_retention()
        self.stdout.write(self.style.SUCCESS(f"{entries} entrée(s) du journal d'audit supprimée(s)."))
