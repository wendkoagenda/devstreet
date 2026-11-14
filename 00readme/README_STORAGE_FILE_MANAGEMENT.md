# Gestion des fichiers — stockage local ou S3/MinIO privé

Ce guide décrit comment les fichiers envoyés par les utilisateurs (avatars, logos, images de publication, CV…) sont stockés et lus.

## Vue d'ensemble

| Couche | Fichier | Rôle |
|--------|---------|------|
| Backend | `backend/app/metier/services/storage_service.py` | Écriture, lecture, suppression et URL, selon `USE_S3` |
| Backend | `backend/app/metier/views/file_views.py` | `GET /api/v1/files/<chemin>` : lecture authentifiée des fichiers |
| Frontend | `frontend/src/helpers/displayers/media-url-builder.ts` | Construit l'URL d'affichage d'un chemin enregistré en base |
| Frontend | `frontend/src/helpers/file-name-builder.ts` | Normalise les noms de fichiers avant l'envoi |

```
Navigateur ──upload──▶ API Django ──StorageService.save()──┬─ USE_S3=False → disque local (MEDIA_ROOT)
                                                           └─ USE_S3=True  → bucket S3/MinIO privé

Navigateur ──GET /media/<chemin>──────▶ (local) servi par Nginx / runserver
Navigateur ──GET /api/v1/files/<chemin>──▶ API Django (utilisateur connecté) ──lit le bucket──▶ flux
```

## Principe : le bucket n'a aucune URL publique

Avec `USE_S3=True`, le bucket est **privé** : pas de lecture anonyme (`mc anonymous set none`), pas de route Nginx vers MinIO, pas d'URL signée. Seule l'application possède des clés d'accès (`S3_ACCESS_KEY` / `S3_SECRET_KEY`).

Un fichier n'est lisible que via `GET /api/v1/files/<chemin>` :

- **authentification obligatoire** (cookie JWT, comme le reste de l'API) : un `<img src="/api/v1/files/…">` envoie le cookie automatiquement ;
- **tout utilisateur connecté** peut lire tout fichier (pas de contrôle par propriétaire). `cv_snapshot` est donc lisible par tout membre connecté qui en connaît le chemin ;
- chemin normalisé : `..`, chemin absolu, antislash et octet nul sont refusés (404) ;
- réponse en flux, avec `Content-Type` déduit de l'extension, `X-Content-Type-Options: nosniff`, `Cache-Control: private, max-age=86400` (jamais de cache partagé) et le support de `Range` (lecture et avance rapide des vidéos) ;
- images, vidéos, sons et PDF s'affichent ; tout autre type est téléchargé (`Content-Disposition: attachment`) ;
- limite de débit dédiée `files` (3000/minute par utilisateur), car une page charge beaucoup d'images.

Le mode local (`USE_S3=False`) ne change pas : les fichiers sont dans `MEDIA_ROOT` et servis sous `/media/`. `/api/v1/files/` fonctionne aussi, mais le frontend n'y recourt qu'avec `VITE_USE_S3=true`.

## Variables d'environnement

### Backend (`backend/.env`, voir `.env.example`)

`USE_S3` est obligatoire. Les quatre variables `S3_*` ne le sont que si `USE_S3=True`.

| Variable | Description |
|----------|-------------|
| `USE_S3` | `True` ou `False`. `False` = disque local |
| `S3_ENDPOINT_URL` | Adresse **interne** du serveur S3, sans chemin (ex. `http://minio-serveur:9000`) |
| `S3_BUCKET_NAME` | Nom du bucket (minuscules, 3 à 63 caractères) |
| `S3_ACCESS_KEY`, `S3_SECRET_KEY` | Compte applicatif MinIO (secret) |

Si `USE_S3=True` et que la configuration est invalide (variable manquante, `django-storages[s3]`/`boto3` absents), le backend **refuse de démarrer** : il n'y a **pas** de repli silencieux vers le disque local éphémère du conteneur.

Google Cloud Storage n'est plus pris en charge : `USE_GCS`, `GS_*` et `GCS_UPLOADER_SA` sont ignorés.

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_USE_S3` | Facultative. `true` quand le backend a `USE_S3=True` : un chemin relatif devient `/api/v1/files/<chemin>` au lieu de `/media/<chemin>` |

## Backend — `StorageService`

```python
from app.metier.services.storage_service import get_storage_service

storage = get_storage_service()
```

| Méthode | Rôle |
|---------|------|
| `save(name, content, max_length=None)` | Enregistre le fichier, retourne le chemin final (un nom libre est choisi si besoin : `file_overwrite=False`) |
| `delete(name)` | Supprime le fichier (`False` s'il n'existe pas) |
| `exists(name)` | Teste l'existence |
| `open(name)` / `size(name)` | Lecture (utilisées par `/api/v1/files/`) |
| `url(name)` | `/api/v1/files/<chemin>` avec S3, `/media/<chemin>` en local |
| `get_storage_info()` | Configuration active, sans secret |

Consommateurs : `process_uploaded_files` (`app/metier/utils/file_field_utils.py`), l'upload de média du forum, les médias de profil et les sérialiseurs marketplace.

## Frontend — URLs d'affichage (`media-url-builder.ts`)

`buildMediaUrl(filePath)` :

1. URL absolue (`http://`, `https://`) → inchangée ;
2. `/media/…` ou `/api/v1/files/…` → préfixée par l'origine du backend (déduite de `VITE_API_URL`) ;
3. autre chemin absolu → inchangé ;
4. chemin relatif → `/api/v1/files/<chemin>` si `VITE_USE_S3=true`, sinon `/media/<chemin>`.

## Convention de stockage en base

La base ne stocke que le **chemin relatif** (`forum_images/photo-1731500000.png`), jamais une URL. Le passage du disque à S3 ne demande donc aucune migration de données : il faut seulement copier les fichiers existants vers le bucket, avec les mêmes chemins.

## Vérifier le stockage

```powershell
python manage.py check_storage
```

La commande affiche le backend actif, écrit un fichier de test, vérifie sa présence, le relit, affiche l'URL renvoyée à l'API, puis le supprime. Elle s'arrête au premier échec en nommant l'étape. À lancer après un déploiement avec `USE_S3=True` (dans le conteneur backend).

## Configurations types

**Développement local** : `USE_S3=False` ; `VITE_USE_S3` absente. Fichiers dans `backend/media/`.

**Staging / production avec MinIO** :

1. `backend.env.<branche>` : `USE_S3=True`, `S3_ENDPOINT_URL=http://minio-serveur:9000`, `S3_BUCKET_NAME`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` ;
2. variable de build du frontend : `VITE_USE_S3=true` ;
3. le job **CD - MINIO SSH** provisionne le bucket privé et le compte applicatif (voir `deploy/README.md`).

## Points d'attention

1. **Pas de repli GCS/disque** : avec `USE_S3=True`, corriger la configuration plutôt que d'attendre un repli.
2. **Bucket existant public** : le provisionnement exécute `mc anonymous set none`, ce qui retire un ancien accès public.
3. **Images privées du DevStreet Hub** : `ProjectImageStorage` (`app/devstreet_hub/image_storage.py`) reste un stockage local dédié, hors de `StorageService` ; il n'est pas concerné par `USE_S3`.
4. **Contenu déjà publié** : une URL absolue enregistrée dans le contenu d'une publication (`/media/…` ou `/api/v1/files/…`) est servie telle quelle ; après une bascule vers S3, les anciennes URLs `/media/…` ne sont plus servies que si le volume local existe encore.
5. **Tests** : `app/tests/test_storage_files.py` (choix du backend, URL, accès authentifié, `Range`, chemins interdits).

## Fichiers de référence

| Fichier | Contenu |
|---------|---------|
| `backend/config/settings.py` | `USE_S3`, `S3_*`, `FILES_URL`, `MEDIA_*` |
| `backend/app/metier/services/storage_service.py` | `StorageService` |
| `backend/app/metier/views/file_views.py` | Endpoint `/api/v1/files/` |
| `backend/app/metier/management/commands/check_storage.py` | Commande de vérification |
| `frontend/src/helpers/displayers/media-url-builder.ts` | URLs d'affichage |
| `frontend/src/config/config.ts` | `VITE_USE_S3` |
| `deploy/minio/provisionner.sh` | Bucket privé et compte applicatif |
