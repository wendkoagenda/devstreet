"""
Commande Django pour supprimer les anciens challenges de réinitialisation de mot de passe.

Les challenges expirés sont inutilisables ; les purger limite la taille de la table.
À planifier (cron / tâche planifiée) par exemple une fois par jour.
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from app.core.repositories.password_reset_challenge_repository import PasswordResetChallengeRepository


class Command(BaseCommand):
    """
    Supprime les challenges créés il y a plus de N jours (7 par défaut).
    """
    help = "Supprime les challenges de réinitialisation de mot de passe plus anciens que N jours"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help="Âge minimal (en jours) des challenges à supprimer (défaut : 7)",
        )

    def handle(self, *args, **options):
        days = options['days']
        if days < 1:
            self.stderr.write(self.style.ERROR("--days doit être supérieur ou égal à 1."))
            return

        cutoff = timezone.now() - timedelta(days=days)
        deleted = PasswordResetChallengeRepository().delete_expired(cutoff)
        self.stdout.write(self.style.SUCCESS(f"{deleted} challenge(s) supprimé(s) (créés avant {cutoff:%Y-%m-%d %H:%M})."))
