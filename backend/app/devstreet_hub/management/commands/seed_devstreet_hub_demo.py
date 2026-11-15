"""Comptes et projets de démonstration locaux, via les modèles/IAM existants."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from app.core.models import Permission, Role
from app.devstreet_hub.models import Project, Repository, Star, Technology

SHOWCASE_PASSWORD = "test@123"

DEMO_TECHNOLOGIES = (
    ("Python", "python"),
    ("Django", "django"),
    ("PostgreSQL", "postgresql"),
    ("React", "react"),
    ("Go", "go"),
)

DEMO_PROJECTS = (
    {
        "slug": "stock",
        "title": "Stock",
        "problem": (
            "Outil de gestion de stock et de traçabilité pour petits commerces "
            "et grossistes de quartier, adapté aux connexions intermittentes."
        ),
        "description": "Projet de démonstration pour l'explorateur DevStreet Hub.",
        "declared_license": "MIT",
        "status": "published",
        "tech_slugs": ("python", "django", "postgresql"),
        "stars": 3,
    },
    {
        "slug": "afripay-sdk",
        "title": "AfriPay SDK",
        "problem": (
            "Librairie unifiée pour agréger les passerelles Mobile Money "
            "(Wave, Orange Money, MTN MoMo) pour applications Python et Node.js."
        ),
        "description": "SDK de démonstration pour filtrer par technologie.",
        "declared_license": "Apache-2.0",
        "status": "published",
        "tech_slugs": ("python", "go"),
        "stars": 2,
    },
    {
        "slug": "agritrack",
        "title": "AgriTrack",
        "problem": (
            "Tableau de bord de suivi météorologique et de cours des céréales "
            "locales en temps réel pour coopératives agricoles."
        ),
        "description": "Brouillon visible uniquement par la propriétaire.",
        "declared_license": "MIT",
        "status": "draft",
        "tech_slugs": ("django", "react", "postgresql"),
        "stars": 0,
    },
)


class Command(BaseCommand):
    help = (
        "Prépare Aïcha, Moussa, un petit catalogue de technologies et 3 projets "
        "de démonstration ; secrets dans .local uniquement."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--allow-non-debug",
            action="store_true",
            help="Autorise l'exécution quand DEBUG=False (prod/staging vide).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options.get("allow_non_debug"):
            raise CommandError(
                "DEBUG=False : passe --allow-non-debug pour peupler une instance vide."
            )
        call_command("init_devstreet_hub")
        developer = Role.objects.get(name="DevStreet Hub Developer")
        catalog, _ = Role.objects.get_or_create(name="DevStreet Hub Catalog Maintainer")
        catalog.permissions.add(
            *Permission.objects.filter(code__startswith="technologies.")
        )
        User = get_user_model()
        users = {}
        for username, first_name in (
            ("aicha-chantier", "Aïcha"),
            ("moussa-chantier", "Moussa"),
        ):
            user, _created = User.objects.get_or_create(
                email=username + "@example.test",
                defaults={
                    "username": username,
                    "first_name": first_name,
                    "last_name": "Démo",
                },
            )
            user.set_password(SHOWCASE_PASSWORD)
            user.save()
            user.roles.add(developer)
            if username == "aicha-chantier":
                user.roles.add(catalog)
            users[username] = user

        tech_by_slug = {}
        for label, slug in DEMO_TECHNOLOGIES:
            tech, created = Technology.objects.get_or_create(
                slug=slug,
                defaults={
                    "label": label,
                    "created_by": users["aicha-chantier"].pk,
                    "updated_by": users["aicha-chantier"].pk,
                },
            )
            tech_by_slug[slug] = tech
            if created:
                self.stdout.write(f"  Technology créée : {label}")

        owner = users["aicha-chantier"]
        for payload in DEMO_PROJECTS:
            project, created = Project.objects.get_or_create(
                slug=payload["slug"],
                defaults={
                    "owner": owner,
                    "title": payload["title"],
                    "problem": payload["problem"],
                    "description": payload["description"],
                    "declared_license": payload["declared_license"],
                    "status": payload["status"],
                    "created_by": owner.pk,
                    "updated_by": owner.pk,
                },
            )
            if not created:
                project.title = payload["title"]
                project.problem = payload["problem"]
                project.description = payload["description"]
                project.declared_license = payload["declared_license"]
                project.status = payload["status"]
                project.updated_by = owner.pk
                project.save()
            project.technologies.set(
                [tech_by_slug[slug] for slug in payload["tech_slugs"]]
            )
            repository, _ = Repository.objects.get_or_create(
                project=project,
                defaults={"name": f"project-{project.pk}"},
            )
            if payload["status"] == "published":
                repository.status = "ready"
                repository.namespace = owner.username
                repository.name = payload["slug"]
                repository.default_branch = "main"
                repository.save(
                    update_fields=["status", "namespace", "name", "default_branch"]
                )
            Star.objects.filter(project=project).delete()
            for index in range(payload["stars"]):
                Star.objects.get_or_create(
                    project=project,
                    user=users["moussa-chantier"] if index == 0 else owner,
                )
            self.stdout.write(
                f"  Projet {'créé' if created else 'mis à jour'} : "
                f"{project.title} ({project.status})"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Comptes et projets prêts — mot de passe : {SHOWCASE_PASSWORD}"
            )
        )
