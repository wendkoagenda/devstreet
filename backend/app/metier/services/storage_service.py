"""Service centralisé pour la gestion du stockage de fichiers.
Gère automatiquement le choix entre GoogleCloudStorage et FileSystemStorage
selon la configuration de l'environnement.
"""
import json
import os
import logging
from typing import Optional, Union
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.exceptions import ImproperlyConfigured


logger = logging.getLogger(__name__)


def _load_gcs_credentials():
    """Construit des credentials Google à partir de ``GCS_UPLOADER_SA``.

    La variable d'environnement doit contenir la clé d'un service account GCP
    au format JSON, sur une seule ligne (collée telle quelle depuis la console GCP).
    """
    from google.oauth2 import service_account

    # settings.GCS_UPLOADER_SA est obligatoire dès que USE_GCS est actif (voir config/settings.py)
    sa_json = settings.GCS_UPLOADER_SA
    if not sa_json:
        raise ImproperlyConfigured(
            "GCS_UPLOADER_SA est requis (clé de service account GCP au format JSON, sur une seule ligne)."
        )

    try:
        sa_info = json.loads(sa_json)
    except json.JSONDecodeError as exc:
        raise ImproperlyConfigured(
            f"GCS_UPLOADER_SA doit contenir un JSON valide. Erreur de parsing: {exc}"
        ) from exc

    logger.info(
        "[GCS] Credentials chargées depuis GCS_UPLOADER_SA (client_email=%s)",
        sa_info.get("client_email", "?"),
    )
    return service_account.Credentials.from_service_account_info(sa_info)


# Les fonctions de normalisation ont été déplacées côté frontend
# Voir frontend/src/helpers/file-utils.ts


class StorageService:
    """
    Service centralisé pour la gestion du stockage de fichiers.
    """
    
    def __init__(self):
        self._storage_backend = None
        self._is_gcs_enabled = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """
        Initialise le backend de stockage selon la configuration.

        Si ``USE_GCS=True`` mais l'initialisation GCS échoue (variables manquantes,
        clé SA invalide, etc.), on lève l'exception : c'est un échec de
        configuration explicite qui doit empêcher le démarrage du backend plutôt
        que de fallback silencieusement sur le disque éphémère du container.
        """
        self._is_gcs_enabled = settings.USE_GCS

        gs_bucket = settings.GS_BUCKET_NAME
        gs_project = settings.GS_PROJECT_ID

        logger.info("[INIT] StorageService - Initialisation")
        logger.info("  USE_GCS: %s", self._is_gcs_enabled)
        logger.info("  GS_BUCKET_NAME: %s", gs_bucket)
        logger.info("  GS_PROJECT_ID: %s", gs_project)

        if self._is_gcs_enabled:
            # GCS est explicitement demandé -> toute erreur doit remonter.
            self._initialize_gcs_storage()
        else:
            logger.warning("[WARNING] USE_GCS=False, utilisation du stockage local")
            self._initialize_local_storage()
    
    def _initialize_gcs_storage(self):
        """
        Initialise Google Cloud Storage.

        Les credentials sont chargées exclusivement via ``GCS_UPLOADER_SA``
        (JSON inline du service account GCP).
        """
        try:
            from storages.backends.gcloud import GoogleCloudStorage  # type: ignore

            bucket_name = settings.GS_BUCKET_NAME
            project_id = settings.GS_PROJECT_ID

            if not bucket_name:
                raise ImproperlyConfigured("GS_BUCKET_NAME est requis pour GCS")
            if not project_id:
                raise ImproperlyConfigured("GS_PROJECT_ID est requis pour GCS")

            credentials = _load_gcs_credentials()

            self._storage_backend = GoogleCloudStorage(
                bucket_name=bucket_name,
                project_id=project_id,
                credentials=credentials,
                default_acl=None,  # UBLA activée
                file_overwrite=False,
                location='',  # Racine du bucket
            )

            logger.info(f"[SUCCESS] GoogleCloudStorage initialisé")
            logger.info(f"  Bucket: {bucket_name}")
            logger.info(f"  Project: {project_id}")

        except ImportError:
            logger.error("[ERROR] django-storages[google] non disponible")
            raise ImproperlyConfigured("django-storages[google] est requis pour GCS")
        except Exception as e:
            logger.error(f"[ERROR] Erreur initialisation GCS: {e}")
            raise
    
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
        
        logger.info(f"[SUCCESS] FileSystemStorage initialisé")
        logger.info(f"  MEDIA_ROOT: {media_root}")
        logger.info(f"  MEDIA_URL: {media_url}")
    
    @property
    def backend(self):
        """
        Retourne le backend de stockage configuré.
        """
        return self._storage_backend
    
    @property
    def is_gcs_enabled(self) -> bool:
        """
        Indique si GCS est activé.
        """
        return self._is_gcs_enabled
    
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
            logger.info(f"Sauvegarde fichier: {name}")
            logger.info(f"  Backend: {self._storage_backend.__class__.__name__}")
            logger.info(f"  Taille: {content.size if hasattr(content, 'size') else 'inconnue'} bytes")
            
            saved_path = self._storage_backend.save(name, content, max_length)
            
            logger.info(f"Fichier sauvegardé: {saved_path}")
            return saved_path
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde fichier {name}: {e}")
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
            logger.info(f"Fichier supprimé: {name}")
            return True
        else:
            logger.warning(f"Fichier inexistant: {name}")
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
    
    def url(self, name: str) -> str:
        """
        Retourne l'URL d'accès au fichier.
        
        Args:
            name: Nom du fichier
        
        Returns:
            str: URL du fichier
        """
        if self._is_gcs_enabled:
            # Pour GCS, construire l'URL manuellement
            bucket_name = settings.GS_BUCKET_NAME
            if bucket_name:
                return f"https://storage.googleapis.com/{bucket_name}/{name}"
            else:
                return self._storage_backend.url(name)
        else:
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
            'is_gcs_enabled': self._is_gcs_enabled,
        }
        
        if self._is_gcs_enabled:
            info.update({
                'bucket_name': settings.GS_BUCKET_NAME,
                'project_id': settings.GS_PROJECT_ID,
            })
        else:
            info.update({
                'media_root': settings.MEDIA_ROOT,
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


