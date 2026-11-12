"""Configuration facultative du module : aucun appel externe sans configuration explicite."""

import os
from django.conf import settings

# Réutilise les clés app.ai si DEVSTREET_HUB_* n'est pas défini (une seule config OpenAI).
_AI_FALLBACKS = {
    "OPENAI_API_KEY": "AI_OPENAI_API_KEY",
    "OPENAI_MODEL": "AI_OPENAI_MODEL",
    "AI_DAILY_LIMIT": "AI_DAILY_LIMIT",
    "AI_PROJECT_DAILY_LIMIT": "AI_PROJECT_DAILY_LIMIT",
    "AI_INLINE_WORKER": "AI_INLINE_WORKER",
}


def _read_env_or_settings(key, default=""):
    if hasattr(settings, key):
        value = getattr(settings, key)
        if value not in (None, ""):
            return value
    value = os.environ.get(key)
    if value:
        return value
    return default


def config(name, default=""):
    key = f"DEVSTREET_HUB_{name}"
    value = _read_env_or_settings(key)
    if value not in (None, ""):
        return value
    fallback = _AI_FALLBACKS.get(name)
    if fallback:
        value = _read_env_or_settings(fallback)
        if value not in (None, ""):
            return value
    # Paramètres facultatifs uniquement ; un adaptateur non configuré renvoie 503.
    return default
