"""OAuth2 public (PKCE) pour Git Credential Manager → PAT Gitea via DevStreet."""

from __future__ import annotations

import secrets
import uuid
from datetime import timedelta
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from app.devstreet_hub.conf import config
from app.devstreet_hub.models import (
    ForgeIdentity,
    GitConnectedComputer,
    GitOAuthAuthorization,
)
from app.devstreet_hub.repositories.workflow_repository import WorkflowRepository
from app.devstreet_hub.services.errors import Conflict, ExternalUnavailable
from app.devstreet_hub.services.gitea_client import GiteaClient
from app.devstreet_hub.services.git_auth_service import (
    REQUESTED_SCOPE_LABELS,
    REQUESTED_SCOPES,
    _sha256_b64url,
)

# Client public documenté (pas un secret administrateur).
GCM_CLIENT_ID = "devstreet-gcm"
REQUEST_TTL = timedelta(minutes=10)
CODE_TTL = timedelta(minutes=5)


class GitOAuthService:
    def __init__(self, repository=None, forge=None):
        self.repo = repository or WorkflowRepository()
        self._forge = forge

    @property
    def forge(self):
        return self._forge or GiteaClient()

    def _configured_gitea_url(self) -> str:
        """URL publique de Gitea telle que configurée (chaîne vide si absente)."""
        return config("GITEA_PUBLIC_URL", config("GITEA_URL")).rstrip("/")

    def _gitea_public_origin(self) -> str:
        url = self._configured_gitea_url()
        if not url:
            raise ExternalUnavailable("Gitea doit être configuré côté serveur.")
        return url

    def _hub_api_base(self) -> str:
        """Base API v1 absolue (FRONTEND_URL proxy ou origine API)."""
        front = settings.FRONTEND_URL.rstrip("/")
        return f"{front}/api/v1"

    def client_config(self) -> dict:
        gitea = self._gitea_public_origin()
        api = self._hub_api_base()
        origin_key = gitea  # credential.<exact-origin>
        commands = [
            f'git config --global credential.{origin_key}.provider generic',
            f'git config --global credential.{origin_key}.oauthClientId {GCM_CLIENT_ID}',
            (
                f'git config --global credential.{origin_key}.oauthAuthorizeEndpoint '
                f'{api}/git-oauth/authorize'
            ),
            (
                f'git config --global credential.{origin_key}.oauthTokenEndpoint '
                f'{api}/git-oauth/token'
            ),
            f'git config --global credential.{origin_key}.oauthRedirectUri http://127.0.0.1',
            f'git config --global credential.{origin_key}.oauthUseClientAuthHeader false',
            f'git config --global credential.{origin_key}.oauthDefaultUserName git',
            f'git config --global credential.{origin_key}.oauthScopes git',
        ]
        return {
            "client_id": GCM_CLIENT_ID,
            "gitea_origin": gitea,
            "authorize_endpoint": f"{api}/git-oauth/authorize",
            "token_endpoint": f"{api}/git-oauth/token",
            "redirect_uri": "http://127.0.0.1",
            "oauth_default_username": "git",
            "scopes": "git",
            "git_config_commands": commands,
        }

    def _validate_redirect_uri(self, redirect_uri: str) -> str:
        raw = (redirect_uri or "").strip()
        parsed = urlsplit(raw)
        if parsed.scheme != "http":
            raise ValidationError({"redirect_uri": "Seuls http://127.0.0.1 ou localhost sont acceptés."})
        if parsed.hostname not in ("127.0.0.1", "localhost"):
            raise ValidationError({"redirect_uri": "Redirect loopback GCM requis."})
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValidationError({"redirect_uri": "Redirect URI invalide."})
        return raw

    def start_authorize(self, params: dict) -> dict:
        """Valide la requête GCM et renvoie l'URL frontend de confirmation."""
        response_type = (params.get("response_type") or "").strip()
        if response_type != "code":
            raise ValidationError({"response_type": "Seul response_type=code est supporté."})
        client_id = (params.get("client_id") or "").strip()
        if client_id != GCM_CLIENT_ID:
            raise ValidationError({"client_id": "Client OAuth inconnu."})
        redirect_uri = self._validate_redirect_uri(params.get("redirect_uri") or "")
        challenge = (params.get("code_challenge") or "").strip()
        method = (params.get("code_challenge_method") or "S256").strip()
        if method != "S256":
            raise ValidationError({"code_challenge_method": "Seul S256 est supporté."})
        if not challenge or len(challenge) < 43 or len(challenge) > 128:
            raise ValidationError({"code_challenge": "Challenge PKCE invalide."})
        state = (params.get("state") or "")[:200]
        scope = (params.get("scope") or "git")[:200]
        now = timezone.now()
        item = GitOAuthAuthorization.objects.create(
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=challenge,
            code_challenge_method=method,
            scope=scope,
            expires_at=now + REQUEST_TTL,
        )
        front = settings.FRONTEND_URL.rstrip("/")
        return {
            "request_id": str(item.id),
            "confirm_url": f"{front}/hub/git-oauth/authorize?request={item.id}",
        }

    def get_public(self, request_id) -> dict:
        item = self._get(request_id)
        self._expire_if_needed(item)
        # Information d'affichage : un Gitea non configuré donne un hôte vide, sans erreur.
        gitea_host = urlsplit(self._configured_gitea_url()).netloc
        return {
            "id": str(item.id),
            "status": item.status,
            "computer_name": item.computer_name,
            "expires_at": item.expires_at.isoformat(),
            "created_at": item.created_at.isoformat(),
            "decided_at": item.decided_at.isoformat() if item.decided_at else None,
            "scopes": list(REQUESTED_SCOPES),
            "scope_labels": list(REQUESTED_SCOPE_LABELS),
            "gitea_host": gitea_host,
            "client_id": item.client_id,
        }

    def _get(self, request_id) -> GitOAuthAuthorization:
        try:
            return GitOAuthAuthorization.objects.get(pk=request_id)
        except (GitOAuthAuthorization.DoesNotExist, ValueError, TypeError):
            raise NotFound("Demande OAuth introuvable.")

    def _expire_if_needed(self, item: GitOAuthAuthorization) -> None:
        now = timezone.now()
        if item.status == GitOAuthAuthorization.STATUS_PENDING and item.expires_at <= now:
            item.status = GitOAuthAuthorization.STATUS_EXPIRED
            item.decided_at = now
            item.save(update_fields=["status", "decided_at"])
        if (
            item.status == GitOAuthAuthorization.STATUS_AUTHORIZED
            and item.code_expires_at
            and item.code_expires_at <= now
        ):
            item.status = GitOAuthAuthorization.STATUS_EXPIRED
            item.authorization_code = ""
            item.save(update_fields=["status", "authorization_code"])

    def approve(self, actor, request_id) -> dict:
        """Confirmation explicite : émet un code d'autorisation (PAT à l'échange token)."""
        with transaction.atomic():
            try:
                item = GitOAuthAuthorization.objects.select_for_update().get(
                    pk=request_id
                )
            except (GitOAuthAuthorization.DoesNotExist, ValueError, TypeError):
                raise NotFound("Demande OAuth introuvable.")
            self._expire_if_needed(item)
            if item.status != GitOAuthAuthorization.STATUS_PENDING:
                raise Conflict("Cette demande n'est plus en attente.")
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
            code = secrets.token_urlsafe(32)
            now = timezone.now()
            item.user = actor
            item.status = GitOAuthAuthorization.STATUS_AUTHORIZED
            item.authorization_code = code
            item.decided_at = now
            item.code_expires_at = now + CODE_TTL
            item.save(
                update_fields=[
                    "user",
                    "status",
                    "authorization_code",
                    "decided_at",
                    "code_expires_at",
                ]
            )
        redirect = self._append_query(
            item.redirect_uri, {"code": code, "state": item.state}
        )
        return {"status": item.status, "redirect_uri": redirect}

    def deny(self, actor, request_id) -> dict:
        with transaction.atomic():
            try:
                item = GitOAuthAuthorization.objects.select_for_update().get(
                    pk=request_id
                )
            except (GitOAuthAuthorization.DoesNotExist, ValueError, TypeError):
                raise NotFound("Demande OAuth introuvable.")
            self._expire_if_needed(item)
            if item.status != GitOAuthAuthorization.STATUS_PENDING:
                raise Conflict("Cette demande n'est plus en attente.")
            item.user = actor
            item.status = GitOAuthAuthorization.STATUS_DENIED
            item.decided_at = timezone.now()
            item.save(update_fields=["user", "status", "decided_at"])
        error_redirect = self._append_query(
            item.redirect_uri,
            {
                "error": "access_denied",
                "state": item.state,
            },
        )
        return {"status": item.status, "redirect_uri": error_redirect}

    def exchange_token(self, data: dict) -> dict:
        """Échange code + PKCE → PAT Gitea (access_token). Jamais de JWT Django."""
        grant = (data.get("grant_type") or "").strip()
        if grant != "authorization_code":
            raise ValidationError({"error": "unsupported_grant_type"})
        client_id = (data.get("client_id") or "").strip()
        if client_id != GCM_CLIENT_ID:
            raise ValidationError({"error": "invalid_client"})
        code = (data.get("code") or "").strip()
        verifier = (data.get("code_verifier") or "").strip()
        redirect_uri = (data.get("redirect_uri") or "").strip()
        if not code or not verifier:
            raise ValidationError({"error": "invalid_request"})

        with transaction.atomic():
            try:
                item = GitOAuthAuthorization.objects.select_for_update().get(
                    authorization_code=code
                )
            except GitOAuthAuthorization.DoesNotExist:
                raise PermissionDenied("invalid_grant")
            self._expire_if_needed(item)
            if item.status != GitOAuthAuthorization.STATUS_AUTHORIZED:
                raise PermissionDenied("invalid_grant")
            if item.client_id != client_id:
                raise PermissionDenied("invalid_grant")
            if item.redirect_uri != redirect_uri:
                raise PermissionDenied("invalid_grant")
            if _sha256_b64url(verifier) != item.code_challenge:
                raise PermissionDenied("invalid_grant")
            actor = item.user
            if actor is None:
                raise PermissionDenied("invalid_grant")
            identity = self.repo.identity(actor)
            if (
                not identity
                or identity.status != ForgeIdentity.STATUS_LINKED
                or not identity.login
            ):
                raise Conflict("Compte Git non lié.")

            token_name = f"ds-gcm-{uuid.uuid4().hex[:10]}"[:200]
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
            item.status = GitOAuthAuthorization.STATUS_CONSUMED
            item.authorization_code = ""
            item.connected_computer = computer
            item.save(
                update_fields=["status", "authorization_code", "connected_computer"]
            )

        return {
            "access_token": sha1,
            "token_type": "bearer",
            "scope": "git",
        }

    @staticmethod
    def _append_query(url: str, extra: dict) -> str:
        parts = urlsplit(url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        for key, value in extra.items():
            if value is None or value == "":
                continue
            query[key] = value
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
        )
