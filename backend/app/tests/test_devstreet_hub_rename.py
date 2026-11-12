"""Compatibilité du renommage : mêmes données et attributions IAM."""

from io import StringIO
from django.apps import apps
from django.core.management import call_command
from django.test import SimpleTestCase
from app.core.models import Role
from app.tests.devstreet_hub_base import DevStreetHubAPITestCase


class AppIdentityTests(SimpleTestCase):
    def test_python_module_is_renamed_without_changing_database_identity(self):
        config = apps.get_app_config("projects")
        self.assertEqual(config.name, "app.devstreet_hub")
        self.assertEqual(config.verbose_name, "DevStreet Hub")
        self.assertTrue(
            all(
                model._meta.db_table.startswith("projects_")
                for model in config.get_models()
            )
        )


class RoleRenameTests(DevStreetHubAPITestCase):
    def test_existing_role_members_and_permissions_survive_rebranding(self):
        old_role = Role.objects.create(name="Chantier Developer")
        old_role.permissions.set(self.role.permissions.all())
        self.moussa.roles.add(old_role)
        original_codes = set(old_role.get_permissions())
        call_command("init_devstreet_hub", stdout=StringIO())
        old_role.refresh_from_db()
        self.assertEqual(old_role.name, "DevStreet Hub Developer")
        self.assertTrue(self.moussa.roles.filter(pk=old_role.pk).exists())
        self.assertTrue(original_codes <= set(old_role.get_permissions()))
