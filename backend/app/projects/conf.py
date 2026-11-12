"""Configuration facultative du module : aucun appel externe sans configuration explicite."""

import os
from django.conf import settings


def config(name, default=""):
    key = f"PROJECTS_{name}"
    if hasattr(settings, key):
        return getattr(settings, key)
    if key in os.environ:
        return os.environ[key]
    # Paramètres facultatifs uniquement ; un adaptateur non configuré renvoie 503.
    return default
