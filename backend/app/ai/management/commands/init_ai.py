"""Enregistre la permission ai.chat dans l'IAM existant."""

from django.core.management.base import BaseCommand
from django.db import transaction

from app.core.models import Permission, Role

AI_CODES = ("ai.chat",)


class Command(BaseCommand):
    help = "Crée la permission ai.chat et l'attribue aux rôles Admin / Super Admin / DevStreet Hub Developer."

    @transaction.atomic
    def handle(self, *args, **options):
        permissions = {
            code: Permission.objects.get_or_create(
                code=code, defaults={"description": f"Assistant IA : {code}"}
            )[0]
            for code in AI_CODES
        }
        for role_name in ("Admin", "Super Admin", "DevStreet Hub Developer"):
            role = Role.objects.filter(name=role_name).first()
            if role:
                role.permissions.add(*permissions.values())
        self.stdout.write(
            self.style.SUCCESS(
                "Permission ai.chat prête. Attribuez-la via l’IAM si besoin."
            )
        )
