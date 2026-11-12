"""Importe tous les modules de règles (l'import les enregistre dans le registre)."""
from . import (  # noqa: F401
    api_rules,
    config_rules,
    django_rules,
    exposure_rules,
    fallback_rules,
    frontend_rules,
    infra_rules,
    python_rules,
    secret_rules,
)
