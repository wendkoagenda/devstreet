"""Utilitaires pour les champs fichier (chemin relatif + StorageService)."""
from __future__ import annotations

import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from django.core.exceptions import ValidationError

_UPLOAD_FOLDER_RE = re.compile(r"^[a-z][a-z0-9_-]*(/[a-z][a-z0-9_-]*)*$")
_DEFAULT_MAX_SIZE_MB = 10
MAX_UPLOAD_SIZE_MB = 25  # plafond absolu ; doit rester égal à settings.UPLOAD_MAX_SIZE_MB et à scripts/generator/field_utils.py
_FILE_PATH_MAX_LENGTH = 512


def validate_upload_folder(folder: str) -> str:
    normalized = folder.strip().strip("/")
    if not normalized or not _UPLOAD_FOLDER_RE.match(normalized):
        raise ValueError(
            f"upload_folder invalide : '{folder}'. "
            "Utilisez des segments en minuscules séparés par des slashes (ex: elitest_documents)."
        )
    return normalized


def normalize_allowed_extensions(values: Optional[Iterable[str]]) -> List[str]:
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


def get_file_field_names(field_types: Dict[str, str]) -> List[str]:
    return [name for name, field_type in field_types.items() if field_type == "FileField"]


def _validate_upload(file_obj, allowed_extensions: List[str], max_size_mb: int) -> None:
    # Aucune extension configurée = aucun fichier accepté (jamais « tout accepter »)
    if not allowed_extensions:
        raise ValidationError("Aucune extension de fichier n'est autorisée pour ce champ")
    _, ext = os.path.splitext(file_obj.name or "")
    if ext.lower() not in allowed_extensions:
        raise ValidationError(
            f"Extension non autorisée : {ext or '(aucune)'}. "
            f"Extensions acceptées : {', '.join(allowed_extensions)}"
        )

    max_bytes = min(max_size_mb, MAX_UPLOAD_SIZE_MB) * 1024 * 1024
    if getattr(file_obj, "size", 0) > max_bytes:
        raise ValidationError(f"Fichier trop volumineux (max {max_size_mb} Mo)")


def process_uploaded_files(
    request,
    file_field_config: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    """
    Traite les fichiers uploadés d'une requête multipart.

    file_field_config example:
        {
            "document": {
                "upload_folder": "elitest_documents",
                "allowed_extensions": [".pdf"],
                "max_size_mb": 5,
            }
        }
    """
    from app.metier.services.storage_service import get_storage_service

    if not file_field_config:
        return {}

    storage = get_storage_service()
    resolved: Dict[str, str] = {}

    for field_name, config in file_field_config.items():
        uploaded = request.FILES.get(field_name)
        if not uploaded:
            continue

        relative_path = request.data.get(f"{field_name}_path")
        if not relative_path:
            raise ValidationError(
                f"Chemin manquant pour le champ {field_name} ({field_name}_path requis)"
            )

        relative_path = str(relative_path).strip().lstrip("/")
        allowed_extensions = config.get("allowed_extensions") or []
        max_size_mb = int(config.get("max_size_mb") or _DEFAULT_MAX_SIZE_MB)

        _validate_upload(uploaded, allowed_extensions, max_size_mb)

        expected_prefix = f"{config['upload_folder'].strip('/')}/"
        if not relative_path.startswith(expected_prefix):
            raise ValidationError(
                f"Chemin invalide pour {field_name} : doit commencer par {expected_prefix}"
            )

        if len(relative_path) > _FILE_PATH_MAX_LENGTH:
            raise ValidationError(f"Chemin trop long pour {field_name}")

        saved_path = storage.save(relative_path, uploaded)
        resolved[field_name] = saved_path

    return resolved


def delete_storage_files(paths: Iterable[Optional[str]]) -> None:
    from app.metier.services.storage_service import get_storage_service

    storage = get_storage_service()
    for path in paths:
        if path:
            storage.delete(path)


def delete_replaced_files(
    instance,
    new_data: Dict[str, Any],
    file_field_names: Iterable[str],
) -> None:
    paths_to_delete: List[str] = []
    for field_name in file_field_names:
        if field_name not in new_data:
            continue
        old_path = getattr(instance, field_name, None)
        new_path = new_data.get(field_name)
        if old_path and new_path and old_path != new_path:
            paths_to_delete.append(old_path)
    delete_storage_files(paths_to_delete)


def delete_instance_files(instance, file_field_names: Iterable[str]) -> None:
    paths = [getattr(instance, field_name, None) for field_name in file_field_names]
    delete_storage_files(paths)


def build_file_field_config(fields_meta: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Construit la config runtime à partir des métadonnées injectées dans le viewset."""
    return {
        name: {
            "upload_folder": meta["upload_folder"],
            "allowed_extensions": meta.get("allowed_extensions") or [],
            "max_size_mb": meta.get("max_size_mb") or _DEFAULT_MAX_SIZE_MB,
        }
        for name, meta in fields_meta.items()
    }
