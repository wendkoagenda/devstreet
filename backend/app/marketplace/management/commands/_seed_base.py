"""
Base commune des seeds de la marketplace.

Chaque commande seed_<modele> crée les permissions du modèle, les assigne aux rôles Admin / Super Admin,
puis insère quelques données de démonstration cohérentes (objets liés inclus) via app.marketplace.factories.
Le seed est ignoré si la table contient déjà des lignes et reste atomique : un échec ne laisse aucune donnée partielle.
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from app.core.models import Permission, Role, User

DEMO_COUNT = 3


class MarketplaceSeedCommand(BaseCommand):
    model = None  # classe du modèle
    resource_plural = None  # préfixe des permissions (ex. « profil-histories »)

    def build(self, admin, index):
        """Crée et retourne un enregistrement de démonstration (index de 1 à DEMO_COUNT)."""
        raise NotImplementedError

    def handle(self, *args, **options):
        label = self.model.__name__
        self.stdout.write(self.style.SUCCESS(f"Création des seeds pour {label}..."))

        self.create_permissions()
        admin = self.get_admin()
        self.assign_permissions_to_admin_role()

        existing = self.model.objects.count()
        if existing > 0:
            self.stdout.write(
                self.style.WARNING(f"La table {label} contient déjà {existing} enregistrement(s). Seeds de données ignorés.")
            )
            return

        with transaction.atomic():
            for index in range(1, DEMO_COUNT + 1):
                created = self.build(admin, index)
                self.stdout.write(f"{label} créé: {created}")

        total = self.model.objects.count()
        self.stdout.write(self.style.SUCCESS(f"{DEMO_COUNT} {label} créé(s) ; total dans la base: {total}"))

    def get_admin(self):
        """Administrateur (identifiants : variables ADMIN_EMAIL / ADMIN_PASSWORD), créé au besoin."""
        try:
            return User.objects.get(email=settings.ADMIN_EMAIL)
        except User.DoesNotExist:
            admin = User.objects.create_user(
                username="admin",
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.WARNING("Utilisateur admin créé"))
            return admin

    def create_permissions(self):
        for action in ("view", "create", "update", "delete"):
            code = f"{self.resource_plural}.{action}"
            _, created = Permission.objects.get_or_create(
                code=code, defaults={"description": f"Can {action} {self.resource_plural}"}
            )
            if created:
                self.stdout.write(f"Permission créée: {code}")

    def assign_permissions_to_admin_role(self):
        permissions = Permission.objects.filter(code__startswith=f"{self.resource_plural}.")
        for role_name in ("Admin", "Super Admin"):
            try:
                role = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Rôle {role_name} non trouvé"))
                continue
            role.permissions.add(*permissions)
            self.stdout.write(f"Permissions {self.resource_plural} assignées au rôle {role_name}")
