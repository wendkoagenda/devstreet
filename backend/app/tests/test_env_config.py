"""
Tests de la configuration par variables d'environnement : aucune valeur de repli, démarrage refusé si une variable manque.
"""
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.env import optional, required, required_bool, required_list

BACKEND_DIR = Path(__file__).resolve().parents[2]


class EnvHelpersTests(SimpleTestCase):
    def env(self, **values):
        return patch.dict(os.environ, values, clear=True)

    def test_required_returns_the_stripped_value(self):
        with self.env(X='  valeur  '):
            self.assertEqual(required('X'), 'valeur')

    def test_required_refuses_missing_empty_and_blank(self):
        for values in ({}, {'X': ''}, {'X': '   '}):
            with self.env(**values), self.assertRaisesMessage(ImproperlyConfigured, 'X est obligatoire'):
                required('X')

    def test_required_bool_accepts_only_clear_values(self):
        for text, expected in (('true', True), ('True', True), ('1', True), ('yes', True),
                               ('false', False), ('False', False), ('0', False), ('no', False)):
            with self.env(B=text):
                self.assertIs(required_bool('B'), expected, text)

    def test_required_bool_refuses_ambiguous_values(self):
        for text in ('peut-etre', 'vrai', 'on', '2'):
            with self.env(B=text), self.assertRaisesMessage(ImproperlyConfigured, 'true ou false'):
                required_bool('B')

    def test_required_bool_refuses_missing(self):
        with self.env(), self.assertRaisesMessage(ImproperlyConfigured, 'B est obligatoire'):
            required_bool('B')

    def test_required_list_splits_and_trims(self):
        with self.env(L=' a , b,,c '):
            self.assertEqual(required_list('L'), ['a', 'b', 'c'])

    def test_required_list_refuses_empty_lists(self):
        for text in ('', ',', ' , '):
            with self.env(L=text), self.assertRaises(ImproperlyConfigured):
                required_list('L')

    def test_optional_returns_none_when_absent_or_blank(self):
        for values in ({}, {'O': ''}, {'O': '  '}):
            with self.env(**values):
                self.assertIsNone(optional('O'))
        with self.env(O='x'):
            self.assertEqual(optional('O'), 'x')


class SettingsStartupTests(SimpleTestCase):
    """Démarre Django dans un processus séparé avec une variable cassée : le démarrage doit échouer en la nommant."""

    def start(self, **override):
        env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings', **override}
        return subprocess.run([sys.executable, '-c', 'import django; django.setup()'], cwd=BACKEND_DIR, env=env,
                              capture_output=True, text=True)

    def test_each_mandatory_variable_stops_the_startup(self):
        for name in ('DEBUG', 'ALLOWED_HOSTS', 'CORS_ALLOWED_ORIGINS', 'CSRF_TRUSTED_ORIGINS', 'FRONTEND_URL',
                     'EMAIL_BACKEND', 'DEFAULT_FROM_EMAIL', 'USE_X_FORWARDED_PROTO', 'ENABLE_API_DOCS', 'ENABLE_ADMIN', 'USE_S3',
                     'DB_NAME'):
            with self.subTest(variable=name):
                result = self.start(**{name: ''})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f'{name} est obligatoire', result.stderr)

    def test_smtp_backend_requires_the_smtp_variables(self):
        result = self.start(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend', EMAIL_HOST='')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('EMAIL_HOST est obligatoire', result.stderr)

    def test_s3_requires_its_variables_only_when_enabled(self):
        complete = {'S3_ENDPOINT_URL': 'http://minio-serveur:9000', 'S3_BUCKET_NAME': 'bucket-test',
                    'S3_ACCESS_KEY': 'cle-applicative', 'S3_SECRET_KEY': 'secret-applicatif'}
        for name in complete:
            with self.subTest(variable=name):
                enabled = self.start(USE_S3='true', **{**complete, name: ''})
                self.assertNotEqual(enabled.returncode, 0)
                self.assertIn(f'{name} est obligatoire', enabled.stderr)

        disabled = self.start(USE_S3='false', S3_BUCKET_NAME='')
        self.assertEqual(disabled.returncode, 0, disabled.stderr)

    def test_s3_enabled_with_all_variables_starts(self):
        result = self.start(USE_S3='true', S3_ENDPOINT_URL='http://minio-serveur:9000', S3_BUCKET_NAME='bucket-test',
                            S3_ACCESS_KEY='cle-applicative', S3_SECRET_KEY='secret-applicatif')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_legacy_gcs_variables_are_ignored(self):
        result = self.start(USE_GCS='true', GS_BUCKET_NAME='', USE_S3='false')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_tuning_values_are_constants_not_environment(self):
        from django.conf import settings
        self.assertEqual(settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'], '10/minute')
        self.assertEqual(settings.AUTH_COOKIE_SAMESITE, 'Lax')
        self.assertEqual(settings.AUTH_COOKIE_REFRESH_PATH, '/api/auth')
        with patch.dict(os.environ, {'LOGIN_RATE': '1/second', 'AUTH_COOKIE_SAMESITE': 'None'}):
            result = self.start(LOGIN_RATE='1/second', AUTH_COOKIE_SAMESITE='None')
        self.assertEqual(result.returncode, 0, result.stderr)  # ces variables n'existent plus : ignorées


class PasswordPolicyTests(SimpleTestCase):
    """Les nouveaux mots de passe doivent faire au moins 12 caractères (la connexion des anciens comptes n'est pas touchée)."""

    def test_eleven_characters_are_refused(self):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            validate_password('Abcdefgh-12')  # 11 caractères

    def test_twelve_characters_are_accepted(self):
        from django.contrib.auth.password_validation import validate_password
        validate_password('Abcdefgh-123x')

    def test_numeric_passwords_are_still_refused(self):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            validate_password('123456789012')
