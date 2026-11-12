"""Utilitaires partagés pour la génération de champs Django."""
from __future__ import annotations

import json
import re
from typing import Any, Iterable, List, Tuple

ChoiceTuple = Tuple[Any, str]

_UPLOAD_FOLDER_RE = re.compile(r"^[a-z][a-z0-9_-]*(/[a-z][a-z0-9_-]*)*$")
_CHOICES_FIELD_TYPES = frozenset(
    {"CharField", "IntegerField", "BigIntegerField", "PositiveIntegerField"}
)


def validate_upload_folder(folder: str) -> str:
    normalized = folder.strip().strip("/")
    if not normalized or not _UPLOAD_FOLDER_RE.match(normalized):
        raise ValueError(
            f"upload_folder invalide : '{folder}'. "
            "Utilisez des segments en minuscules (ex: elitest_documents ou elitests/avatar)."
        )
    return normalized


MAX_UPLOAD_SIZE_MB = 25  # plafond absolu ; doit rester égal à settings.UPLOAD_MAX_SIZE_MB et à app/metier/utils/file_field_utils.py


def normalize_allowed_extensions(values: Iterable[str] | None) -> List[str]:
    if not values:
        return []
    normalized: List[str] = []
    for value in values:
        ext = value.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized.append(ext)
    return normalized


def normalize_choices(raw_choices: Any) -> List[ChoiceTuple]:
    """Normalise les choix JSON vers le format Django [(value, label), ...]."""
    if raw_choices is None:
        return []

    if isinstance(raw_choices, dict):
        return [(key, str(label)) for key, label in raw_choices.items()]

    if not isinstance(raw_choices, (list, tuple)):
        raise ValueError("choices doit être une liste, un tuple ou un objet")

    normalized: List[ChoiceTuple] = []
    for item in raw_choices:
        if isinstance(item, (list, tuple)):
            if len(item) < 1:
                raise ValueError("chaque choix doit contenir au moins une valeur")
            value = item[0]
            label = str(item[1]) if len(item) > 1 else str(item[0])
            normalized.append((value, label))
        elif isinstance(item, dict):
            if "value" not in item:
                raise ValueError("chaque choix objet doit contenir une clé 'value'")
            value = item["value"]
            label = str(item.get("label", item.get("display", value)))
            normalized.append((value, label))
        else:
            normalized.append((item, str(item)))

    return normalized


def validate_choices_field(field_name: str, field_type: str, choices: List[ChoiceTuple]) -> None:
    """Valide qu'un champ avec choices est correctement configuré."""
    if not choices:
        raise ValueError(f"choices vide pour le champ {field_name}")

    if field_type not in _CHOICES_FIELD_TYPES:
        raise ValueError(
            f"choices non supporté pour le type {field_type} sur le champ {field_name}. "
            f"Types autorisés : {', '.join(sorted(_CHOICES_FIELD_TYPES))}"
        )

    integer_types = {"IntegerField", "BigIntegerField", "PositiveIntegerField"}
    if field_type in integer_types:
        for value, _ in choices:
            if not isinstance(value, int):
                raise ValueError(
                    f"choices du champ {field_name} : la valeur {value!r} doit être un entier"
                )


def format_django_field_param(param_name: str, param_value: Any) -> str:
    """Formate un paramètre de champ Django en code Python valide."""
    if param_name == "default" and param_value == "uuid.uuid4":
        return "default=uuid.uuid4"
    if param_name == "choices":
        return f"choices={repr(normalize_choices(param_value))}"
    # repr() échappe correctement guillemets, apostrophes et antislashs
    return f"{param_name}={param_value!r}"


def choices_to_frontend_options(choices: List[ChoiceTuple]) -> List[dict]:
    """Convertit les choix Django en options pour le frontend."""
    return [{"value": value, "label": label} for value, label in choices]


def choices_values_json(choices: List[ChoiceTuple]) -> str:
    """Sérialise les valeurs de choix pour z.enum / literals TypeScript."""
    return json.dumps([choice[0] for choice in choices], ensure_ascii=False)


def choices_labels_json(choices: List[ChoiceTuple]) -> str:
    """Sérialise le mapping value -> label pour l'affichage frontend."""
    return json.dumps({str(value): label for value, label in choices}, ensure_ascii=False)


def format_ts_default_value(choices: List[ChoiceTuple], django_type: str) -> str:
    """Valeur par défaut TypeScript pour un champ à choix."""
    if not choices:
        return "undefined"
    value = choices[0][0]
    if django_type in {"IntegerField", "BigIntegerField", "PositiveIntegerField"}:
        return str(value)
    return json.dumps(str(value))
