"""Enregistre les permissions métier dans l'IAM fourni par la boilerplate."""

from django.core.management.base import BaseCommand
from django.db import transaction
from app.core.models import Permission, Role

DEVELOPER_CODES = (
    "projects.create",
    "projects.update",
    "projects.publish",
    "projects.archive",
    "projects.star",
    "projects.members",
    "projects.analyze",
    "projects.discuss",
    "contribution-tasks.create",
    "contribution-tasks.update",
    "contributions.create",
    "contributions.review",
)
ADMIN_CODES = DEVELOPER_CODES + (
    "technologies.view",
    "technologies.create",
    "technologies.update",
    "technologies.delete",
)


class Command(BaseCommand):
    help = "Crée le rôle DevStreet Hub Developer et les permissions, sans créer ni modifier de comptes."

    @transaction.atomic
    def handle(self, *args, **options):
        # Renommage des rôles du module en conservant leurs IDs et attributions.
        for old_name, new_name in (
            ("Chantier Developer", "DevStreet Hub Developer"),
            ("Chantier Catalog Maintainer", "DevStreet Hub Catalog Maintainer"),
        ):
            if not Role.objects.filter(name=new_name).exists():
                Role.objects.filter(name=old_name).update(name=new_name)
        permissions = {
            code: Permission.objects.get_or_create(
                code=code, defaults={"description": f"DevStreet Hub : {code}"}
            )[0]
            for code in ADMIN_CODES
        }
        developer, _ = Role.objects.get_or_create(name="DevStreet Hub Developer")
        developer.permissions.add(*(permissions[c] for c in DEVELOPER_CODES))
        for role in Role.objects.filter(name__in=["Admin", "Super Admin"]):
            role.permissions.add(*permissions.values())
        self.stdout.write(
            self.style.SUCCESS(
                "Permissions DevStreet Hub prêtes. Attribuez le rôle via l’IAM existant."
            )
        )
