"""
Journal d'audit : enregistre qui a fait quoi, sur quoi, quand et depuis quelle adresse.

Les métadonnées ne contiennent jamais de secret (mot de passe, jeton, code) : seulement des noms de rôles,
des codes de permission et des noms de champs modifiés.
"""
import hashlib
from datetime import timedelta
from typing import Any, Dict, Optional

from django.conf import settings
from django.utils import timezone
from rest_framework.throttling import BaseThrottle

from app.core.models import AuditLog


class Actions:
    """Codes des actions journalisées."""
    LOGIN_SUCCESS = 'auth.login_success'
    LOGIN_FAILED = 'auth.login_failed'
    LOGIN_LOCKED = 'auth.login_locked'
    PASSWORD_CHANGED = 'auth.password_changed'
    PASSWORD_RESET = 'auth.password_reset'
    USER_CREATED = 'user.created'
    USER_UPDATED = 'user.updated'
    USER_DELETED = 'user.deleted'
    USER_ROLE_ASSIGNED = 'user.role_assigned'
    USER_ROLE_REMOVED = 'user.role_removed'
    ROLE_CREATED = 'role.created'
    ROLE_UPDATED = 'role.updated'
    ROLE_DELETED = 'role.deleted'
    ROLE_PERMISSION_ASSIGNED = 'role.permission_assigned'
    ROLE_PERMISSION_REMOVED = 'role.permission_removed'
    ROLE_PERMISSIONS_BULK_ASSIGNED = 'role.permissions_bulk_assigned'
    ACCESS_DENIED = 'access.denied'


def account_key(email: Optional[str]) -> str:
    """Empreinte stable d'un e-mail saisi (casse et espaces ignorés) ; vide si aucun e-mail n'est fourni."""
    normalized = (email or '').strip().lower() if isinstance(email, str) else ''
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest() if normalized else ''


def client_ip(request) -> str:
    """Adresse du client, avec la même règle de proxys de confiance que la limitation de débit (NUM_PROXIES)."""
    if request is None:
        return ''
    return (BaseThrottle().get_ident(request) or '')[:45]


def record(action: str, *, actor=None, target=None, target_type: str = '', target_id='', target_label: str = '',
           subject: str = '', request=None, metadata: Optional[Dict[str, Any]] = None) -> AuditLog:
    """
    Ajoute une entrée au journal. `actor` anonyme ou absent : l'entrée n'a pas d'auteur.
    L'objet concerné se donne soit par `target` (instance enregistrée), soit par `target_type` et `target_id`
    (objet déjà supprimé).
    """
    data = dict(metadata or {})
    if target_label:
        data['label'] = target_label
    if target is not None:
        target_type, target_id = target._meta.model_name, target.pk
    return AuditLog.objects.create(
        actor=actor if getattr(actor, 'is_authenticated', False) else None,
        action=action,
        target_type=target_type,
        target_id='' if target_id is None else str(target_id),
        subject=subject,
        ip_address=client_ip(request),
        metadata=data,
    )


def purge_older_than_retention() -> int:
    """Supprime les entrées plus anciennes que AUDIT_RETENTION_DAYS ; retourne leur nombre."""
    cutoff = timezone.now() - timedelta(days=settings.AUDIT_RETENTION_DAYS)
    deleted, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
    return deleted
