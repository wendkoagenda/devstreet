# Backend Django (DRF)

API REST de devstreet : authentification JWT, utilisateurs, rôles et permissions, architecture Repository Pattern.

## Prérequis

- Python 3.12
- PostgreSQL
- Environnement virtuel Python

## Installation

Toutes les commandes ci-dessous se lancent depuis `backend/` (sauf la création de la base, qui peut se faire depuis n’importe où si `createdb` / `psql` sont dans le PATH).

### 1. Environnement virtuel Python

```bash
cd backend
python -m venv venv          # crée le dossier venv/
# ou, pour forcer Python 3.12 :
# py -3.12 -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate
```

Active le venv : les `pip` / `python` suivants utilisent cet interpréteur isolé.

### 2. Dépendances

```bash
pip install -r requirements.txt
```

Installe Django, DRF, et les outils du projet (tests, lint, générateur…).

### 3. Variables d'environnement

```bash
cp .env.example .env
```

Copie le modèle, puis **renseigne** au minimum les secrets, `ADMIN_*` et les `DB_*` (voir section suivante et `.env.example`).

### 4. Base de données PostgreSQL

Créer une base vide dont le nom correspond à `DB_NAME` dans `.env` (exemple du modèle : `devstreet_bd`) :

```bash
# Option A — utilitaire PostgreSQL
createdb devstreet_bd

# Option B — via psql
psql -U postgres -c "CREATE DATABASE devstreet_bd;"
```

Puis appliquer le schéma Django :

```bash
python manage.py migrate
```

Crée les tables (users, rôles, etc.) à partir des migrations.

### 5. Données initiales

```bash
python manage.py init_data
```

Crée le compte admin (`ADMIN_EMAIL` / `ADMIN_PASSWORD`) et les rôles / permissions par défaut.

### 6. Serveur de développement

```bash
python manage.py runserver    # http://127.0.0.1:8000
```

Lance l’API en local (rechargement auto à chaque modification).


## Variables d'environnement

Toutes les variables listées dans `.env.example` sont **obligatoires** : Django refuse de démarrer si l'une manque. Modèle : [`backend/.env.example`](.env.example).

| Variable                                       | Rôle                                |
| ---------------------------------------------- | ----------------------------------- |
| `SECRET_KEY`, `JWT_SIGNING_KEY`                | Secrets (50+ caractères, distincts) |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD`                | Compte créé par `init_data`         |
| `DEBUG`, `ALLOWED_HOSTS`                       | Mode debug et hôtes autorisés       |
| `DB_*`                                         | Connexion PostgreSQL                |
| `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | Origines du frontend                |
| `ENABLE_API_DOCS`, `ENABLE_ADMIN`              | Swagger/ReDoc et `/admin/`          |
| `USE_X_FORWARDED_PROTO`                        | `true` derrière un reverse proxy    |
| `FRONTEND_URL`                                 | URL publique (liens e-mails)        |
| `EMAIL_*`                                      | Backend e-mail (`console` en local) |
| `USE_GCS`, `GS_*`, `GCS_UPLOADER_SA`           | Stockage GCS si activé              |

Les réglages de tuning (rate limit, durées JWT, cookies, HSTS…) sont des constantes dans `config/settings.py`.

## Architecture

Flux : `Client → ViewSet → Service → Repository → DB`

- `app/core/` : auth, users, rôles, permissions
- `app/metier/` : domaine métier (modèles générés inclus)
- Chaque app : `interfaces/`, `repositories/`, `services/`, `permissions/`, `views/`, `models.py`, `serializers.py`

Ne pas placer de logique métier dans les vues, ni d'appels ORM dans les services.

## Commandes utiles

```bash
# venv activé, depuis backend/
python manage.py test
python manage.py test app.tests.test_module
python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py init_data
```

## Documentation API

- Swagger : `/swagger/`
- ReDoc : `/redoc/`

(activés si `ENABLE_API_DOCS=true`)

## Liens

- Générateur CRUD : [`scripts/README.md`](scripts/README.md)
- README racine : [`../README.md`](../README.md)
- Docs projet : [`../00readme/`](../00readme/)
