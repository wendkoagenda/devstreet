"""Adaptateur HTTP Gitea. Aucun mot de passe Django ni code utilisateur n'est exécuté."""

from __future__ import annotations

import base64
import logging
import secrets
import re
from urllib.parse import quote, urlsplit

import httpx
from django.conf import settings

from app.devstreet_hub.conf import config
from app.devstreet_hub.services.errors import Conflict, ExternalUnavailable
from app.devstreet_hub.services.forge_identity_tokens import (
    description_with_marker,
    has_correlation,
)


class GiteaClient:
    def __init__(self):
        self.url = config("GITEA_URL").rstrip("/")
        self.token = config("GITEA_TOKEN")
        parsed = urlsplit(self.url)
        if (
            not self.url
            or not self.token
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ExternalUnavailable("Gitea doit être configuré côté serveur.")
        if parsed.scheme != "https" and not (
            settings.DEBUG
            and parsed.scheme == "http"
            and parsed.hostname in ("127.0.0.1", "localhost")
        ):
            raise ExternalUnavailable("Gitea exige HTTPS hors développement local.")

    def request(self, method, path, data=None, *, missing_ok=False, raw=False):
        try:
            with httpx.Client(
                timeout=15, follow_redirects=False, trust_env=False
            ) as client:
                response = client.request(
                    method,
                    self.url + "/api/v1" + path,
                    headers={"Authorization": "token " + self.token},
                    json=data,
                )
            if missing_ok and response.status_code == 404:
                return None
            if response.status_code == 409:
                raise Conflict(
                    "Conflit côté forge : ressource déjà présente sans preuve locale."
                )
            response.raise_for_status()
            if raw or not response.content:
                return response
            return response.json()
        except Conflict:
            raise
        except (httpx.HTTPError, ValueError) as error:
            raise ExternalUnavailable(
                "La forge ne répond pas correctement ; réessayez."
            ) from error

    def get_user_by_login(self, login: str) -> dict | None:
        return self.request("GET", "/users/" + quote(login, safe=""), missing_ok=True)

    def get_user_by_id(self, gitea_user_id: int) -> dict | None:
        """Résout un utilisateur par ID numérique (preuve plus fiable que le login)."""
        payload = self.request(
            "GET",
            f"/users/search?uid={int(gitea_user_id)}",
            missing_ok=True,
        )
        if not payload:
            return None
        data = payload.get("data") if isinstance(payload, dict) else payload
        if not isinstance(data, list):
            return None
        for item in data:
            if isinstance(item, dict) and item.get("id") == int(gitea_user_id):
                return item
        return None

    def apply_correlation(self, login: str, provisioning_key, *, email: str) -> dict:
        """Écrit la preuve de corrélation dans description (champ admin, pas d'idempotence API)."""
        return self.request(
            "PATCH",
            "/admin/users/" + quote(login, safe=""),
            {
                "source_id": 0,
                "login_name": login,
                "email": email,
                "description": description_with_marker(provisioning_key),
            },
        )

    def create_user(
        self,
        *,
        login: str,
        email: str,
        provisioning_key,
        password: str | None = None,
    ) -> tuple[dict, str]:
        """Crée un compte Git puis pose la preuve de corrélation.

        N'adopte jamais un compte préexistant : si le login est pris sans notre
        marqueur, Conflict. Le mot de passe Django n'est jamais réutilisé.
        """
        existing = self.get_user_by_login(login)
        if existing:
            if has_correlation(existing, provisioning_key):
                # Compte déjà créé lors d'une tentative précédente ; pas de secret.
                return existing, ""
            raise Conflict(
                "Compte Git déjà présent sans preuve de propriété DevStreet Hub : "
                "rapprochement administratif requis."
            )

        password = password or secrets.token_urlsafe(32)
        try:
            user = self.request(
                "POST",
                "/admin/users",
                {
                    "username": login,
                    "email": email,
                    "password": password,
                    "full_name": "DevStreet Hub",
                    "must_change_password": True,
                    "send_notify": False,
                    "visibility": "limited",
                },
            )
        except Conflict:
            # Course : un tiers a pris le login entre le GET et le POST.
            raise Conflict(
                "Compte Git déjà présent sans preuve de propriété DevStreet Hub : "
                "rapprochement administratif requis."
            ) from None
        except ExternalUnavailable:
            # Timeout ambigu : l'appelant doit reprendre avec la même clé/login.
            raise

        try:
            user = self.apply_correlation(login, provisioning_key, email=email) or user
        except ExternalUnavailable:
            # Compte créé mais marqueur absent : la reprise pourra échouer
            # explicitement plutôt que d'adopter un tiers.
            logging.getLogger(__name__).warning(
                "Marqueur de corrélation forge non appliqué pour login réservé"
            )
            raise
        if not has_correlation(user, provisioning_key):
            # Certains Gitea renvoient le user sans relire description : relecture.
            refreshed = self.get_user_by_login(login) or user
            if not has_correlation(refreshed, provisioning_key):
                raise Conflict(
                    "Compte Git créé sans preuve de corrélation vérifiable : "
                    "réparation administrative requise."
                )
            user = refreshed
        return user, password

    def reissue_password(self, *, login: str, email: str) -> str:
        """Réémet un secret initial après reprise contrôlée (preuve déjà vérifiée)."""
        password = secrets.token_urlsafe(32)
        self.request(
            "PATCH",
            "/admin/users/" + quote(login, safe=""),
            {
                "source_id": 0,
                "login_name": login,
                "email": email,
                "password": password,
                "must_change_password": True,
            },
        )
        return password

    def provision_identity(self, actor, *, login: str, provisioning_key):
        """Compatibilité de signature pour les mocks de tests existants."""
        return self.create_user(
            login=login,
            email=actor.email,
            provisioning_key=provisioning_key,
        )

    def repo_path(self, repository):
        return (
            "/repos/"
            + quote(repository.namespace, safe="")
            + "/"
            + quote(repository.name, safe="")
        )

    def provision_repository(self, repository, identity):
        path = (
            "/repos/"
            + quote(identity.login, safe="")
            + "/"
            + quote(repository.name, safe="")
        )
        result = self.request("GET", path, missing_ok=True)
        if result is None:
            result = self.request(
                "POST",
                "/admin/users/" + quote(identity.login, safe="") + "/repos",
                {
                    "name": repository.name,
                    "private": True,
                    "auto_init": False,
                    "default_branch": "main",
                },
            )
        if not result.get("private"):
            result = self.request("PATCH", path, {"private": True})
        if (
            not result.get("private")
            or result.get("owner", {}).get("id") != identity.gitea_user_id
        ):
            raise ExternalUnavailable(
                "Le dépôt ne possède pas la visibilité ou le propriétaire attendu."
            )
        return result

    def set_public(self, repository, public):
        result = self.request(
            "PATCH", self.repo_path(repository), {"private": not public}
        )
        if result.get("private") != (not public):
            raise ExternalUnavailable("La visibilité Git n’a pas été confirmée.")

    def repo_is_empty(self, repository) -> bool:
        """True si la branche par défaut n'existe pas encore (dépôt sans commit)."""
        branch = self.request(
            "GET",
            self.repo_path(repository)
            + "/branches/"
            + quote(repository.default_branch or "main", safe=""),
            missing_ok=True,
        )
        return branch is None

    def create_file(self, repository, *, path: str, content: str, message: str, branch: str):
        """Crée un fichier via l'API contents Gitea (contenu base64)."""
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        return self.request(
            "POST",
            self.repo_path(repository) + "/contents/" + quote(path, safe="/"),
            {
                "content": encoded,
                "message": message,
                "branch": branch,
            },
        )

    def initialize_scaffold(self, repository, files: list[tuple[str, str]]):
        """Écrit les fichiers d'init un par un ; le premier commit crée la branche."""
        branch = repository.default_branch or "main"
        if not self.repo_is_empty(repository):
            raise Conflict("Le dépôt contient déjà des commits.")
        last_sha = ""
        for path, content in files:
            result = self.create_file(
                repository,
                path=path,
                content=content,
                message=f"chore: add {path}",
                branch=branch,
            )
            commit = (result or {}).get("commit") or {}
            sha = commit.get("sha") or ""
            if isinstance(sha, str) and sha:
                last_sha = sha
        if not last_sha:
            # Relecture si la forge omet le SHA dans la dernière réponse.
            last_sha = self.head(repository)
        return {"sha": last_sha, "branch": branch}

    def head(self, repository):
        branch = self.request(
            "GET",
            self.repo_path(repository)
            + "/branches/"
            + quote(repository.default_branch, safe=""),
            missing_ok=True,
        )
        if not branch:
            raise Conflict(
                "Le dépôt est vide ou sa branche principale est absente : créez une tâche manuellement."
            )
        sha = branch.get("commit", {}).get("id", "")
        if not isinstance(sha, str) or not re.fullmatch(
            r"(?:[a-fA-F0-9]{40}|[a-fA-F0-9]{64})", sha
        ):
            raise ExternalUnavailable(
                "La forge n’a pas confirmé une version de code valide."
            )
        return sha

    def pull_request(self, repository, number):
        return self.request("GET", self.repo_path(repository) + f"/pulls/{number}")

    def collect_sources(self, repository, sha):
        tree = self.request(
            "GET",
            self.repo_path(repository)
            + "/git/trees/"
            + quote(sha, safe="")
            + "?recursive=true",
        )
        if tree.get("truncated"):
            raise Conflict("Arborescence trop grande pour une analyse bornée.")
        suffixes = (
            ".py",
            ".md",
            ".toml",
            ".json",
            ".js",
            ".ts",
            ".tsx",
            ".yaml",
            ".yml",
        )
        blocked = (
            ".env",
            "secret",
            "credential",
            "private_key",
            "package-lock",
            "poetry.lock",
        )
        sources, remaining = [], 16000
        entries = sorted(
            tree.get("tree", []),
            key=lambda x: (not x["path"].lower().startswith("readme"), x["path"]),
        )
        inspected = 0
        for entry in entries:
            path = entry["path"]
            if (
                entry.get("type") != "blob"
                or not path.lower().endswith(suffixes)
                or any(word in path.lower() for word in blocked)
            ):
                continue
            if int(entry.get("size", 0)) > min(30000, remaining):
                continue
            if inspected >= 12:
                break
            inspected += 1
            blob = self.request(
                "GET",
                self.repo_path(repository)
                + "/git/blobs/"
                + quote(entry["sha"], safe=""),
            )
            try:
                raw = base64.b64decode(blob["content"], validate=False)
                if len(raw) > min(30000, remaining):
                    continue
                text = raw.decode("utf-8")
            except (ValueError, UnicodeDecodeError, KeyError):
                logging.getLogger(__name__).info(
                    "Extrait non textuel ignoré lors de la collecte"
                )
                continue
            # Rejet conservateur du fichier entier ; la détection n'est pas un audit de secrets.
            lowered = text.lower()
            if "\x00" in text or any(
                s in lowered
                for s in (
                    "-----begin private",
                    "-----begin rsa private",
                    "sk-proj-",
                    "ghp_",
                    "password=",
                    "api_key=",
                    "api_key =",
                    "secret_key=",
                )
            ):
                continue
            sources.append(
                {"source_id": f"src_{len(sources)+1:02}", "path": path, "content": text}
            )
            remaining -= len(raw)
            if len(sources) >= 12 or remaining <= 0:
                break
        if not sources:
            raise Conflict(
                "Aucun extrait texte admissible : créez une tâche manuellement."
            )
        return sources
