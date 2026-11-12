"""Permissions de la marketplace : migration de seed et attribution aux rôles Admin / Super Admin."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from app.core.models import Permission, Role
from app.marketplace.permission_codes import MARKETPLACE_PERMISSION_CODES


class MarketplacePermissionsTests(TestCase):
    def test_migration_creates_all_permissions(self):
        self.assertEqual(len(MARKETPLACE_PERMISSION_CODES), 52)
        existing = set(Permission.objects.filter(code__in=MARKETPLACE_PERMISSION_CODES).values_list("code", flat=True))
        self.assertEqual(existing, set(MARKETPLACE_PERMISSION_CODES))

    def test_init_data_assigns_permissions_to_admin_roles(self):
        call_command("init_data", skip_admin=True, stdout=StringIO())
        for name in ("Admin", "Super Admin"):
            codes = set(Role.objects.get(name=name).permissions.values_list("code", flat=True))
            self.assertTrue(set(MARKETPLACE_PERMISSION_CODES) <= codes, name)
        # les autres rôles ne reçoivent rien
        viewer = set(Role.objects.get(name="Viewer").permissions.values_list("code", flat=True))
        self.assertFalse(viewer & set(MARKETPLACE_PERMISSION_CODES))

    def test_migration_assigns_permissions_to_existing_roles(self):
        """Rôles déjà présents lors de la migration : elle leur attribue les permissions (rejouée sur la base de test)."""
        import importlib

        migration = importlib.import_module("app.marketplace.migrations.0002_seed_marketplace_permissions")
        from django.apps import apps
        from django.db import connection

        role = Role.objects.create(name="Admin", description="Test")
        migration.seed_permissions(apps, type("Editor", (), {"connection": connection})())
        self.assertEqual(role.permissions.filter(code__in=MARKETPLACE_PERMISSION_CODES).count(), 52)


class SyncMarketplacePermissionsMigrationTests(TestCase):
    """Migration 0004 : rattrape les permissions manquantes, sans doublon ni création de rôle."""

    def run_sync(self):
        import importlib

        from django.apps import apps
        from django.db import connection

        migration = importlib.import_module("app.marketplace.migrations.0004_sync_marketplace_permissions")
        migration.sync_permissions(apps, type("Editor", (), {"connection": connection})())

    def test_recreates_deleted_permissions_and_reassigns_them(self):
        role = Role.objects.create(name="Admin", description="Test")
        Permission.objects.filter(code__in=["offers.view", "reviews.delete"]).delete()
        self.run_sync()
        codes = set(Permission.objects.filter(code__in=MARKETPLACE_PERMISSION_CODES).values_list("code", flat=True))
        self.assertEqual(codes, set(MARKETPLACE_PERMISSION_CODES))
        self.assertEqual(role.permissions.filter(code__in=MARKETPLACE_PERMISSION_CODES).count(), 52)

    def test_is_idempotent(self):
        role = Role.objects.create(name="Super Admin", description="Test")
        self.run_sync()
        before = Permission.objects.count()
        self.run_sync()
        self.assertEqual(Permission.objects.count(), before)
        self.assertEqual(role.permissions.filter(code__in=MARKETPLACE_PERMISSION_CODES).count(), 52)

    def test_does_not_create_roles_nor_touch_other_roles(self):
        other = Role.objects.create(name="Viewer-test", description="Test")
        roles_before = Role.objects.count()
        self.run_sync()
        self.assertEqual(Role.objects.count(), roles_before)
        self.assertFalse(other.permissions.filter(code__in=MARKETPLACE_PERMISSION_CODES).exists())

    def test_keeps_the_codes_of_the_migration_in_step_with_the_application(self):
        """La liste figée de la migration doit rester égale à celle de l'application (à mettre à jour si on ajoute un modèle)."""
        import importlib

        migration = importlib.import_module("app.marketplace.migrations.0004_sync_marketplace_permissions")
        self.assertEqual(migration._codes(), MARKETPLACE_PERMISSION_CODES)
