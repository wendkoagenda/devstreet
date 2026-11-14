"""Service centralisé pour la gestion du stockage de fichiers.

Deux backends, choisis par ``USE_S3`` (voir config/settings.py) :
- ``USE_S3=False`` : disque local (FileSystemStorage, ``MEDIA_ROOT``) ;
- ``USE_S3=True``  : bucket S3/MinIO **privé**. Aucun objet n'a d'URL publique : les fichiers ne sont lus que par
  l'endpoint authentifié ``/api/v1/files/<chemin>`` (app/metier/views/file_views.py).
"""
import logging
import os
from typing import Optional, Union
from urllib.parse import quote

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile


logger = logging.getLogger(__name__)


# Les fonctions de normalisation ont été déplacées côté frontend
# Voir frontend/src/helpers/file-utils.ts


class StorageService:
    """
    Service centralisé pour la gestion du stockage de fichiers.
    """

    def __init__(self):
        self._storage_backend = None
        self._is_s3_enabled = None
        self._initialize_storage()

    def _initialize_storage(self):
        """
        Initialise le backend de stockage selon la configuration.

        Si ``USE_S3=True`` mais l'initialisation échoue (variables manquantes, dépendance absente, etc.), on lève
        l'exception : c'est un échec de configuration explicite qui doit empêcher le démarrage du backend plutôt
        que de fallback silencieusement sur le disque éphémère du container.
        """
        self._is_s3_enabled = settings.USE_S3

        logger.info("[INIT] StorageService - Initialisation")
        logger.info("  USE_S3: %s", self._is_s3_enabled)

        if self._is_s3_enabled:
            self._initialize_s3_storage()
        else:
            logger.warning("[WARNING] USE_S3=False, utilisation du stockage local")
            self._initialize_local_storage()

    def _initialize_s3_storage(self):
        """
        Initialise le stockage S3/MinIO (bucket privé, accès par clés applicatives uniquement).
        """
        try:
            from storages.backends.s3 import S3Storage  # type: ignore
        except ImportError as exc:
            logger.error("[ERROR] django-storages[s3] non disponible")
            raise ImproperlyConfigured("django-storages[s3] et boto3 sont requis pour USE_S3=True") from exc

        for name in ('S3_ENDPOINT_URL', 'S3_BUCKET_NAME', 'S3_ACCESS_KEY', 'S3_SECRET_KEY'):
            if not getattr(settings, name):
                raise ImproperlyConfigured(f"{name} est requis pour USE_S3=True")

        self._storage_backend = S3Storage(
            bucket_name=settings.S3_BUCKET_NAME,
            endpoint_url=settings.S3_ENDPOINT_URL,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            region_name='us-east-1',  # MinIO ignore la région, boto3 en exige une
            signature_version='s3v4',
            addressing_style='path',  # MinIO : http://hote:9000/<bucket>/<clé>, pas de sous-domaine par bucket
            default_acl=None,
            querystring_auth=False,  # aucune URL signée n'est jamais produite : la lecture passe par l'application
            file_overwrite=False,
            location='',  # Racine du bucket
        )

        logger.info("[SUCCESS] S3Storage initialisé (bucket=%s, endpoint=%s)", settings.S3_BUCKET_NAME, settings.S3_ENDPOINT_URL)

    def _initialize_local_storage(self):
        """
        Initialise le stockage local (FileSystemStorage).
        """
        from django.core.files.storage import FileSystemStorage

        # MEDIA_ROOT et MEDIA_URL sont définis dans config/settings.py : pas de valeur de repli ici
        media_root = settings.MEDIA_ROOT
        media_url = settings.MEDIA_URL

        # Créer le dossier s'il n'existe pas
        os.makedirs(media_root, exist_ok=True)

        self._storage_backend = FileSystemStorage(
            location=media_root,
            base_url=media_url
        )

        logger.info("[SUCCESS] FileSystemStorage initialisé")
        logger.info("  MEDIA_ROOT: %s", media_root)
        logger.info("  MEDIA_URL: %s", media_url)

    @property
    def backend(self):
        """
        Retourne le backend de stockage configuré.
        """
        return self._storage_backend

    @property
    def is_s3_enabled(self) -> bool:
        """
        Indique si le stockage S3/MinIO est activé.
        """
        return self._is_s3_enabled

    # Les méthodes de normalisation ont été déplacées côté frontend

    def save(self, name: str, content: Union[ContentFile, bytes], max_length: Optional[int] = None) -> str:
        """
        Sauvegarde un fichier avec le backend configuré.

        Args:
            name: Nom du fichier (déjà normalisé côté frontend)
            content: Contenu du fichier (ContentFile ou bytes)
            max_length: Longueur maximale du nom de fichier

        Returns:
            str: Chemin du fichier sauvegardé
        """
        try:
            if isinstance(content, bytes):
                content = ContentFile(content)

            # Le nom de fichier est déjà normalisé côté frontend
            logger.info("Sauvegarde fichier: %s", name)
            logger.info("  Backend: %s", self._storage_backend.__class__.__name__)
            logger.info("  Taille: %s bytes", content.size if hasattr(content, 'size') else 'inconnue')

            saved_path = self._storage_backend.save(name, content, max_length)

            logger.info("Fichier sauvegardé: %s", saved_path)
            return saved_path

        except Exception as e:
            logger.error("Erreur sauvegarde fichier %s: %s", name, e)
            raise

    def delete(self, name: str) -> bool:
        """
        Supprime un fichier.

        Args:
            name: Nom du fichier à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        if self.exists(name):
            self._storage_backend.delete(name)
            logger.info("Fichier supprimé: %s", name)
            return True
        else:
            logger.warning("Fichier inexistant: %s", name)
            return False

    def exists(self, name: str) -> bool:
        """
        Vérifie si un fichier existe.

        Args:
            name: Nom du fichier

        Returns:
            bool: True si le fichier existe
        """
        return self._storage_backend.exists(name)

    def open(self, name: str, mode: str = 'rb'):
        """Ouvre un fichier en lecture (utilisé par l'endpoint authentifié /api/v1/files/)."""
        return self._storage_backend.open(name, mode)

    def size(self, name: str) -> int:
        """Taille d'un fichier en octets."""
        return self._storage_backend.size(name)

    def url(self, name: str) -> str:
        """
        Retourne l'URL d'accès au fichier.

        Avec S3, c'est l'URL de l'endpoint authentifié de l'application (jamais une URL du bucket).
        En local, c'est l'URL ``/media/…``.

        Args:
            name: Nom du fichier

        Returns:
            str: URL du fichier
        """
        if self._is_s3_enabled:
            if name.startswith(settings.FILES_URL):
                return name
            return f"{settings.FILES_URL}{quote(name.lstrip('/'), safe='/')}"

        # Pour le stockage local, vérifier si le nom contient déjà le préfixe media
        media_url = settings.MEDIA_URL

        # Si le nom commence déjà par /media/, le retourner tel quel
        if name.startswith('/media/'):
            return name

        # Sinon, ajouter le préfixe media
        if not media_url.endswith('/'):
            media_url += '/'
        return f"{media_url}{name}"

    def get_storage_info(self) -> dict:
        """
        Retourne les informations sur la configuration du stockage.

        Returns:
            dict: Informations de configuration
        """
        info = {
            'backend_class': self._storage_backend.__class__.__name__,
            'is_s3_enabled': self._is_s3_enabled,
        }

        if self._is_s3_enabled:
            info.update({
                'bucket_name': settings.S3_BUCKET_NAME,
                'endpoint_url': settings.S3_ENDPOINT_URL,
            })
        else:
            info.update({
                'media_root': str(settings.MEDIA_ROOT),
                'media_url': settings.MEDIA_URL,
            })

        return info


# Instance globale du service (singleton pattern)
_storage_service_instance = None


def get_storage_service() -> StorageService:
    """
    Retourne l'instance globale du StorageService (singleton).

    Returns:
        StorageService: Instance du service de stockage
    """
    global _storage_service_instance

    if _storage_service_instance is None:
        _storage_service_instance = StorageService()

    return _storage_service_instance


# Export des fonctions utilitaires
__all__ = ['StorageService', 'get_storage_service']
