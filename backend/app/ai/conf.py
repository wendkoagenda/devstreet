"""Configuration facultative de l'app IA : aucun appel externe sans clé explicite."""

import os
from django.conf import settings


def config(name, default=""):
    key = f"AI_{name}"
    if hasattr(settings, key):
        return getattr(settings, key)
    if key in os.environ:
        return os.environ[key]
    return default
