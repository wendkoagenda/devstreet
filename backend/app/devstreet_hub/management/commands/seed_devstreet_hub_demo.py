"""Comptes de démonstration locaux, via les modèles/IAM existants."""

import json
import secrets
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from app.core.models import Permission, Role


class Command(BaseCommand):
    help = "Prépare Aïcha et Moussa en développement ; secrets dans .local uniquement."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Données de démonstration réservées à DEBUG=True.")
        call_command("init_devstreet_hub")
        directory = Path(settings.BASE_DIR) / ".local"
        directory.mkdir(exist_ok=True)
        path = directory / "demo.credentials.json"
        data = (
            json.loads(path.read_text())
            if path.exists()
            else {"password": secrets.token_urlsafe(24)}
        )
        developer = Role.objects.get(name="DevStreet Hub Developer")
        catalog, _ = Role.objects.get_or_create(name="DevStreet Hub Catalog Maintainer")
        catalog.permissions.add(
            *Permission.objects.filter(code__startswith="technologies.")
        )
        User = get_user_model()
        for username, first_name in (
            ("aicha-chantier", "Aïcha"),
            ("moussa-chantier", "Moussa"),
        ):
            user, created = User.objects.get_or_create(
                email=username + "@example.test",
                defaults={
                    "username": username,
                    "first_name": first_name,
                    "last_name": "Démo",
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
            user.roles.add(developer)
            if username == "aicha-chantier":
                user.roles.add(catalog)
            data[username] = {"id": user.pk, "email": user.email}
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.stdout.write(
            "Comptes prêts ; identifiants dans backend/.local/demo.credentials.json (ignoré par Git)."
        )
