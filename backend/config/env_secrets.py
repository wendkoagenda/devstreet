"""
Lecture et validation des secrets de signature (SECRET_KEY, JWT_SIGNING_KEY)
et des identifiants du compte administrateur (ADMIN_EMAIL, ADMIN_PASSWORD).

Aucune valeur par défaut : si une variable est absente, trop faible, copiée depuis un exemple
ou invalide, Django refuse de démarrer (en développement comme en production).
"""
import os

from django.core.exceptions import ImproperlyConfigured

MIN_SECRET_LENGTH = 50

# Débuts de valeurs reconnus comme des exemples à ne jamais utiliser
FORBIDDEN_PREFIXES = ('django-insecure', 'votre-', 'change-me', 'changeme', 'your-', 'secret')

GENERATE_HINT = (
    'Générer une valeur : python -c "import secrets; print(secrets.token_urlsafe(64))"'
)


def read_secret(name: str) -> str:
    """Lit une variable d'environnement secrète et refuse toute valeur faible."""
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        raise ImproperlyConfigured(f'{name} est obligatoire (variable absente ou vide). {GENERATE_HINT}')
    value = raw_value.strip()
    if len(value) < MIN_SECRET_LENGTH:
        raise ImproperlyConfigured(
            f'{name} est trop courte ({len(value)} caractères, minimum {MIN_SECRET_LENGTH}). {GENERATE_HINT}'
        )
    if value.lower().startswith(FORBIDDEN_PREFIXES):
        raise ImproperlyConfigured(f'{name} contient une valeur d\'exemple. {GENERATE_HINT}')
    return value


def read_signing_secrets() -> tuple:
    """Retourne (SECRET_KEY, JWT_SIGNING_KEY) ; les deux doivent exister et être différentes."""
    secret_key = read_secret('SECRET_KEY')
    jwt_signing_key = read_secret('JWT_SIGNING_KEY')
    if secret_key == jwt_signing_key:
        raise ImproperlyConfigured(
            'JWT_SIGNING_KEY doit être différente de SECRET_KEY : une fuite de l\'une ne doit pas '
            'permettre de forger l\'autre. ' + GENERATE_HINT
        )
    return secret_key, jwt_signing_key


MIN_ADMIN_PASSWORD_LENGTH = 12


def read_admin_credentials() -> tuple:
    """Retourne (ADMIN_EMAIL, ADMIN_PASSWORD) : obligatoires, jamais écrits dans le code."""
    raw_email = os.getenv('ADMIN_EMAIL')
    if raw_email is None or not raw_email.strip():
        raise ImproperlyConfigured('ADMIN_EMAIL est obligatoire (variable absente ou vide).')
    email = raw_email.strip()
    if '@' not in email or email.startswith('@') or email.endswith('@'):
        raise ImproperlyConfigured(f'ADMIN_EMAIL n\'est pas une adresse e-mail valide : {email!r}.')

    raw_password = os.getenv('ADMIN_PASSWORD')
    if raw_password is None or not raw_password.strip():
        raise ImproperlyConfigured('ADMIN_PASSWORD est obligatoire (variable absente ou vide).')
    password = raw_password.strip()
    if len(password) < MIN_ADMIN_PASSWORD_LENGTH:
        raise ImproperlyConfigured(
            f'ADMIN_PASSWORD est trop court ({len(password)} caractères, minimum {MIN_ADMIN_PASSWORD_LENGTH}).'
        )
    return email, password
