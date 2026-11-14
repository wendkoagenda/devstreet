"""
Règles sur le nom d'utilisateur, identifiant public du profil (/profil/<nom>).

Le nom est unique sans tenir compte de la casse, et certains noms sont
réservés car ils servent d'alias ou de sous-pages de l'adresse de profil.
"""
from typing import Optional

from django.contrib.auth import get_user_model

# Alias et segments d'adresse de profil qu'un membre ne peut pas prendre.
RESERVED_USERNAMES = frozenset(
    {
        'me',
        'moi',
        'new',
        'nouveau',
        'edit',
        'settings',
        'parametres',
        'entreprise',
        'dev',
        'invitation',
        'invitations',
    }
)

MESSAGE_RESERVED = "Ce nom d'utilisateur est réservé."
MESSAGE_TAKEN = "Ce nom d'utilisateur est déjà pris."


def is_reserved_username(value: str) -> bool:
    """Indique si le nom (sans tenir compte de la casse) est réservé."""
    return (value or '').strip().lower() in RESERVED_USERNAMES


def username_taken(value: str, exclude_pk: Optional[int] = None) -> bool:
    """Indique si un autre utilisateur porte déjà ce nom, à la casse près."""
    queryset = get_user_model().objects.filter(username__iexact=(value or '').strip())
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)
    return queryset.exists()


def check_username(value: str, exclude_pk: Optional[int] = None) -> Optional[str]:
    """
    Vérifie un nom d'utilisateur.

    Returns:
        Optional[str]: message d'erreur en français, ou None si le nom est valide.
    """
    if is_reserved_username(value):
        return MESSAGE_RESERVED
    if username_taken(value, exclude_pk=exclude_pk):
        return MESSAGE_TAKEN
    return None
