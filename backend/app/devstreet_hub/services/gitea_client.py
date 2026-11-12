"""Adaptateur HTTP Gitea. Aucun mot de passe Django ni code utilisateur n'est exécuté."""

import base64
import logging
import secrets
import re
from urllib.parse import quote, urlsplit
import httpx
from django.conf import settings
from app.devstreet_hub.conf import config
from app.devstreet_hub.services.errors import ExternalUnavailable, Conflict


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

    def request(self, method, path, data=None, *, missing_ok=False):
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
            response.raise_for_status()
            if not response.content:
                return None
            return response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise ExternalUnavailable(
                "La forge ne répond pas correctement ; réessayez."
            ) from error

    def provision_identity(self, actor):
        login = f"devstreet-user-{actor.pk}"
        existing = self.request("GET", "/users/" + login, missing_ok=True)
        if existing:
            # Ne pas adopter un compte existant dont la propriété n'est pas établie.
            raise Conflict(
                "Compte Git déjà présent sans liaison locale : rapprochement administratif requis."
            )
        password = secrets.token_urlsafe(32)
        user = self.request(
            "POST",
            "/admin/users",
            {
                "username": login,
                "email": actor.email,
                "password": password,
                "must_change_password": True,
                "send_notify": False,
            },
        )
        return user, password

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
