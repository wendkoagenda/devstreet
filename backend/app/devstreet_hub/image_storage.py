"""Images Hub privées : ACL via la route projet, jamais via MEDIA_URL ni /api/v1/files/.

- ``USE_S3=True`` : objets MinIO sous le préfixe ``hub_project_images/`` (même bucket, lecture
  uniquement par ``GET /api/v1/projects/{id}/presentation/images/{id}``).
- ``USE_S3=False`` : disque ``DEVSTREET_HUB_PRIVATE_IMAGE_ROOT`` (hors MEDIA_ROOT).
"""
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible


# Préfixe S3 / clé objet. Aussi refusé par l'endpoint générique /api/v1/files/.
HUB_PROJECT_IMAGES_PREFIX = 'hub_project_images'


@deconstructible
class ProjectImageStorage(Storage):
    """Stockage des images de présentation de projet (S3 ou disque privé)."""

    def __eq__(self, other):
        return isinstance(other, ProjectImageStorage)

    def deconstruct(self):
        return ('app.devstreet_hub.image_storage.ProjectImageStorage', [], {})

    def _local_backend(self):
        root = Path(settings.DEVSTREET_HUB_PRIVATE_IMAGE_ROOT)
        root.mkdir(parents=True, exist_ok=True)
        return FileSystemStorage(location=str(root.resolve()))

    def _backend(self):
        if settings.USE_S3:
            from app.metier.services.storage_service import get_storage_service

            return get_storage_service().backend
        return self._local_backend()

    def _full_name(self, name: str) -> str:
        """Avec S3, force le préfixe privé ; en local, le dossier privé suffit."""
        cleaned = (name or '').lstrip('/')
        if not settings.USE_S3:
            return cleaned
        prefix = HUB_PROJECT_IMAGES_PREFIX + '/'
        if cleaned.startswith(prefix) or cleaned == HUB_PROJECT_IMAGES_PREFIX:
            return cleaned
        return prefix + cleaned

    def _open(self, name, mode='rb'):
        return self._backend().open(self._full_name(name), mode)

    def _save(self, name, content):
        return self._backend().save(self._full_name(name), content)

    def delete(self, name):
        full = self._full_name(name)
        backend = self._backend()
        if backend.exists(full):
            backend.delete(full)

    def exists(self, name):
        return self._backend().exists(self._full_name(name))

    def size(self, name):
        return self._backend().size(self._full_name(name))

    def url(self, name):
        raise ValueError('Utiliser la route image du projet, soumise aux permissions.')

    def get_accessed_time(self, name):
        return self._backend().get_accessed_time(self._full_name(name))

    def get_created_time(self, name):
        return self._backend().get_created_time(self._full_name(name))

    def get_modified_time(self, name):
        return self._backend().get_modified_time(self._full_name(name))

    def path(self, name):
        # Uniquement disque local ; S3 lève NotImplementedError via le backend.
        return self._backend().path(self._full_name(name))
