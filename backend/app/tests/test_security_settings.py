"""
Tests de la configuration de sécurité : secrets obligatoires, limitation de débit,
documentation de l'API et réglages HTTP hors DEBUG.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APITestCase

from app.core.throttles import LoginThrottle, TokenRefreshThrottle
from config.env_secrets import (
    MIN_SECRET_LENGTH,
    read_admin_credentials,
    read_secret,
    read_signing_secrets,
)

BACKEND_DIR = Path(__file__).resolve().parents[2]
STRONG_A = 'a' * 60
STRONG_B = 'b' * 60


class SecretValidationTests(SimpleTestCase):
    def test_absent_secret_is_refused(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ImproperlyConfigured):
                read_secret('SECRET_KEY')

    def test_blank_secret_is_refused(self):
        with patch.dict(os.environ, {'SECRET_KEY': '   '}, clear=True):
            with self.assertRaises(ImproperlyConfigured):
                read_secret('SECRET_KEY')

    def test_short_secret_is_refused(self):
        with patch.dict(os.environ, {'SECRET_KEY': 'x' * (MIN_SECRET_LENGTH - 1)}, clear=True):
            with self.assertRaises(ImproperlyConfigured):
                read_secret('SECRET_KEY')

    def test_example_value_is_refused(self):
        for value in ('django-insecure-' + 'x' * 60, 'votre-cle-' + 'x' * 60, 'change-me' + 'x' * 60):
            with patch.dict(os.environ, {'SECRET_KEY': value}, clear=True):
                with self.assertRaises(ImproperlyConfigured, msg=value):
                    read_secret('SECRET_KEY')

    def test_strong_secret_is_accepted(self):
        with patch.dict(os.environ, {'SECRET_KEY': STRONG_A}, clear=True):
            self.assertEqual(read_secret('SECRET_KEY'), STRONG_A)

    def test_jwt_key_is_mandatory(self):
        with patch.dict(os.environ, {'SECRET_KEY': STRONG_A}, clear=True):
            with self.assertRaisesMessage(ImproperlyConfigured, 'JWT_SIGNING_KEY'):
                read_signing_secrets()

    def test_jwt_key_must_differ_from_secret_key(self):
        with patch.dict(os.environ, {'SECRET_KEY': STRONG_A, 'JWT_SIGNING_KEY': STRONG_A}, clear=True):
            with self.assertRaisesMessage(ImproperlyConfigured, 'différente'):
                read_signing_secrets()

    def test_distinct_keys_are_accepted(self):
        with patch.dict(os.environ, {'SECRET_KEY': STRONG_A, 'JWT_SIGNING_KEY': STRONG_B}, clear=True):
            self.assertEqual(read_signing_secrets(), (STRONG_A, STRONG_B))


class AdminCredentialsTests(SimpleTestCase):
    GOOD = {'ADMIN_EMAIL': 'chef@exemple.fr', 'ADMIN_PASSWORD': 'Mot-de-passe-1'}

    def read(self, **override):
        env = {**self.GOOD, **override}
        env = {k: v for k, v in env.items() if v is not None}
        with patch.dict(os.environ, env, clear=True):
            return read_admin_credentials()

    def test_valid_credentials(self):
        self.assertEqual(self.read(), ('chef@exemple.fr', 'Mot-de-passe-1'))

    def test_email_is_mandatory(self):
        for value in (None, '', '   '):
            with self.assertRaisesMessage(ImproperlyConfigured, 'ADMIN_EMAIL'):
                self.read(ADMIN_EMAIL=value)

    def test_email_must_look_like_an_address(self):
        for value in ('admin', '@exemple.fr', 'admin@'):
            with self.assertRaisesMessage(ImproperlyConfigured, 'ADMIN_EMAIL'):
                self.read(ADMIN_EMAIL=value)

    def test_password_is_mandatory(self):
        for value in (None, '', '   '):
            with self.assertRaisesMessage(ImproperlyConfigured, 'ADMIN_PASSWORD'):
                self.read(ADMIN_PASSWORD=value)

    def test_short_password_is_refused(self):
        with self.assertRaisesMessage(ImproperlyConfigured, 'trop court'):
            self.read(ADMIN_PASSWORD='court')


@override_settings(ADMIN_EMAIL='chef@exemple.fr', ADMIN_PASSWORD='Mot-de-passe-1')
class AdminSeedTests(TestCase):
    """init_data crée l'administrateur avec les identifiants des variables, jamais avec une valeur du code."""

    def test_init_data_uses_the_environment_credentials(self):
        from io import StringIO
        call_command('init_data', verbosity=0, stdout=StringIO())  # la sortie ne dépend pas du terminal
        user = get_user_model().objects.get(email='chef@exemple.fr')
        self.assertTrue(user.check_password('Mot-de-passe-1'))
        self.assertTrue(user.is_superuser)
        self.assertFalse(get_user_model().objects.filter(email='admin@example.com').exists())

    def test_no_password_is_printed(self):
        from io import StringIO
        out = StringIO()
        call_command('init_data', verbosity=0, stdout=out)
        self.assertNotIn('Mot-de-passe-1', out.getvalue())


class JwtSigningKeyTests(SimpleTestCase):
    def test_jwt_is_signed_with_its_own_key(self):
        from django.conf import settings

        self.assertEqual(settings.SIMPLE_JWT['SIGNING_KEY'], settings.JWT_SIGNING_KEY)
        self.assertNotEqual(settings.JWT_SIGNING_KEY, settings.SECRET_KEY)


class AuthThrottleTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    def test_login_is_rate_limited(self):
        with patch.dict(LoginThrottle.THROTTLE_RATES, {'login': '3/minute'}):
            codes = [
                self.client.post(
                    '/api/auth/login', {'email': 'nobody@example.com', 'password': 'bad'}, format='json'
                ).status_code
                for _ in range(4)
            ]
        self.assertNotIn(429, codes[:3])
        self.assertEqual(codes[3], 429)

    def test_refresh_is_rate_limited(self):
        with patch.dict(TokenRefreshThrottle.THROTTLE_RATES, {'token_refresh': '2/minute'}):
            codes = [
                self.client.post('/api/auth/token/refresh', {'refresh': 'invalide'}, format='json').status_code
                for _ in range(3)
            ]
        self.assertNotIn(429, codes[:2])
        self.assertEqual(codes[2], 429)


class ProductionSettingsTests(SimpleTestCase):
    """Charge les réglages dans un processus séparé avec DEBUG=False."""

    def _settings(self, extra=None):
        env = {**os.environ, 'DEBUG': 'False', 'SECRET_KEY': STRONG_A, 'JWT_SIGNING_KEY': STRONG_B,
               'DJANGO_SETTINGS_MODULE': 'config.settings'}
        env['ENABLE_API_DOCS'] = 'false'
        env['ENABLE_ADMIN'] = 'false'
        env.update(extra or {})
        code = (
            'import json, django\n'
            'django.setup()\n'
            'from django.conf import settings\n'
            'from django.urls import resolve, Resolver404\n'
            'def routed(path):\n'
            '    try:\n        resolve(path); return True\n    except Resolver404:\n        return False\n'
            'print(json.dumps({"docs": settings.ENABLE_API_DOCS, "swagger": routed("/swagger/"),'
            ' "redoc": routed("/redoc/"), "admin": routed("/admin/"), "session_secure": settings.SESSION_COOKIE_SECURE,'
            ' "csrf_secure": settings.CSRF_COOKIE_SECURE, "hsts": settings.SECURE_HSTS_SECONDS}))\n'
        )
        out = subprocess.run([sys.executable, '-c', code], cwd=BACKEND_DIR, env=env,
                             capture_output=True, text=True, check=True)
        return json.loads(out.stdout.strip().splitlines()[-1])

    def test_defaults_outside_debug(self):
        result = self._settings()
        self.assertFalse(result['docs'])
        self.assertFalse(result['swagger'])
        self.assertFalse(result['redoc'])
        self.assertFalse(result['admin'])
        self.assertTrue(result['session_secure'])
        self.assertTrue(result['csrf_secure'])
        self.assertGreater(result['hsts'], 0)

    def test_admin_can_be_enabled_explicitly(self):
        self.assertTrue(self._settings({'ENABLE_ADMIN': 'true'})['admin'])

    def test_docs_can_be_enabled_explicitly(self):
        result = self._settings({'ENABLE_API_DOCS': 'true'})
        self.assertTrue(result['swagger'])
        self.assertTrue(result['redoc'])
