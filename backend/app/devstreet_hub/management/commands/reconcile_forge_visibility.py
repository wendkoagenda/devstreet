"""Réconcilie la visibilité publique des dépôts Gitea (aperçu dry-run par défaut)."""

from django.core.management.base import BaseCommand

from app.devstreet_hub.models import Repository
from app.devstreet_hub.services.errors import ExternalUnavailable
from app.devstreet_hub.services.gitea_client import GiteaClient


class Command(BaseCommand):
    help = (
        "Liste ou applique private=False sur les dépôts Hub prêts. "
        "Aucune suppression de projet ni de dépôt."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Applique les changements (sinon aperçu lecture seule).",
        )

    def handle(self, *args, **options):
        apply = options["apply"]
        qs = Repository.objects.filter(status="ready").select_related("project")
        forge = GiteaClient()
        planned = []
        for repository in qs:
            if not repository.namespace or not repository.name:
                continue
            planned.append(repository)

        self.stdout.write(
            f"{'APPLY' if apply else 'DRY-RUN'}: {len(planned)} dépôt(s) prêts."
        )
        for repository in planned:
            label = f"{repository.namespace}/{repository.name} (project={repository.project_id})"
            owner = repository.project.owner
            if not apply:
                self.stdout.write(
                    f"  would set public repo + user visibility: {label}"
                )
                continue
            try:
                forge.ensure_user_public_visibility(
                    repository.namespace, email=owner.email
                )
                forge.set_public(repository, True)
                self.stdout.write(self.style.SUCCESS(f"  public: {label}"))
            except ExternalUnavailable as error:
                self.stdout.write(self.style.ERROR(f"  échec {label}: {error}"))
        if not apply:
            self.stdout.write("Relancer avec --apply pour écrire sur la forge.")
