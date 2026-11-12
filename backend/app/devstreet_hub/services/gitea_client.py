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

    def reissue_password(
        self, *, login: str, email: str, must_change_password: bool = True
    ) -> str:
        """Réémet un secret forge (login déjà prouvé / lié localement)."""
        password = secrets.token_urlsafe(32)
        self.request(
            "PATCH",
            "/admin/users/" + quote(login, safe=""),
            {
                "source_id": 0,
                "login_name": login,
                "email": email,
                "password": password,
                "must_change_password": must_change_password,
            },
        )
        return password

    def create_user_access_token(
        self,
        *,
        login: str,
        email: str,
        name: str,
        scopes: list[str] | None = None,
    ) -> dict:
        """Crée un PAT Gitea réel pour l'utilisateur lié (BasicAuth temporaire).

        Le jeton admin n'est jamais exposé. Le mot de passe temporaire sert uniquement
        à POST /users/{login}/tokens puis est invalidé immédiatement.
        """
        scopes = scopes or [
            "write:repository",
            "read:repository",
            "read:user",
        ]
        temp_password = self.reissue_password(
            login=login, email=email, must_change_password=False
        )
        try:
            with httpx.Client(
                timeout=20, follow_redirects=False, trust_env=False
            ) as client:
                response = client.request(
                    "POST",
                    self.url + "/api/v1/users/" + quote(login, safe="") + "/tokens",
                    headers={"Content-Type": "application/json"},
                    auth=(login, temp_password),
                    json={"name": name[:255], "scopes": scopes},
                )
            if response.status_code == 409:
                raise Conflict(
                    "Un accès Git porte déjà ce nom ; choisissez un autre libellé."
                )
            response.raise_for_status()
            payload = response.json()
        except Conflict:
            raise
        except (httpx.HTTPError, ValueError) as error:
            raise ExternalUnavailable(
                "La forge ne répond pas correctement ; réessayez."
            ) from error
        finally:
            # Invalide le mot de passe temporaire (secret aléatoire inconnu de l'utilisateur).
            # must_change_password DOIT rester False : sinon Gitea bloque aussi les PAT
            # (git push / API) jusqu'à un changement de mot de passe interactif.
            self.reissue_password(
                login=login, email=email, must_change_password=False
            )
        if not isinstance(payload, dict) or not payload.get("sha1"):
            raise ExternalUnavailable(
                "La forge n'a pas renvoyé de jeton d'accès utilisable."
            )
        return payload

    def delete_user_access_token(self, *, login: str, email: str, token_id: int) -> None:
        """Révoque un PAT Gitea (BasicAuth temporaire, puis invalidation du mot de passe)."""
        temp_password = self.reissue_password(
            login=login, email=email, must_change_password=False
        )
        try:
            with httpx.Client(
                timeout=20, follow_redirects=False, trust_env=False
            ) as client:
                response = client.request(
                    "DELETE",
                    self.url
                    + "/api/v1/users/"
                    + quote(login, safe="")
                    + "/tokens/"
                    + str(int(token_id)),
                    auth=(login, temp_password),
                )
            if response.status_code not in (204, 404):
                response.raise_for_status()
        except (httpx.HTTPError, ValueError) as error:
            raise ExternalUnavailable(
                "La forge ne répond pas correctement ; réessayez."
            ) from error
        finally:
            self.reissue_password(
                login=login, email=email, must_change_password=False
            )

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

    # --- Exploration de dépôt (lecture seule, sans copier dans Django) ---

    MAX_BLOB_BYTES = 512 * 1024
    MAX_README_BYTES = 200 * 1024
    MAX_TREE_ENTRIES = 500
    MAX_BRANCHES = 100
    MAX_ARCHIVE_BYTES = 50 * 1024 * 1024

    def get_repository_meta(self, repository) -> dict:
        """Métadonnées Gitea du dépôt lié (taille, description, empty…)."""
        return self.request("GET", self.repo_path(repository)) or {}

    def list_branches(self, repository) -> list[dict]:
        items = self.request(
            "GET",
            self.repo_path(repository) + f"/branches?limit={self.MAX_BRANCHES}&page=1",
            missing_ok=True,
        )
        if not isinstance(items, list):
            return []
        return items[: self.MAX_BRANCHES]

    def list_tags(self, repository) -> list[dict]:
        items = self.request(
            "GET",
            self.repo_path(repository) + "/tags?limit=50&page=1",
            missing_ok=True,
        )
        if not isinstance(items, list):
            return []
        return items[:50]

    def get_languages(self, repository) -> dict:
        payload = self.request(
            "GET", self.repo_path(repository) + "/languages", missing_ok=True
        )
        return payload if isinstance(payload, dict) else {}

    def count_commits(self, repository, *, ref: str) -> int | None:
        """Compte approximatif via en-tête ; None si la forge ne le fournit pas."""
        try:
            with httpx.Client(
                timeout=15, follow_redirects=False, trust_env=False
            ) as client:
                response = client.request(
                    "GET",
                    self.url
                    + "/api/v1"
                    + self.repo_path(repository)
                    + "/commits?limit=1&stat=false&sha="
                    + quote(ref, safe=""),
                    headers={"Authorization": "token " + self.token},
                )
            if response.status_code == 404:
                return 0
            response.raise_for_status()
            for header in ("X-Total-Count", "x-total-count"):
                raw = response.headers.get(header)
                if raw and raw.isdigit():
                    return int(raw)
            data = response.json() if response.content else []
            if isinstance(data, list):
                return len(data) if len(data) < 1 else None
            return None
        except (httpx.HTTPError, ValueError) as error:
            raise ExternalUnavailable(
                "La forge ne répond pas correctement ; réessayez."
            ) from error

    def latest_commit(self, repository, *, ref: str, path: str = "") -> dict | None:
        query = f"/commits?limit=1&stat=false&sha={quote(ref, safe='')}"
        if path:
            query += f"&path={quote(path, safe='/')}"
        items = self.request(
            "GET", self.repo_path(repository) + query, missing_ok=True
        )
        if not isinstance(items, list) or not items:
            return None
        return items[0] if isinstance(items[0], dict) else None

    def get_contents(self, repository, *, path: str, ref: str):
        """Liste (dossier) ou entrée (fichier) via l'API contents Gitea."""
        suffix = ""
        if path:
            suffix = "/" + quote(path, safe="/")
        return self.request(
            "GET",
            self.repo_path(repository)
            + "/contents"
            + suffix
            + "?ref="
            + quote(ref, safe=""),
            missing_ok=True,
        )

    def get_raw_blob(self, repository, *, path: str, ref: str) -> bytes | None:
        """Contenu brut borné ; None si absent."""
        if not path:
            return None
        try:
            with httpx.Client(
                timeout=15, follow_redirects=False, trust_env=False
            ) as client:
                response = client.request(
                    "GET",
                    self.url
                    + "/api/v1"
                    + self.repo_path(repository)
                    + "/raw/"
                    + quote(path, safe="/")
                    + "?ref="
                    + quote(ref, safe=""),
                    headers={"Authorization": "token " + self.token},
                )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            # Limite stricte : on ne lit pas au-delà.
            return response.content[: self.MAX_BLOB_BYTES + 1]
        except (httpx.HTTPError, ValueError) as error:
            raise ExternalUnavailable(
                "La forge ne répond pas correctement ; réessayez."
            ) from error

    def download_archive(self, repository, *, ref: str, fmt: str) -> bytes | None:
        """Archive ZIP/TAR.GZ bornée ; None si référence absente."""
        if fmt not in ("zip", "tar.gz"):
            raise ValueError("format archive invalide")
        archive = f"{quote(ref, safe='')}.{fmt}"
        try:
            with httpx.Client(
                timeout=60, follow_redirects=True, trust_env=False
            ) as client:
                response = client.request(
                    "GET",
                    self.url
                    + "/api/v1"
                    + self.repo_path(repository)
                    + "/archive/"
                    + archive,
                    headers={"Authorization": "token " + self.token},
                )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.content[: self.MAX_ARCHIVE_BYTES + 1]
        except (httpx.HTTPError, ValueError) as error:
            raise ExternalUnavailable(
                "La forge ne répond pas correctement ; réessayez."
            ) from error
