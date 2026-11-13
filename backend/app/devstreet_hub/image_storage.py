"""Images privees : jamais exposees directement par MEDIA_URL."""
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class ProjectImageStorage(FileSystemStorage):
    @property
    def base_location(self):
        return settings.DEVSTREET_HUB_PRIVATE_IMAGE_ROOT

    @property
    def location(self):
        return str(Path(self.base_location).resolve())

    def url(self, name):
        raise ValueError('Utiliser la route image du projet, soumise aux permissions.')
