"""Utilitaires de nommage partagés entre générateurs backend et frontend."""
import re
from typing import Any, Dict, Optional

_RESOURCE_PLURAL_RE = re.compile(r"^[a-z][a-z0-9_-]*$")


def pluralize(lower_name: str) -> str:
    if lower_name.endswith(("s", "x", "z", "ch", "sh")):
        return f"{lower_name}es"
    if lower_name.endswith("y") and len(lower_name) > 1 and lower_name[-2] not in "aeiou":
        return f"{lower_name[:-1]}ies"
    return f"{lower_name}s"


def validate_resource_plural(value: str) -> str:
    """Valide et normalise un pluriel de ressource explicite (routes API, permissions)."""
    normalized = value.strip().lower()
    if not _RESOURCE_PLURAL_RE.match(normalized):
        raise ValueError(
            f"resource_plural invalide : '{value}'. "
            "Doit commencer par une lettre minuscule et ne contenir que des lettres, chiffres, tirets ou underscores."
        )
    return normalized


def get_resource_plural(model_name: str, meta: Optional[Dict[str, Any]] = None) -> str:
    """Retourne meta.resource_plural (override explicite obligatoire)."""
    if not meta or not meta.get("resource_plural"):
        raise ValueError(
            f"meta.resource_plural est obligatoire pour le modèle {model_name}. "
            'Définissez explicitement le pluriel API (ex: "elitests", "cities", "analyses").'
        )
    return validate_resource_plural(meta["resource_plural"])


def to_snake_case(name: str) -> str:
    """CamelCase / PascalCase -> snake_case (OrderItem -> order_item, Elitest -> elitest)."""
    step = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step).replace("-", "_").lower()


def to_kebab_case(name: str) -> str:
    """CamelCase / PascalCase -> kebab-case (OrderItem -> order-item)."""
    return to_snake_case(name).replace("_", "-")
