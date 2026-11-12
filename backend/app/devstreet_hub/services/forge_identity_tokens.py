"""Identifiants opaques et preuves de corrélation pour les comptes Gitea.

Gitea n'offre ni clé d'idempotence ni champ personnalisé à la création
(CreateUserOption : username, email, full_name, password, …).
La preuve retenue est un jeton opaque écrit dans `description` (via PATCH admin)
immédiatement après création, et vérifié à la reprise. Le login dérivé de la
clé n'est qu'un adressage, jamais une preuve d'appartenance à lui seul.
"""

from __future__ import annotations

import hashlib
import re
import uuid

from django.conf import settings

from app.devstreet_hub.conf import config

CORRELATION_PREFIX = "devstreet-hub:pk="
# Gitea Username MaxSize(40) ; alphabet sûr pour un login.
_LOGIN_SAFE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,38}[a-z0-9])?$")


def instance_segment() -> str:
    """Préfixe court pour partager une forge entre plusieurs installations."""
    configured = (config("INSTANCE_ID") or "").strip().lower()
    if configured and re.fullmatch(r"[a-z0-9]{2,8}", configured):
        return configured
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).hexdigest()
    return digest[:8]


def new_provisioning_key() -> uuid.UUID:
    return uuid.uuid4()


def login_for_key(key: uuid.UUID) -> str:
    """Construit un login opaque stable : ds-{instance}-{12 hex} (≤ 24 car.)."""
    login = f"ds-{instance_segment()}-{key.hex[:12]}"
    if len(login) > 40 or not _LOGIN_SAFE.fullmatch(login):
        raise ValueError(f"Login forge invalide généré : {login!r}")
    return login


def correlation_marker(key: uuid.UUID) -> str:
    return f"{CORRELATION_PREFIX}{key}"


def description_with_marker(key: uuid.UUID, *, display_name: str = "") -> str:
    marker = correlation_marker(key)
    base = (display_name or "DevStreet Hub").strip()[:60]
    text = f"{base}\n{marker}"
    return text[:255]


def extract_provisioning_key(description: str | None) -> uuid.UUID | None:
    if not description:
        return None
    match = re.search(
        rf"{re.escape(CORRELATION_PREFIX)}"
        r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
        description,
    )
    if not match:
        return None
    try:
        return uuid.UUID(match.group(1))
    except ValueError:
        return None


def has_correlation(remote_user: dict, key: uuid.UUID) -> bool:
    """Vérifie la preuve écrite côté forge ; login/e-mail seuls ne suffisent pas."""
    found = extract_provisioning_key(remote_user.get("description"))
    return found is not None and found == key
