"""ProjectImageStorage : disque privé local, ou MinIO sous hub_project_images/."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings

from app.devstreet_hub.image_storage import HUB_PROJECT_IMAGES_PREFIX, ProjectImageStorage


class ProjectImageStorageTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__('shutil').rmtree(self.root, ignore_errors=True))

    def test_local_writes_under_private_root_without_media_url(self):
        with override_settings(USE_S3=False, DEVSTREET_HUB_PRIVATE_IMAGE_ROOT=self.root):
            storage = ProjectImageStorage()
            saved = storage.save('demo.jpg', ContentFile(b'jpeg-bytes'))
            self.assertTrue(storage.exists(saved))
            self.assertEqual(storage.open(saved, 'rb').read(), b'jpeg-bytes')
            self.assertTrue((self.root / saved).is_file())
            with self.assertRaises(ValueError):
                storage.url(saved)

    def test_s3_prefixes_keys_and_delegates_to_storage_service(self):
        backend = MagicMock()
        backend.save.side_effect = lambda name, content, max_length=None: name
        # False : sinon Storage.get_available_name boucle sans fin (exists toujours vrai).
        backend.exists.return_value = False
        backend.open.return_value = ContentFile(b'from-s3')
        service = MagicMock()
        service.backend = backend

        with override_settings(USE_S3=True), patch(
            'app.metier.services.storage_service.get_storage_service',
            return_value=service,
        ):
            storage = ProjectImageStorage()
            saved = storage.save('photo.jpg', ContentFile(b'x'))
            self.assertEqual(saved, f'{HUB_PROJECT_IMAGES_PREFIX}/photo.jpg')
            backend.save.assert_called_once()
            self.assertEqual(
                backend.save.call_args.args[0],
                f'{HUB_PROJECT_IMAGES_PREFIX}/photo.jpg',
            )
            backend.exists.return_value = True
            self.assertEqual(storage.open(saved, 'rb').read(), b'from-s3')
            with self.assertRaises(ValueError):
                storage.url(saved)
