"""À lancer depuis un worker/cron ; aucune exécution de code des dépôts."""

from django.core.management.base import BaseCommand
from app.devstreet_hub.services.analysis_worker import process_next


class Command(BaseCommand):
    help = "Traite au maximum N analyses IA en attente (défaut : 10)."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        for _ in range(max(0, min(options["limit"], 100))):
            job = process_next()
            if job is None:
                break
            self.stdout.write(f"Analyse {job.pk}: {job.status}")
