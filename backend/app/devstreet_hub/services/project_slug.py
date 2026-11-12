"""Génération de slugs projet uniques, sans dépendre du frontend."""

from __future__ import annotations

import re
import unicodedata

from django.utils.text import slugify

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def normalize_slug(value: str, *, max_length: int = 100) -> str:
    raw = unicodedata.normalize("NFKD", value or "")
    ascii_text = raw.encode("ascii", "ignore").decode("ascii")
    slug = slugify(ascii_text).strip("-")[:max_length].strip("-")
    return slug


def is_valid_slug(value: str) -> bool:
    return bool(value) and len(value) <= 100 and bool(_SLUG_RE.fullmatch(value))


def allocate_unique_slug(base: str, *, exists, max_length: int = 100) -> str:
    """Retourne un slug libre. `exists(slug) -> bool` teste l'occupation."""
    root = normalize_slug(base, max_length=max_length) or "projet"
    candidate = root[:max_length]
    if not exists(candidate):
        return candidate
    # Suffixe -2, -3… en respectant la longueur max.
    index = 2
    while index < 10_000:
        suffix = f"-{index}"
        trimmed = root[: max(1, max_length - len(suffix))].rstrip("-")
        candidate = f"{trimmed}{suffix}"
        if not exists(candidate):
            return candidate
        index += 1
    raise RuntimeError("Impossible d'allouer un slug unique.")
