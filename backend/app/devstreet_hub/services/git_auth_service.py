"""Autorisation navigateur DevStreet → PAT Gitea pour le CLI local."""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError, Throttled

from app.devstreet_hub.conf import config
from app.devstreet_hub.models import (
    ForgeIdentity,
    GitConnectedComputer,
    GitDeviceAuthRequest,
)
from app.devstreet_hub.repositories.workflow_repository import WorkflowRepository
from app.devstreet_hub.services.errors import Conflict, ExternalUnavailable
from app.devstreet_hub.services.gitea_client import GiteaClient

REQUEST_TTL = timedelta(minutes=10)
POLL_MIN_INTERVAL = timedelta(seconds=2)
MAX_POLLS = 90
GRANT_SALT = "devstreet-git-auth-grant-v1"
_NAME_RE = re.compile(r"^[\w .@+\-]{2,120}$", re.UNICODE)

# Scopes Gitea réellement demandés pour le PAT (pas de JWT Django).
REQUESTED_SCOPES = (
    "write:repository",
    "read:repository",
    "read:user",
)
REQUESTED_SCOPE_LABELS = (
    "Lire et pousser sur les dépôts auxquels vous avez déjà accès",
    "Lire votre profil forge lié",
)


def _sha256_b64url(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    import base64

    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


class GitAuthService:
    def __init__(self, repository=None, forge=None):
        self.repo = repository or WorkflowRepository()
        self._forge = forge

    @property
    def forge(self):
        return self._forge or GiteaClient()

    def _gitea_public_host(self) -> str:
        url = config("GITEA_PUBLIC_URL", config("GITEA_URL")).rstrip("/")
        if not url:
            raise ExternalUnavailable("Gitea doit être configuré côté serveur.")
        return url

    def _validate_hub_base_url(self, hub_base_url: str) -> str:
        raw = (hub_base_url or "").strip().rstrip("/")
        if not raw:
            raise ValidationError({"hub_base_url": "URL DevStreet requise."})
        parsed = urlsplit(raw)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValidationError({"hub_base_url": "URL DevStreet invalide."})
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValidationError({"hub_base_url": "URL DevStreet invalide."})
        allowed = {o.rstrip("/").lower() for o in settings.CORS_ALLOWED_ORIGINS}
        allowed.add(settings.FRONTEND_URL.rstrip("/").lower())
        if raw.lower() not in allowed:
            raise ValidationError(
                {
                    "hub_base_url": (
                        "Instance DevStreet non reconnue. "
                        "Utilisez l'URL publique de cette installation."
                    )
                }
            )
        return raw

    def _validate_computer_name(self, name: str) -> str:
        value = (name or "").strip()
        if not _NAME_RE.fullmatch(value):
            raise ValidationError(
                {"computer_name": "Nom d'ordinateur invalide (2–120 caractères)."}
            )
        return value

    def start_device_auth(
        self, *, computer_name: str, hub_base_url: str, code_challenge: str
    ) -> dict:
        hub = self._validate_hub_base_url(hub_base_url)
        name = self._validate_computer_name(computer_name)
        challenge = (code_challenge or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_\-]{43,128}", challenge):
            raise ValidationError({"code_challenge": "Challenge PKCE invalide."})
        now = timezone.now()
        request = GitDeviceAuthRequest.objects.create(
            computer_name=name,
            hub_base_url=hub,
            code_challenge=challenge,
            expires_at=now + REQUEST_TTL,
        )
        authorize_url = (
            f"{hub}/hub/git-auth/authorize?request={request.id}"
        )
        return {
            "request_id": str(request.id),
            "authorize_url": authorize_url,
            "expires_at": request.expires_at.isoformat(),
            "interval_seconds": int(POLL_MIN_INTERVAL.total_seconds()),
        }

    def get_request_public(self, request_id) -> dict:
        try:
            item = GitDeviceAuthRequest.objects.get(pk=request_id)
        except (GitDeviceAuthRequest.DoesNotExist, ValueError, TypeError):
            raise NotFound("Demande introuvable.")
        self._expire_if_needed(item)
        try:
            gitea_host = urlsplit(self._gitea_public_host()).netloc
        except ExternalUnavailable:
            gitea_host = ""
        return {
            "id": str(item.id),
            "computer_name": item.computer_name,
            "hub_base_url": item.hub_base_url,
            "status": item.status,
            "expires_at": item.expires_at.isoformat(),
            "created_at": item.created_at.isoformat(),
            "decided_at": item.decided_at.isoformat() if item.decided_at else None,
            "scopes": list(REQUESTED_SCOPES),
            "scope_labels": list(REQUESTED_SCOPE_LABELS),
            "gitea_host": gitea_host,
        }

    def _expire_if_needed(self, item: GitDeviceAuthRequest) -> None:
        if (
            item.status == GitDeviceAuthRequest.STATUS_PENDING
            and item.expires_at <= timezone.now()
        ):
            item.status = GitDeviceAuthRequest.STATUS_EXPIRED
            item.decided_at = timezone.now()
            item.save(update_fields=["status", "decided_at"])

    def authorize(self, actor, request_id) -> dict:
        """Confirmation explicite navigateur — jamais automatique."""
        with transaction.atomic():
            try:
                item = GitDeviceAuthRequest.objects.select_for_update().get(
                    pk=request_id
                )
            except (GitDeviceAuthRequest.DoesNotExist, ValueError, TypeError):
                raise NotFound("Demande introuvable.")
            self._expire_if_needed(item)
            if item.status != GitDeviceAuthRequest.STATUS_PENDING:
                raise Conflict("Cette demande n'est plus en attente d'autorisation.")
            identity = self.repo.identity(actor)
            if (
                not identity
                or identity.status != ForgeIdentity.STATUS_LINKED
                or not identity.login
                or not identity.gitea_user_id
            ):
                raise Conflict(
                    "Compte Git non lié. Terminez d'abord la préparation du dépôt "
                    "dans DevStreet."
                )
            # Nom unique côté Gitea (évite 409 si reconnexion du même libellé).
            token_name = (
                f"ds-{item.computer_name[:48]}-{uuid.uuid4().hex[:8]}"
            )[:200]
            forge_token = self.forge.create_user_access_token(
                login=identity.login,
                email=actor.email,
                name=token_name,
                scopes=list(REQUESTED_SCOPES),
            )
            sha1 = str(forge_token.get("sha1") or "")
            if not sha1 or "id" not in forge_token:
                raise ExternalUnavailable(
                    "La forge n'a pas renvoyé de jeton d'accès utilisable."
                )
            computer = GitConnectedComputer.objects.create(
                user=actor,
                name=item.computer_name,
                forge_login=identity.login,
                gitea_token_id=int(forge_token["id"]),
                token_last_eight=str(
                    forge_token.get("token_last_eight") or sha1
                )[-8:],
                status=GitConnectedComputer.STATUS_ACTIVE,
            )
            grant = signing.dumps(
                {
                    "token": sha1,
                    "login": identity.login,
                    "gitea_url": self._gitea_public_host(),
                    "computer_id": computer.pk,
                    "request_id": str(item.id),
                },
                salt=GRANT_SALT,
                compress=True,
            )
            item.user = actor
            item.status = GitDeviceAuthRequest.STATUS_AUTHORIZED
            item.grant_payload = grant
            item.connected_computer = computer
            item.decided_at = timezone.now()
            item.save(
                update_fields=[
                    "user",
                    "status",
                    "grant_payload",
                    "connected_computer",
                    "decided_at",
                ]
            )
        return {
            "status": item.status,
            "computer_name": item.computer_name,
            "decided_at": item.decided_at.isoformat() if item.decided_at else None,
        }

    def deny(self, actor, request_id) -> dict:
        with transaction.atomic():
            try:
                item = GitDeviceAuthRequest.objects.select_for_update().get(
                    pk=request_id
                )
            except (GitDeviceAuthRequest.DoesNotExist, ValueError, TypeError):
                raise NotFound("Demande introuvable.")
            self._expire_if_needed(item)
            if item.status != GitDeviceAuthRequest.STATUS_PENDING:
                raise Conflict("Cette demande n'est plus en attente.")
            item.user = actor
            item.status = GitDeviceAuthRequest.STATUS_DENIED
            item.decided_at = timezone.now()
            item.save(update_fields=["user", "status", "decided_at"])
        return {"status": item.status}

    def poll(self, *, request_id, code_verifier: str) -> dict:
        verifier = (code_verifier or "").strip()
        if len(verifier) < 43 or len(verifier) > 128:
            raise ValidationError({"code_verifier": "Vérificateur invalide."})
        with transaction.atomic():
            try:
                item = GitDeviceAuthRequest.objects.select_for_update().get(
                    pk=request_id
                )
            except (GitDeviceAuthRequest.DoesNotExist, ValueError, TypeError):
                raise NotFound("Demande introuvable.")
            self._expire_if_needed(item)
            now = timezone.now()
            if item.last_poll_at and now - item.last_poll_at < POLL_MIN_INTERVAL:
                raise Throttled(wait=POLL_MIN_INTERVAL.total_seconds())
            if item.poll_count >= MAX_POLLS:
                fields = ["poll_count", "last_poll_at"]
                item.poll_count += 1
                item.last_poll_at = now
                if item.status == GitDeviceAuthRequest.STATUS_PENDING:
                    item.status = GitDeviceAuthRequest.STATUS_EXPIRED
                    item.decided_at = now
                    fields.extend(["status", "decided_at"])
                item.save(update_fields=fields)
                raise Conflict("Trop de tentatives de vérification.")
            item.poll_count += 1
            item.last_poll_at = now
            item.save(update_fields=["poll_count", "last_poll_at"])

            if _sha256_b64url(verifier) != item.code_challenge:
                raise PermissionDenied("Vérificateur incorrect.")

            if item.status == GitDeviceAuthRequest.STATUS_PENDING:
                return {
                    "status": "pending",
                    "expires_at": item.expires_at.isoformat(),
                }
            if item.status == GitDeviceAuthRequest.STATUS_DENIED:
                return {"status": "denied"}
            if item.status in (
                GitDeviceAuthRequest.STATUS_EXPIRED,
                GitDeviceAuthRequest.STATUS_CONSUMED,
            ):
                return {"status": item.status}
            if item.status != GitDeviceAuthRequest.STATUS_AUTHORIZED:
                return {"status": item.status}

            try:
                payload = signing.loads(
                    item.grant_payload,
                    salt=GRANT_SALT,
                    max_age=int(REQUEST_TTL.total_seconds()) + 60,
                )
            except signing.BadSignature as error:
                raise Conflict("Autorisation invalide ou déjà consommée.") from error
            if payload.get("request_id") != str(item.id):
                raise Conflict("Autorisation incohérente.")

            item.status = GitDeviceAuthRequest.STATUS_CONSUMED
            item.grant_payload = ""
            item.save(update_fields=["status", "grant_payload"])

            return {
                "status": "authorized",
                "login": payload["login"],
                "token": payload["token"],
                "gitea_url": payload["gitea_url"],
                "computer_id": payload["computer_id"],
                "computer_name": item.computer_name,
            }

    def list_computers(self, actor):
        return (
            GitConnectedComputer.objects.filter(user=actor)
            .order_by("-created_at")
        )

    def revoke_computer(self, actor, computer_id: int) -> None:
        with transaction.atomic():
            try:
                computer = GitConnectedComputer.objects.select_for_update().get(
                    pk=computer_id, user=actor
                )
            except GitConnectedComputer.DoesNotExist:
                raise NotFound("Ordinateur introuvable.")
            if computer.status == GitConnectedComputer.STATUS_REVOKED:
                return
            identity = self.repo.identity(actor)
            if (
                identity
                and identity.status == ForgeIdentity.STATUS_LINKED
                and identity.login == computer.forge_login
            ):
                try:
                    self.forge.delete_user_access_token(
                        login=identity.login,
                        email=actor.email,
                        token_id=computer.gitea_token_id,
                    )
                except ExternalUnavailable:
                    # On marque révoqué localement ; la forge peut être indisponible.
                    pass
            computer.status = GitConnectedComputer.STATUS_REVOKED
            computer.revoked_at = timezone.now()
            computer.save(update_fields=["status", "revoked_at"])
