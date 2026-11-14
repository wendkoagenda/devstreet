"""
Django settings for the devstreet project.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config.env import optional, required, required_bool, required_list  # noqa: E402 (après load_dotenv)
from config.env_secrets import read_admin_credentials, read_signing_secrets  # noqa: E402

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Secrets obligatoires, sans valeur par défaut : SECRET_KEY (Django) et JWT_SIGNING_KEY (jetons JWT),
# distinctes l'une de l'autre. Voir config/env_secrets.py.
SECRET_KEY, JWT_SIGNING_KEY = read_signing_secrets()

# Compte administrateur créé par init_data et les seeds : obligatoire, sans valeur par défaut.
ADMIN_EMAIL, ADMIN_PASSWORD = read_admin_credentials()

# SECURITY WARNING: don't run with debug turned on in production!
# Aucune variable d'environnement n'a de valeur de repli : une variable absente arrête le démarrage
# (voir config/env.py). Les réglages de tuning sont des constantes visibles dans ce fichier.
DEBUG = required_bool('DEBUG')

ALLOWED_HOSTS = required_list('ALLOWED_HOSTS')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
]

LOCAL_APPS = [
    'app',
    'app.core',
    'app.metier',
    'app.metier.legacy_garoapp.apps.GaroappHistoryConfig',
    'app.devstreet_hub',
    'app.ai',
    'app.marketplace',
    'app.communaute',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'app.core.middleware.RequestSizeLimitMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.core.middleware.JWTAuthenticationMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': required('DB_NAME'),
        'USER': required('DB_USER'),
        'PASSWORD': required('DB_PASSWORD'),
        'HOST': required('DB_HOST'),
        'PORT': required('DB_PORT'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'core.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEVSTREET_HUB_PRIVATE_IMAGE_ROOT = BASE_DIR / 'private_uploads' / 'project_images'

# Stockage objet S3/MinIO : USE_S3 est obligatoire ; les réglages S3 ne sont exigés que s'il est actif.
# Sans USE_S3, les fichiers vont sur le disque local (MEDIA_ROOT). Le bucket est privé : les fichiers ne sont lus
# que par l'endpoint authentifié /api/v1/files/<chemin> (voir app/metier/views/file_views.py).
USE_S3 = required_bool('USE_S3')
if USE_S3:
    S3_ENDPOINT_URL = required('S3_ENDPOINT_URL')  # adresse interne de MinIO, ex. http://minio-serveur:9000
    S3_BUCKET_NAME = required('S3_BUCKET_NAME')
    S3_ACCESS_KEY = required('S3_ACCESS_KEY')
    S3_SECRET_KEY = required('S3_SECRET_KEY')
else:
    S3_ENDPOINT_URL = None
    S3_BUCKET_NAME = None
    S3_ACCESS_KEY = None
    S3_SECRET_KEY = None
FILES_URL = '/api/v1/files/'  # URL de lecture authentifiée des fichiers stockés sur S3

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Derrière un reverse proxy de confiance (un seul) : X-Forwarded-Proto est honoré (voir plus bas) et la limitation
# de débit compte chaque visiteur par son adresse réelle (X-Forwarded-For) au lieu de l'adresse du proxy.
BEHIND_PROXY = required_bool('USE_X_FORWARDED_PROTO')

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'app.core.auth.CookieJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'app.core.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    # Limitation de débit par défaut de TOUTES les routes (visiteur anonyme : par IP ; connecté : par utilisateur).
    # Une route peut déclarer une limite plus stricte avec throttle_classes (voir app/core/throttles.py).
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    # Nombre de proxys de confiance devant Django : 1 derrière un reverse proxy, 0 sinon. Jamais None : DRF ferait alors
    # confiance à l'en-tête X-Forwarded-For que n'importe quel client peut forger, et la
    # limitation de débit comme le journal d'audit seraient contournables.
    'NUM_PROXIES': 1 if BEHIND_PROXY else 0,
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '600/minute',
        'files': '3000/minute',  # lecture des fichiers stockés (/api/v1/files/) : une page charge beaucoup d'images
        # Limites propres des routes publiques (par IP)
        'password_reset_request': '5/hour',
        'password_reset_verify': '20/hour',
        'password_reset_confirm': '10/hour',
        # Limitation de débit de la connexion et du rafraîchissement (par IP)
        'login': '10/minute',
        'register': '5/minute',
        'token_refresh': '30/minute',
        'token_verify': '60/minute',
        'logout': '30/minute',
        'csrf': '60/minute',
        'health': '60/minute',
        'oauth_providers': '60/minute',
        'oauth_start': '20/minute',
        'oauth_callback': '20/minute',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}

# Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': JWT_SIGNING_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS settings
CORS_ALLOWED_ORIGINS = required_list('CORS_ALLOWED_ORIGINS')

CORS_ALLOW_CREDENTIALS = True

# En DEBUG : téléphone sur le LAN / tunnel Cloudflare (Vite proxy).
# Sans ça, les POST (like, commentaire, message) renvoient 403 CSRF.
if DEBUG:
    import socket
    import sys
    from ipaddress import ip_address

    _lan_origins: list[str] = []
    try:
        _hostname = socket.gethostname()
        for _info in socket.getaddrinfo(_hostname, None, socket.AF_INET):
            _ip = _info[4][0]
            try:
                _addr = ip_address(_ip)
            except ValueError:
                print(f'CORS LAN : adresse ignorée ({_ip})', file=sys.stderr)
                continue
            if _addr.is_private and not _addr.is_loopback:
                _lan_origins.append(f'http://{_ip}:5173')
    except OSError as _error:
        print(f'CORS LAN : détection des adresses impossible ({_error})', file=sys.stderr)

    CORS_ALLOWED_ORIGINS = list(
        dict.fromkeys([*CORS_ALLOWED_ORIGINS, *_lan_origins])
    )
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r'^https://[a-z0-9-]+\.trycloudflare\.com$',
        r'^https://[a-z0-9-]+\.ngrok-free\.app$',
        r'^https://[a-z0-9-]+\.ngrok\.io$',
    ]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Autoriser les en-têtes personnalisés
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header. You can use either "Bearer {token}" or just "{token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'SECURITY': [
        {
            'Bearer': []
        }
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEFAULT_MODELS_EXPAND_DEPTH': 1,
    'DEFAULT_INFO': 'OnePourcent API',
    'DEFAULT_API_URL': None,
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# E-mail (réinitialisation de mot de passe)
# EMAIL_BACKEND est obligatoire : ...console.EmailBackend (développement : e-mails affichés dans la console du serveur)
# ou ...smtp.EmailBackend (production : EMAIL_HOST, EMAIL_HOST_USER et EMAIL_HOST_PASSWORD deviennent obligatoires).
EMAIL_BACKEND = required('EMAIL_BACKEND')
if EMAIL_BACKEND.endswith('smtp.EmailBackend'):
    EMAIL_HOST = required('EMAIL_HOST')
    EMAIL_HOST_USER = required('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = required('EMAIL_HOST_PASSWORD')
else:
    EMAIL_HOST = ''
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = required('DEFAULT_FROM_EMAIL')

# URL publique du frontend (liens présents dans les e-mails)
FRONTEND_URL = required('FRONTEND_URL').rstrip('/')

# OAuth social (Google / GitHub) : facultatif. Absent → routes start en 503, boutons front masqués.
# Callback à déclarer chez le provider : {origine API}/api/auth/oauth/{google|github}/callback
GOOGLE_OAUTH_CLIENT_ID = optional('GOOGLE_OAUTH_CLIENT_ID')
GOOGLE_OAUTH_CLIENT_SECRET = optional('GOOGLE_OAUTH_CLIENT_SECRET')
OAUTH_GITHUB_CLIENT_ID = optional('OAUTH_GITHUB_CLIENT_ID')
OAUTH_GITHUB_CLIENT_SECRET = optional('OAUTH_GITHUB_CLIENT_SECRET')

# Sécurité HTTP : actif hors DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'
# HSTS : 1 an hors DEBUG. Suppose que le site est servi en HTTPS.
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
# La redirection HTTP -> HTTPS est faite par le reverse proxy, pas par Django
SECURE_SSL_REDIRECT = False
# À activer uniquement derrière un reverse proxy de confiance qui pose X-Forwarded-Proto
if BEHIND_PROXY:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Documentation de l'API (Swagger/ReDoc) : à activer explicitement, jamais en production
ENABLE_API_DOCS = required_bool('ENABLE_API_DOCS')

# Interface d'administration Django (/admin/) : à activer explicitement, désactivée par défaut en production.
# Toute la gestion passe par l'API ; l'admin Django contourne les règles d'accès et le journal d'audit de l'API.
ENABLE_ADMIN = required_bool('ENABLE_ADMIN')

# Authentification par cookies HttpOnly (voir app/core/cookies.py et 00readme/README_SAME_ORIGIN_COOKIES.md)
AUTH_COOKIE_ACCESS = 'access_token'
AUTH_COOKIE_REFRESH = 'refresh_token'
AUTH_COOKIE_ACCESS_PATH = '/'
AUTH_COOKIE_REFRESH_PATH = '/api/auth'
AUTH_COOKIE_SECURE = not DEBUG
AUTH_COOKIE_SAMESITE = 'Lax'
AUTH_COOKIE_DOMAIN = None  # cookie limité à l'hôte exact (pas de partage avec d'autres sous-domaines)

# Verrouillage de la connexion par compte, en plus de la limite par adresse IP : après N échecs dans la fenêtre,
# l'e-mail saisi (qu'il existe ou non, pour ne pas révéler les comptes) refuse toute tentative jusqu'à la fin de la fenêtre
LOGIN_LOCKOUT_MAX_FAILURES = 10
LOGIN_LOCKOUT_MINUTES = 15

# Taille maximale d'un fichier téléversé, en Mo : plafond absolu, quel que soit le max_size_mb d'un champ.
# Les requêtes plus grosses (plafond + 1 Mo de multipart) sont refusées avant d'être lues (RequestSizeLimitMiddleware).
UPLOAD_MAX_SIZE_MB = 25
# Corps de requête hors fichiers (JSON, formulaires), en octets
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# Conservation du journal d'audit, en jours (purge par la commande purge_expired_data)
AUDIT_RETENTION_DAYS = 365

# CSRF : le cookie csrftoken doit rester lisible par le JavaScript (en-tête X-CSRFToken)
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
# Origines exactes autorisées à envoyer des requêtes modifiantes (schéma + hôte + port)
CSRF_TRUSTED_ORIGINS = required_list('CSRF_TRUSTED_ORIGINS')

if DEBUG:
    CSRF_TRUSTED_ORIGINS = list(
        dict.fromkeys(
            [
                *CSRF_TRUSTED_ORIGINS,
                *_lan_origins,
                'https://*.trycloudflare.com',
                'https://*.ngrok-free.app',
                'https://*.ngrok.io',
            ]
        )
    )
