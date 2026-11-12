"""Normalisation des payloads multipart pour l'écriture ORM."""
from __future__ import annotations

from typing import Any, Dict, Mapping


def flatten_request_data(data: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Convertit un QueryDict (multipart) en dict de scalaires.

    Django peut renvoyer des listes (ex: prix=['12.50']) lors du **kwargs
    vers le modèle, ce qui provoque une ValidationError sur DecimalField.
    """
    flat: Dict[str, Any] = {}
    getlist = getattr(data, "getlist", None)

    for key in data.keys():
        if getlist is not None:
            values = getlist(key)
            value = values[0] if values else None
        elif hasattr(data, "get"):
            value = data.get(key)
        else:
            value = data[key]

        if isinstance(value, list):
            value = value[0] if value else None

        flat[key] = value

    return flat
