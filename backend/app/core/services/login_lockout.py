"""
Verrouillage de la connexion par compte.

La limite par adresse IP (LoginThrottle) n'arrête pas une attaque répartie sur plusieurs adresses visant le même
e-mail. Ici, les échecs sont comptés par e-mail saisi, d'après le journal d'audit (partagé entre les processus,
contrairement à un cache en mémoire). Un e-mail inconnu est verrouillé comme un e-mail connu : la réponse ne révèle
pas quels comptes existent.
"""
from datetime import timedelta

from django.conf import settings
from django.db.models import Max
from django.utils import timezone

from app.core.models import AuditLog
from app.core.services.audit_service import Actions


def is_locked(key: str) -> bool:
    """Vrai si `key` (voir audit_service.account_key) a atteint le maximum d'échecs dans la fenêtre, sans connexion réussie depuis."""
    if not key:
        return False
    window_start = timezone.now() - timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
    last_success = AuditLog.objects.filter(
        action=Actions.LOGIN_SUCCESS, subject=key, created_at__gte=window_start
    ).aggregate(latest=Max('created_at'))['latest']
    failures = AuditLog.objects.filter(action=Actions.LOGIN_FAILED, subject=key,
                                       created_at__gte=last_success or window_start)
    return failures.count() >= settings.LOGIN_LOCKOUT_MAX_FAILURES
