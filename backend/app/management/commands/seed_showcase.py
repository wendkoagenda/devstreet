"""Peuple une instance vide : forum + marketplace + Hub (Afrique de l'Ouest).

Usage (backend/, venv active) :
  python manage.py seed_showcase
  python manage.py seed_showcase --allow-non-debug   # prod / staging vide
  python manage.py seed_showcase --allow-non-debug --reset-marketplace

Couverture :
  Forum — users, communautés, chaînes, pubs, commentaires/réponses, likes,
          suivis, favoris, DM, messages groupe
  Marketplace — entreprises, profils, skills, offres, candidatures, avis,
                swipes, connexions, disponibilités…
  Hub — technos, projets, repos, tâches, contributions, stars

Mot de passe commun de tous les comptes : test@123
"""
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Showcase qualitatif complet : forum (engagement) + marketplace + Hub (repos)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--allow-non-debug",
            action="store_true",
            help="Autorise l'exécution quand DEBUG=False (prod/staging vide).",
        )
        parser.add_argument(
            "--force-forum",
            action="store_true",
            help="Réécrit publications/messages/engagement forum showcase.",
        )
        parser.add_argument(
            "--reset-marketplace",
            action="store_true",
            help="Supprime d'abord les données marketplace de démo avant de reseeder.",
        )
        parser.add_argument(
            "--skip-hub",
            action="store_true",
            help="Ne pas peupler le Hub.",
        )
        parser.add_argument(
            "--skip-marketplace",
            action="store_true",
            help="Ne pas peupler la marketplace.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["allow_non_debug"]:
            raise CommandError(
                "DEBUG=False : passe --allow-non-debug pour peupler une instance vide."
            )

        flag = {}
        if options["allow_non_debug"]:
            flag["allow_non_debug"] = True

        self.stdout.write(self.style.MIGRATE_HEADING("1/3 — Forum showcase"))
        forum_opts = dict(flag)
        if options["force_forum"]:
            forum_opts["force"] = True
        call_command("seed_forum_showcase", **forum_opts)

        if options["skip_marketplace"]:
            self.stdout.write(self.style.WARNING("2/3 — Marketplace ignorée (--skip-marketplace)"))
        else:
            self.stdout.write(self.style.MIGRATE_HEADING("2/3 — Marketplace demo"))
            market_opts = dict(flag)
            if options["reset_marketplace"]:
                market_opts["reset"] = True
            call_command("seed_marketplace_demo", **market_opts)

        if options["skip_hub"]:
            self.stdout.write(self.style.WARNING("3/3 — Hub ignoré (--skip-hub)"))
        else:
            self.stdout.write(self.style.MIGRATE_HEADING("3/3 — Hub showcase"))
            call_command("seed_hub_showcase", **flag)

        self.stdout.write(
            self.style.SUCCESS("Showcase prêt. Mot de passe de tous les comptes : test@123")
        )
