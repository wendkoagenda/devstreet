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
