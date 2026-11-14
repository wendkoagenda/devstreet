"""Stockage de fichiers : choix du backend (USE_S3), URLs sans exposition publique, lecture authentifiée /api/v1/files/."""
import shutil
import sys
import tempfile
import types
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

import app.metier.services.storage_service as storage_module
from app.metier.services.storage_service import StorageService
from app.metier.views.file_views import normalize_file_path, parse_range

S3_SETTINGS = dict(
    USE_S3=True,
    S3_ENDPOINT_URL='http://minio-serveur:9000',
    S3_BUCKET_NAME='bucket-test',
    S3_ACCESS_KEY='cle-applicative',
    S3_SECRET_KEY='secret-applicatif',
)


def fake_s3_module():
    """Module `storages.backends.s3` factice : django-storages n'a pas besoin d'être installé pour tester."""
    s3 = types.ModuleType('storages.backends.s3')
    s3.S3Storage = MagicMock(name='S3Storage')
    backends = types.ModuleType('storages.backends')
    backends.s3 = s3
    root = types.ModuleType('storages')
    root.backends = backends
    return {'storages': root, 'storages.backends': backends, 'storages.backends.s3': s3}, s3.S3Storage


class StorageBackendChoiceTests(SimpleTestCase):
    def setUp(self):
        self.media_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

    def test_local_storage_when_s3_is_disabled(self):
        with override_settings(USE_S3=False, MEDIA_ROOT=self.media_root):
            service = StorageService()
        self.assertFalse(service.is_s3_enabled)
        self.assertEqual(service.backend.__class__.__name__, 'FileSystemStorage')

    def test_local_url_keeps_the_media_prefix(self):
        with override_settings(USE_S3=False, MEDIA_ROOT=self.media_root, MEDIA_URL='/media/'):
            service = StorageService()
            self.assertEqual(service.url('forum_images/a.png'), '/media/forum_images/a.png')
            self.assertEqual(service.url('/media/forum_images/a.png'), '/media/forum_images/a.png')

    def test_s3_storage_is_built_from_the_settings(self):
        modules, s3_class = fake_s3_module()
        with override_settings(**S3_SETTINGS), patch.dict(sys.modules, modules):
            service = StorageService()
        self.assertTrue(service.is_s3_enabled)
        options = s3_class.call_args.kwargs
        self.assertEqual(options['bucket_name'], 'bucket-test')
        self.assertEqual(options['endpoint_url'], 'http://minio-serveur:9000')
        self.assertEqual(options['access_key'], 'cle-applicative')
        self.assertEqual(options['addressing_style'], 'path')
        self.assertFalse(options['querystring_auth'])  # aucune URL signée
        self.assertIsNone(options['default_acl'])

    def test_s3_url_is_the_authenticated_endpoint_never_the_bucket(self):
        modules, _ = fake_s3_module()
        with override_settings(**S3_SETTINGS), patch.dict(sys.modules, modules):
            service = StorageService()
            self.assertEqual(service.url('forum_images/photo 1.png'), '/api/v1/files/forum_images/photo%201.png')
            self.assertEqual(service.url('/api/v1/files/a.png'), '/api/v1/files/a.png')
            self.assertNotIn('minio', service.url('a.png'))
            self.assertNotIn('bucket-test', service.url('a.png'))

    def test_s3_missing_variable_stops_the_service(self):
        modules, _ = fake_s3_module()
        with override_settings(**{**S3_SETTINGS, 'S3_BUCKET_NAME': None}), patch.dict(sys.modules, modules):
            with self.assertRaisesMessage(ImproperlyConfigured, 'S3_BUCKET_NAME'):
                StorageService()

    def test_s3_without_django_storages_stops_the_service(self):
        # None dans sys.modules fait échouer l'import : jamais de repli silencieux sur le disque
        with override_settings(**S3_SETTINGS), patch.dict(sys.modules, {'storages.backends.s3': None}):
            with self.assertRaisesMessage(ImproperlyConfigured, 'django-storages[s3]'):
                StorageService()

    def test_storage_info_never_exposes_the_secrets(self):
        modules, _ = fake_s3_module()
        with override_settings(**S3_SETTINGS), patch.dict(sys.modules, modules):
            info = StorageService().get_storage_info()
        self.assertEqual(info['bucket_name'], 'bucket-test')
        self.assertNotIn('secret-applicatif', str(info))
        self.assertNotIn('cle-applicative', str(info))


class FilePathTests(SimpleTestCase):
    def test_normalize_accepts_relative_paths(self):
        self.assertEqual(normalize_file_path('forum_images/a.png'), 'forum_images/a.png')
        self.assertEqual(normalize_file_path('a/./b.png'), 'a/b.png')

    def test_normalize_refuses_paths_leaving_the_storage(self):
        for raw in ('', '..', '../secret', 'a/../../secret', '/etc/passwd', 'a\\b', 'a\x00b', '.'):
            with self.subTest(path=raw):
                self.assertIsNone(normalize_file_path(raw))

    def test_range_parsing(self):
        self.assertEqual(parse_range('bytes=0-9', 100), (0, 9))
        self.assertEqual(parse_range('bytes=90-', 100), (90, 99))
        self.assertEqual(parse_range('bytes=-10', 100), (90, 99))
        self.assertEqual(parse_range('bytes=50-500', 100), (50, 99))
        for header in ('bytes=100-', 'bytes=9-1', 'bytes=-', 'bytes=0-1,5-6', 'items=0-1', 'bytes=-0'):
            with self.subTest(header=header):
                self.assertIsNone(parse_range(header, 100))


class StoredFileApiTests(APITestCase):
    CONTENT = b'0123456789' * 10

    def setUp(self):
        self.media_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)
        override = override_settings(USE_S3=False, MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)
        # Le service est un singleton : on le reconstruit pour pointer sur le dossier temporaire
        patcher = patch.object(storage_module, '_storage_service_instance', None)
        patcher.start()
        self.addCleanup(patcher.stop)

        (self.media_root / 'forum_images').mkdir()
        (self.media_root / 'forum_images' / 'a.png').write_bytes(self.CONTENT)
        (self.media_root / 'forum_files').mkdir()
        (self.media_root / 'forum_files' / 'page.html').write_bytes(b'<script>alert(1)</script>')

        self.user = get_user_model().objects.create_user(
            username='awa@example.com', email='awa@example.com', password='pass12345', first_name='Awa', last_name='Kone'
        )

    def login(self):
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def body(self, response):
        return b''.join(response.streaming_content)

    def test_anonymous_is_refused(self):
        response = self.client.get('/api/v1/files/forum_images/a.png')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_connected_user_reads_the_file(self):
        self.login()
        response = self.client.get('/api/v1/files/forum_images/a.png')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.body(response), self.CONTENT)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertEqual(response['Content-Length'], str(len(self.CONTENT)))
        self.assertEqual(response['Cache-Control'], 'private, max-age=86400')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertTrue(response['Content-Disposition'].startswith('inline'))

    def test_image_tag_accept_header_is_not_refused(self):
        self.login()
        response = self.client.get('/api/v1/files/forum_images/a.png', HTTP_ACCEPT='image/avif,image/webp,*/*;q=0.8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.body(response)

    def test_missing_file_is_404(self):
        self.login()
        self.assertEqual(self.client.get('/api/v1/files/forum_images/absent.png').status_code, status.HTTP_404_NOT_FOUND)

    def test_path_traversal_is_refused(self):
        self.login()
        (self.media_root.parent / 'secret.txt').write_bytes(b'secret')
        self.addCleanup((self.media_root.parent / 'secret.txt').unlink)
        for path in ('forum_images/../../secret.txt', '..%2Fsecret.txt', '../secret.txt'):
            with self.subTest(path=path):
                response = self.client.get(f'/api/v1/files/{path}')
                self.assertIn(response.status_code, (status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST))

    def test_range_request_returns_partial_content(self):
        self.login()
        response = self.client.get('/api/v1/files/forum_images/a.png', HTTP_RANGE='bytes=10-19')
        self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)
        self.assertEqual(self.body(response), self.CONTENT[10:20])
        self.assertEqual(response['Content-Range'], 'bytes 10-19/100')

    def test_unsatisfiable_range_is_416(self):
        self.login()
        response = self.client.get('/api/v1/files/forum_images/a.png', HTTP_RANGE='bytes=500-')
        self.assertEqual(response.status_code, status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
        self.assertEqual(response['Content-Range'], 'bytes */100')

    def test_non_media_types_are_downloaded_not_displayed(self):
        self.login()
        response = self.client.get('/api/v1/files/forum_files/page.html')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response['Content-Disposition'].startswith('attachment'))
        self.body(response)


class StorageCommandsTests(SimpleTestCase):
    def setUp(self):
        self.media_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)
        patcher = patch.object(storage_module, '_storage_service_instance', None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_check_storage_succeeds_on_local_disk_and_cleans_up(self):
        out = StringIO()
        with override_settings(USE_S3=False, MEDIA_ROOT=self.media_root):
            call_command('check_storage', stdout=out)
        self.assertIn('Stockage opérationnel', out.getvalue())
        self.assertEqual(list((self.media_root / 'check_storage').glob('*')), [])

    def test_check_storage_fails_when_s3_is_misconfigured(self):
        with override_settings(**{**S3_SETTINGS, 'S3_ACCESS_KEY': None}), patch.dict(sys.modules, fake_s3_module()[0]):
            with self.assertRaisesMessage(CommandError, 'S3_ACCESS_KEY'):
                call_command('check_storage', stdout=StringIO())

    def test_test_email_sends_through_the_configured_backend(self):
        from django.core import mail
        out = StringIO()
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            call_command('test_email', 'destinataire@example.com', stdout=out)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['destinataire@example.com'])

    def test_test_email_refuses_an_invalid_address(self):
        with self.assertRaisesMessage(CommandError, 'invalide'):
            call_command('test_email', 'pas-une-adresse', stdout=StringIO())
