"""La suppression des demonstrations preserve les routes utiles et leurs droits."""
from importlib import import_module
from types import SimpleNamespace

from django.apps import apps
from django.db import connection
from django.test import TestCase
from django.urls import Resolver404, resolve

from app.core.models import Permission


class DemoCleanupTests(TestCase):
    def test_demo_routes_and_models_are_absent(self):
        for resource in ('elitests', 'elitesties', 'dragons', 'fusions', 'gados'):
            for suffix in ('', '/1'):
                with self.subTest(resource=resource, suffix=suffix):
                    with self.assertRaises(Resolver404):
                        resolve(f'/api/v1/{resource}{suffix}')
        self.assertEqual(list(apps.get_app_config('metier').get_models()), [])
        self.assertEqual(list(apps.get_app_config('garoapp').get_models()), [])

    def test_core_and_hub_routes_still_resolve(self):
        for resource in ('users', 'roles', 'projects', 'technologies', 'contribution-tasks'):
            with self.subTest(resource=resource):
                self.assertIsNotNone(resolve(f'/api/v1/{resource}').func)

    def test_permission_cleanup_is_scoped_to_demo_crud_codes(self):
        for code in ('dragons.view', 'gados.create', 'users.view', 'projects.view', 'dragons.custom'):
            Permission.objects.get_or_create(code=code)
        migration = import_module('app.metier.migrations.0010_remove_demo_models')
        migration.remove_demo_permissions(apps, SimpleNamespace(connection=connection))
        codes = set(Permission.objects.values_list('code', flat=True))
        self.assertFalse(codes & {'dragons.view', 'gados.create'})
        self.assertTrue({'users.view', 'projects.view', 'dragons.custom'} <= codes)
