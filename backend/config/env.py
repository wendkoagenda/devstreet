"""
Lecture des variables d'environnement SANS valeur de repli.

Une variable absente est une erreur de configuration : Django refuse de démarrer avec un message
qui nomme la variable, au lieu de la remplacer en silence par une valeur qui peut être fausse en production.
"""
import os
from typing import List, Optional

from django.core.exceptions import ImproperlyConfigured

TRUE_VALUES = ('1', 'true', 'yes')
FALSE_VALUES = ('0', 'false', 'no')


def required(name: str) -> str:
    """Valeur d'une variable obligatoire (absente, vide ou blanche : erreur)."""
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ImproperlyConfigured(f'{name} est obligatoire (variable absente ou vide).')
    return value.strip()


def required_bool(name: str) -> bool:
    """Booléen obligatoire : true/false (1/0, yes/no). Toute autre valeur est une erreur."""
    value = required(name).lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    raise ImproperlyConfigured(f'{name} doit valoir true ou false (valeur reçue : {value!r}).')


def required_list(name: str) -> List[str]:
    """Liste obligatoire séparée par des virgules (au moins un élément non vide)."""
    items = [item.strip() for item in required(name).split(',') if item.strip()]
    if not items:
        raise ImproperlyConfigured(f'{name} doit contenir au moins une valeur (séparées par des virgules).')
    return items


def optional(name: str) -> Optional[str]:
    """Variable réellement facultative : None si absente ou vide (l'absence est gérée explicitement par l'appelant)."""
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    return value.strip()
