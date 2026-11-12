"""Règles de DevStreet Hub ; toutes les requêtes ORM sont déléguées au repository."""

import hashlib
import json
import re
from urllib.parse import quote
from django.db import transaction
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from app.core.services.audit_service import record
from app.devstreet_hub.conf import config
from app.devstreet_hub.permissions.policy import (
    require_permission,
    require_maintainer,
    require_owner,
)
from app.devstreet_hub.repositories.workflow_repository import WorkflowRepository
from app.devstreet_hub.services.errors import (
    Conflict,
    ExternalUnavailable,
    QuotaExceeded,
)
from app.devstreet_hub.services.gitea_client import GiteaClient

_REF_RE = re.compile(r"^[A-Za-z0-9._/\-]+$")
_PATH_RE = re.compile(r"^(?:[A-Za-z0-9._\-]+(?:/[A-Za-z0-9._\-]+)*)?$")


class WorkflowService:
    def __init__(self, repository=None, forge=None):
        self.repo = repository or WorkflowRepository()
        self._forge = forge

    @property
    def forge(self):
        return self._forge or GiteaClient()

    def project(self, actor, pk):
        return self.repo.visible_project(actor, pk)

    def _ready_repository(self, actor, project):
        """Dépôt prêt et visible ; la liaison locale est la seule source d'identité forge."""
        project = self.repo.visible_project(actor, project.pk)
        repository = project.repository
        if repository.status != "ready" or not repository.namespace or not repository.name:
            raise Conflict("Le dépôt n’est pas encore prêt.")
        return project, repository

    def _normalize_ref(self, ref: str | None, repository) -> str:
        value = (ref or repository.default_branch or "main").strip()
        if not value or not _REF_RE.fullmatch(value) or ".." in value:
            raise ValidationError({"ref": "Référence de branche invalide."})
        return value

    def _normalize_path(self, path: str | None) -> str:
        value = (path or "").strip().strip("/")
        if not value:
            return ""
        if not _PATH_RE.fullmatch(value) or ".." in value.split("/"):
            raise ValidationError({"path": "Chemin invalide."})
        return value

    def _clone_url(self, repository) -> str | None:
        url = config("GITEA_PUBLIC_URL", config("GITEA_URL")).rstrip("/")
        if not url or repository.status != "ready":
            return None
        return f"{url}/{quote(repository.namespace)}/{quote(repository.name)}.git"

    def _format_commit(self, commit: dict | None) -> dict | None:
        if not commit:
            return None
        sha = commit.get("sha") or ""
        commit_info = commit.get("commit") or {}
        author = commit_info.get("author") or {}
        # Nom forge uniquement : ne prouve pas une identité DevStreet.
        return {
            "sha": sha,
            "short_sha": sha[:10] if isinstance(sha, str) else "",
            "message": (commit_info.get("message") or "").split("\n", 1)[0][:240],
            "author_name": (author.get("name") or "")[:120] or None,
            "authored_at": author.get("date"),
        }

    def _language_breakdown(self, languages: dict) -> list[dict]:
        total = sum(int(v) for v in languages.values() if isinstance(v, (int, float)))
        if total <= 0:
            return []
        items = []
        for name, bytes_count in sorted(
            languages.items(), key=lambda item: (-int(item[1] or 0), item[0])
        ):
            count = int(bytes_count or 0)
            if count <= 0:
                continue
            items.append(
                {
                    "name": str(name)[:40],
                    "bytes": count,
                    "percent": round(100.0 * count / total, 1),
                }
            )
        return items[:12]

    def code_summary(self, actor, project):
        """Statistiques et métadonnées d'exploration ; pas de compteur d'étoiles Gitea."""
        project, repository = self._ready_repository(actor, project)
        meta = self.forge.get_repository_meta(repository)
        is_empty = bool(meta.get("empty")) or self.forge.repo_is_empty(repository)
        default_branch = (
            meta.get("default_branch")
            or repository.default_branch
            or "main"
        )
        branches = [] if is_empty else self.forge.list_branches(repository)
        tags = [] if is_empty else self.forge.list_tags(repository)
        languages = [] if is_empty else self._language_breakdown(
            self.forge.get_languages(repository)
        )
        commit_count = None
        if not is_empty:
            commit_count = self.forge.count_commits(repository, ref=default_branch)
        description = meta.get("description")
        if isinstance(description, str):
            description = description.strip() or None
        else:
            description = None
        size = meta.get("size")
        return {
            "default_branch": default_branch,
            "is_empty": is_empty,
            "clone_url": self._clone_url(repository),
            "description": description,
            "size_kib": int(size) if isinstance(size, (int, float)) else None,
            "stats": {
                "commits": commit_count,
                "branches": len(branches) if branches is not None else None,
                "tags": len(tags) if tags is not None else None,
            },
            "languages": languages,
            "repository": repository,
        }

    def code_branches(self, actor, project):
        project, repository = self._ready_repository(actor, project)
        if self.forge.repo_is_empty(repository):
            return []
        result = []
        for item in self.forge.list_branches(repository):
            name = item.get("name")
            if not isinstance(name, str) or not name:
                continue
            commit = item.get("commit") or {}
            result.append(
                {
                    "name": name,
                    "commit": self._format_commit(
                        {
                            "sha": commit.get("id") or commit.get("sha") or "",
                            "commit": {
                                "message": commit.get("message")
                                or (commit.get("commit") or {}).get("message")
                                or "",
                                "author": {
                                    "name": (
                                        (commit.get("author") or {}).get("name")
                                        or (
                                            (commit.get("commit") or {}).get("author")
                                            or {}
                                        ).get("name")
                                    ),
                                    "date": (
                                        (commit.get("author") or {}).get("date")
                                        or (
                                            (commit.get("commit") or {}).get("author")
                                            or {}
                                        ).get("date")
                                    ),
                                },
                            },
                        }
                    ),
                }
            )
        return result

    def code_tree(self, actor, project, *, ref=None, path=None):
        project, repository = self._ready_repository(actor, project)
        ref = self._normalize_ref(ref, repository)
        path = self._normalize_path(path)
        if self.forge.repo_is_empty(repository):
            return {
                "ref": ref,
                "path": path,
                "is_empty": True,
                "entries": [],
                "latest_commit": None,
                "readme": None,
            }
        contents = self.forge.get_contents(repository, path=path, ref=ref)
        if contents is None:
            raise NotFound("Dossier ou référence introuvable.")
        # Un fichier unique : le client doit utiliser /code/blob.
        if isinstance(contents, dict) and contents.get("type") == "file":
            raise NotFound("Ce chemin désigne un fichier, pas un dossier.")
        entries_raw = contents if isinstance(contents, list) else []
        entries = []
        for entry in entries_raw[: self.forge.MAX_TREE_ENTRIES]:
            if not isinstance(entry, dict):
                continue
            name = entry.get("name") or ""
            entry_path = entry.get("path") or name
            entry_type = "dir" if entry.get("type") == "dir" else "file"
            entries.append(
                {
                    "name": name,
                    "path": entry_path,
                    "type": entry_type,
                    "size": entry.get("size") if entry_type == "file" else None,
                    "sha": entry.get("sha"),
                }
            )
        entries.sort(key=lambda item: (0 if item["type"] == "dir" else 1, item["name"].lower()))
        latest = self._format_commit(
            self.forge.latest_commit(repository, ref=ref, path=path)
        )
        readme = None
        if not path:
            readme = self._load_readme(repository, ref=ref, entries=entries)
        return {
            "ref": ref,
            "path": path,
            "is_empty": False,
            "entries": entries,
            "latest_commit": latest,
            "readme": readme,
        }

    def _load_readme(self, repository, *, ref: str, entries: list) -> dict | None:
        candidates = [
            e["path"]
            for e in entries
            if e["type"] == "file" and e["name"].lower() in (
                "readme.md",
                "readme.markdown",
                "readme.mdown",
                "readme",
            )
        ]
        if not candidates:
            return None
        path = sorted(candidates, key=lambda p: (0 if p.lower().endswith(".md") else 1, p))[0]
        raw = self.forge.get_raw_blob(repository, path=path, ref=ref)
        if raw is None:
            return None
        truncated = len(raw) > self.forge.MAX_README_BYTES
        raw = raw[: self.forge.MAX_README_BYTES]
        if b"\x00" in raw:
            return None
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return None
        return {
            "name": path.split("/")[-1],
            "path": path,
            "content": text,
            "truncated": truncated,
        }

    def code_blob(self, actor, project, *, ref=None, path=None):
        project, repository = self._ready_repository(actor, project)
        ref = self._normalize_ref(ref, repository)
        path = self._normalize_path(path)
        if not path:
            raise ValidationError({"path": "Chemin de fichier requis."})
        meta = self.forge.get_contents(repository, path=path, ref=ref)
        if meta is None:
            raise NotFound("Fichier ou référence introuvable.")
        if isinstance(meta, list):
            raise NotFound("Ce chemin désigne un dossier, pas un fichier.")
        if not isinstance(meta, dict) or meta.get("type") != "file":
            raise NotFound("Fichier introuvable.")
        size = int(meta.get("size") or 0)
        raw = self.forge.get_raw_blob(repository, path=path, ref=ref)
        if raw is None:
            raise NotFound("Fichier introuvable.")
        too_large = len(raw) > self.forge.MAX_BLOB_BYTES or size > self.forge.MAX_BLOB_BYTES
        sample = raw[: self.forge.MAX_BLOB_BYTES]
        is_binary = b"\x00" in sample
        content = None
        encoding = "none"
        if not too_large and not is_binary:
            try:
                content = sample.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                is_binary = True
                content = None
                encoding = "none"
        # HTML et tout texte : jamais exécutés ; renvoyés comme code source.
        return {
            "ref": ref,
            "path": path,
            "name": path.split("/")[-1],
            "size": size or len(sample),
            "sha": meta.get("sha"),
            "encoding": encoding,
            "content": content,
            "is_binary": is_binary,
            "is_too_large": too_large,
            "language": self._guess_language(path),
            "latest_commit": self._format_commit(
                self.forge.latest_commit(repository, ref=ref, path=path)
            ),
        }

    def _guess_language(self, path: str) -> str | None:
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        mapping = {
            "py": "python",
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "html": "html",
            "htm": "html",
            "css": "css",
            "scss": "scss",
            "json": "json",
            "md": "markdown",
            "yml": "yaml",
            "yaml": "yaml",
            "toml": "toml",
            "rs": "rust",
            "go": "go",
            "java": "java",
            "sh": "bash",
            "sql": "sql",
            "xml": "xml",
            "svg": "xml",
        }
        return mapping.get(ext)

    def create_project(self, actor, data):
        require_permission(actor, "projects.create")
        data = dict(data)
        technologies = data.pop("technologies", [])
        data = self._normalize_project_write(data, exclude_pk=None, creating=True)
        with transaction.atomic():
            project = self.repo.create_project(actor, data, technologies)
            record("project.created", actor=actor, target=project)
        return project

    def _normalize_project_write(self, data, *, exclude_pk, creating=False):
        from app.devstreet_hub.services.project_slug import (
            allocate_unique_slug,
            is_valid_slug,
            normalize_slug,
        )

        data = dict(data)
        if "demo_url" in data and data["demo_url"] in (None, ""):
            data["demo_url"] = ""
        if creating:
            data.setdefault("problem", "")
            data.setdefault("description", "")

        if "slug" in data or creating:
            raw_slug = (data.get("slug") or "").strip()
            if raw_slug:
                slug = normalize_slug(raw_slug)
                if not is_valid_slug(slug):
                    raise ValidationError({"slug": "Slug invalide."})
                if self.repo.slug_exists(slug, exclude_pk=exclude_pk):
                    raise ValidationError({"slug": "Ce slug est déjà pris."})
                data["slug"] = slug
            elif creating:
                data["slug"] = allocate_unique_slug(
                    data.get("title") or "projet",
                    exists=lambda candidate: self.repo.slug_exists(candidate),
                )
            else:
                data.pop("slug", None)
        return data

    def create_and_setup(self, actor, data):
        """Crée le brouillon puis orchestre identité forge + dépôt (reprise sans doublon)."""
        project = self.create_project(actor, data)
        return self._run_setup(actor, project)

    def resume_setup(self, actor, project):
        """Reprend identité + dépôt après échec partiel ; idempotent si déjà prêts."""
        require_permission(actor, "projects.create")
        require_owner(actor, project)
        return self._run_setup(actor, project)

    def _run_setup(self, actor, project):
        setup = {"draft": "ok", "identity": "pending", "repository": "pending"}
        forge_access = None
        try:
            forge_access = self.provision_identity(actor)
            setup["identity"] = "ok"
        except Conflict:
            setup["identity"] = "conflict"
            project = self.repo.visible_project(actor, project.pk)
            return {"project": project, "forge_access": None, "setup": setup}
        except ExternalUnavailable:
            setup["identity"] = "failed"
            project = self.repo.visible_project(actor, project.pk)
            return {"project": project, "forge_access": forge_access, "setup": setup}

        try:
            repository = self.provision_repository(actor, project)
            setup["repository"] = "ok" if repository.status == "ready" else "failed"
        except ExternalUnavailable:
            setup["repository"] = "failed"
        except Conflict:
            setup["repository"] = "failed"

        project = self.repo.visible_project(actor, project.pk)
        return {
            "project": project,
            "forge_access": forge_access,
            "setup": setup,
        }

    def initialize_repository(self, actor, project, *, mode: str):
        """Initialise le dépôt dans DevStreet : scaffold Gitea ou consignes de push."""
        require_permission(actor, "projects.create")
        require_owner(actor, project)
        repository = project.repository
        if repository.status != "ready":
            raise Conflict("Le dépôt doit être prêt avant l’initialisation.")

        if mode == "push_existing":
            return {
                "mode": mode,
                "initialized": False,
                "is_empty": not bool(repository.current_sha),
                "repository": repository,
            }

        if mode != "readme":
            raise ValidationError({"mode": "Mode d’initialisation inconnu."})

        if repository.current_sha:
            raise Conflict("Le dépôt contient déjà des commits.")

        from app.devstreet_hub.services.repo_scaffold import scaffold_files

        try:
            if not self.forge.repo_is_empty(repository):
                sha = self.forge.head(repository)
                self.repo.save(repository, current_sha=sha)
                raise Conflict("Le dépôt contient déjà des commits.")
            result = self.forge.initialize_scaffold(
                repository,
                scaffold_files(
                    title=project.title,
                    problem=project.problem,
                    declared_license=project.declared_license,
                ),
            )
        except ExternalUnavailable:
            raise

        repository = self.repo.save(
            repository,
            current_sha=result["sha"],
            default_branch=result.get("branch") or repository.default_branch,
        )
        record("project.repository_initialized", actor=actor, target=project)
        return {
            "mode": mode,
            "initialized": True,
            "is_empty": False,
            "repository": repository,
        }

    def update_project(self, actor, project, data):
        require_permission(actor, "projects.update")
        require_maintainer(actor, project, self.repo)
        data = dict(data)
        with transaction.atomic():
            project = self.repo.locked_project(project.pk)
            if project.status == "archived":
                raise Conflict("Un projet archivé ne se modifie plus.")
            technologies = data.pop("technologies", None)
            data = self._normalize_project_write(
                data, exclude_pk=project.pk, creating=False
            )
            if technologies is not None:
                self.repo.set_technologies(project, technologies)
            self.repo.save(project, updated_by=actor.pk, **data)
        return project

    def provision_identity(self, actor):
        """Provisionne ou reprend une identité Gitea liée explicitement.

        1. Persiste login opaque + provisioning_key avant tout appel externe.
        2. Crée/vérifie le compte distant avec preuve dans `description`.
        3. N'adopte jamais un compte tiers (login/e-mail seuls insuffisants).
        """
        require_permission(actor, "projects.create")
        from app.devstreet_hub.models import ForgeIdentity
        from app.devstreet_hub.services.forge_identity_tokens import (
            login_for_key,
            new_provisioning_key,
        )

        with transaction.atomic():
            self.repo.lock_actor(actor)
            identity = self.repo.locked_identity(actor)

            if identity and identity.status == ForgeIdentity.STATUS_CONFLICT:
                raise Conflict(
                    identity.conflict_reason
                    or "Identité Git en conflit : réparation administrative requise."
                )

            if (
                identity
                and identity.status == ForgeIdentity.STATUS_LINKED
                and identity.gitea_user_id
            ):
                linked_id = identity.pk
            elif identity is None:
                key = new_provisioning_key()
                identity = self.repo.create_pending_identity(
                    actor,
                    login=login_for_key(key),
                    provisioning_key=key,
                )
                linked_id = None
            else:
                linked_id = None

        # Hors transaction : appels Gitea + persistance des conflits (pas de rollback).
        if linked_id is not None:
            return self._reuse_linked_identity(actor)

        return self._complete_pending_identity(actor, identity)

    def reset_forge_password(self, actor):
        """Réémet le secret Git de l'identité liée à l'acteur (jamais un login client).

        Invalide l'ancien mot de passe forge. Ne touche ni au mot de passe Django,
        ni aux dépôts. Le secret n'est ni journalisé ni persisté.
        """
        require_permission(actor, "projects.create")
        from app.devstreet_hub.models import ForgeIdentity

        identity = self.repo.identity(actor)
        if identity is None:
            raise Conflict(
                "Aucun accès Git n’est encore lié à ce compte. Créez d’abord un projet."
            )
        if identity.status == ForgeIdentity.STATUS_CONFLICT:
            raise Conflict(
                identity.conflict_reason
                or "Identité Git en conflit : réparation administrative requise."
            )
        if (
            identity.status != ForgeIdentity.STATUS_LINKED
            or not identity.gitea_user_id
        ):
            raise Conflict(
                "L’accès Git n’est pas encore confirmé. Reprenez la préparation du dépôt."
            )

        # Vérifie que l'ID distant correspond toujours à la liaison locale.
        remote = self.forge.get_user_by_id(identity.gitea_user_id)
        if remote is None or remote.get("id") != identity.gitea_user_id:
            reason = (
                "Compte Git distant introuvable pour cette liaison ; "
                "réparation administrative requise."
            )
            with transaction.atomic():
                current = self.repo.locked_identity(actor)
                if current:
                    self.repo.mark_identity_conflict(current, reason)
            raise Conflict(reason)

        login = identity.login
        if remote.get("login") and remote["login"] != login:
            with transaction.atomic():
                current = self.repo.locked_identity(actor)
                if current and current.gitea_user_id == identity.gitea_user_id:
                    self.repo.save(current, login=remote["login"])
                    login = remote["login"]

        # False : le secret doit servir immédiatement au git push sans UI Gitea.
        password = self.forge.reissue_password(
            login=login,
            email=actor.email,
            must_change_password=False,
        )
        record("project.forge_password_reset", actor=actor, target=identity)
        return {
            "login": login,
            "created": False,
            "reset": True,
            "initial_password": password,
            "change_password_required": False,
        }

    def _reuse_linked_identity(self, actor):
        """Réutilise une liaison existante ; vérifie l'ID distant, jamais un login tiers."""
        identity = self.repo.identity(actor)
        if identity is None or not identity.gitea_user_id:
            raise Conflict("Identité Git liée introuvable.")

        remote = self.forge.get_user_by_id(identity.gitea_user_id)
        if remote is None or remote.get("id") != identity.gitea_user_id:
            reason = (
                "Compte Git distant introuvable pour cette liaison ; "
                "réparation administrative requise."
                if remote is None
                else "L'identifiant Git distant ne correspond plus à la liaison locale."
            )
            with transaction.atomic():
                self.repo.lock_actor(actor)
                current = self.repo.locked_identity(actor)
                if current:
                    self.repo.mark_identity_conflict(current, reason)
            raise Conflict(reason)

        # Un rename côté forge met à jour le login local ; on n'adopte pas un autre id.
        if remote.get("login") and remote["login"] != identity.login:
            with transaction.atomic():
                self.repo.lock_actor(actor)
                current = self.repo.locked_identity(actor)
                if current and current.gitea_user_id == identity.gitea_user_id:
                    self.repo.save(current, login=remote["login"])
                    identity = current
        return {"login": identity.login, "created": False}

    def _complete_pending_identity(self, actor, identity):
        """Termine une identité pending : création distante ou reprise contrôlée."""
        from app.devstreet_hub.models import ForgeIdentity
        from app.devstreet_hub.services.forge_identity_tokens import has_correlation

        with transaction.atomic():
            self.repo.lock_actor(actor)
            identity = self.repo.locked_identity(actor)
            if identity is None:
                raise Conflict("Identité Git introuvable après réservation.")
            if (
                identity.status == ForgeIdentity.STATUS_LINKED
                and identity.gitea_user_id
            ):
                return {"login": identity.login, "created": False}
            if identity.status == ForgeIdentity.STATUS_CONFLICT:
                raise Conflict(
                    identity.conflict_reason
                    or "Identité Git en conflit : réparation administrative requise."
                )

        key = identity.provisioning_key
        login = identity.login
        remote = self.forge.get_user_by_login(login)

        if remote is not None:
            if not has_correlation(remote, key):
                with transaction.atomic():
                    identity = self.repo.locked_identity(actor)
                    self.repo.mark_identity_conflict(
                        identity,
                        "Compte Git déjà présent sans preuve de propriété DevStreet Hub.",
                    )
                raise Conflict(
                    "Compte Git déjà présent sans preuve de propriété DevStreet Hub : "
                    "rapprochement administratif requis."
                )
            # Reprise après échec Django / timeout : secret initial perdu.
            with transaction.atomic():
                self.repo.lock_actor(actor)
                identity = self.repo.locked_identity(actor)
                self.repo.mark_identity_linked(
                    identity, gitea_user_id=remote["id"], login=remote.get("login") or login
                )
                record(
                    "project.forge_identity_recovered",
                    actor=actor,
                    target=identity,
                )
            # Réémission explicite (pas silencieuse) d'un secret à usage unique.
            password = self.forge.reissue_password(login=login, email=actor.email)
            return {
                "login": login,
                "created": False,
                "recovered": True,
                "initial_password": password,
                "change_password_required": True,
                "password_recovery_required": True,
            }

        try:
            user, password = self.forge.create_user(
                login=login,
                email=actor.email,
                provisioning_key=key,
            )
        except ExternalUnavailable:
            # Timeout ambigu : pas de doublon au prochain essai (même login/clé).
            raise
        except Conflict as error:
            with transaction.atomic():
                identity = self.repo.locked_identity(actor)
                if identity and identity.status == ForgeIdentity.STATUS_PENDING:
                    self.repo.mark_identity_conflict(identity, str(error.detail))
            raise

        with transaction.atomic():
            self.repo.lock_actor(actor)
            identity = self.repo.locked_identity(actor)
            if identity is None:
                raise Conflict("Identité Git réservée introuvable après création distante.")
            if (
                identity.status == ForgeIdentity.STATUS_LINKED
                and identity.gitea_user_id
                and identity.gitea_user_id != user["id"]
            ):
                raise Conflict(
                    "Une autre liaison Git a été confirmée pendant le provisionnement."
                )
            self.repo.mark_identity_linked(
                identity,
                gitea_user_id=user["id"],
                login=user.get("login") or login,
            )
            record("project.forge_identity_created", actor=actor, target=identity)

        # Le secret n'est jamais sauvegardé ni journalisé ; affichage une seule fois.
        payload = {
            "login": identity.login,
            "created": True,
            "change_password_required": True,
        }
        if password:
            payload["initial_password"] = password
        else:
            # Compte distant déjà corrélé sans secret (reprise via create_user).
            password = self.forge.reissue_password(login=login, email=actor.email)
            payload.update(
                {
                    "created": False,
                    "recovered": True,
                    "initial_password": password,
                    "password_recovery_required": True,
                }
            )
        return payload

    def provision_repository(self, actor, project):
        require_permission(actor, "projects.create")
        require_owner(actor, project)
        try:
            with transaction.atomic():
                project = self.repo.locked_project(project.pk)
                repository = project.repository
                if repository.status == "ready":
                    return repository
                from app.devstreet_hub.models import ForgeIdentity

                identity = self.repo.identity(actor)
                if (
                    not identity
                    or identity.status != ForgeIdentity.STATUS_LINKED
                    or not identity.gitea_user_id
                ):
                    raise Conflict(
                        "Initialisez d’abord votre accès Git avec /forge-access."
                    )
                result = self.forge.provision_repository(repository, identity)
                return self.repo.save(
                    repository,
                    namespace=identity.login,
                    gitea_repo_id=result["id"],
                    default_branch=result.get("default_branch") or "main",
                    status="ready",
                )
        except ExternalUnavailable:
            self.repo.save(project.repository, status="failed")
            raise

    def transition(self, actor, project, target):
        require_permission(
            actor, "projects.publish" if target == "published" else "projects.archive"
        )
        require_owner(actor, project)
        with transaction.atomic():
            project = self.repo.locked_project(project.pk)
            if project.status == target:
                return project
            if target == "published" and project.status != "draft":
                raise Conflict("Seul un brouillon peut être publié.")
            if target == "published" and project.repository.status != "ready":
                raise Conflict("Le dépôt doit être prêt avant publication.")
            if project.repository.status == "ready":
                self.forge.set_public(project.repository, target == "published")
            self.repo.save(project, status=target, updated_by=actor.pk)
            record("project." + target, actor=actor, target=project)
        return project

    def consent(self, actor, project, enabled):
        require_permission(actor, "projects.analyze")
        require_owner(actor, project)
        return self.repo.save(
            project, ai_consent_at=timezone.now() if enabled else None
        )

    def star(self, actor, project, active):
        require_permission(actor, "projects.star")
        if project.status != "published":
            raise Conflict("Seuls les projets publiés peuvent recevoir des étoiles.")
        return self.repo.set_star(project, actor, active)

    def member(self, actor, project, user_id, role=None):
        require_permission(actor, "projects.members")
        require_owner(actor, project)
        if user_id == project.owner_id:
            raise Conflict("Le propriétaire ne se modifie pas par les membres.")
        if role is None:
            self.repo.remove_member(project, user_id)
            return None
        return self.repo.set_member(project, user_id, role)

    def create_task(self, actor, project, data):
        require_permission(actor, "contribution-tasks.create")
        require_maintainer(actor, project, self.repo)
        if project.status == "archived":
            raise Conflict("Projet archivé.")
        return self.repo.create_task(project, actor, data)

    def task_from_analysis(self, actor, project, analysis_id, suggestion_index):
        require_permission(actor, "contribution-tasks.create")
        require_maintainer(actor, project, self.repo)
        analysis = self.repo.analysis(actor, analysis_id)
        if analysis.project_id != project.pk or analysis.status != "succeeded":
            raise ValidationError("Analyse incompatible avec ce projet.")
        suggestions = analysis.result["suggested_tasks"]
        if suggestion_index >= len(suggestions):
            raise ValidationError("Suggestion absente.")
        item = suggestions[suggestion_index]
        return self.create_task(
            actor,
            project,
            {
                "analysis": analysis,
                "title": item["title"],
                "description": item["description"] + "\n\n" + "\n".join(item["steps"]),
                "acceptance_criteria": item["acceptance_criteria"],
            },
        )

    def update_task(self, actor, task, data):
        require_permission(actor, "contribution-tasks.update")
        require_maintainer(actor, task.project, self.repo)
        if task.project.status == "archived":
            raise Conflict("Projet archivé.")
        if data.get("status") == "open" and not data.get(
            "acceptance_criteria", task.acceptance_criteria
        ):
            raise ValidationError(
                "Définissez les critères de réussite avant d’ouvrir la tâche."
            )
        return self.repo.save(task, updated_by=actor.pk, **data)

    def submit(self, actor, task, data):
        require_permission(actor, "contributions.create")
        if task.status != "open" or task.project.status != "published":
            raise Conflict("La tâche doit être ouverte sur un projet publié.")
        if data.get("pull_request_number"):
            pr = self.forge.pull_request(
                task.project.repository, data["pull_request_number"]
            )
            if not pr.get("number") == data["pull_request_number"]:
                raise ValidationError("Pull request inconnue.")
        return self.repo.create_contribution(task, actor, data)

    def review(self, actor, contribution, status, note):
        require_permission(actor, "contributions.review")
        require_maintainer(actor, contribution.task.project, self.repo)
        if contribution.author_id == actor.pk:
            raise PermissionDenied(
                "Vous ne pouvez pas revoir votre propre contribution."
            )
        with transaction.atomic():
            contribution = self.repo.contribution(actor, contribution.pk, lock=True)
            if contribution.status != "submitted":
                raise Conflict("Cette contribution a déjà été revue.")
            self.repo.save(
                contribution,
                status=status,
                reviewed_by=actor,
                review_note=note,
                reviewed_at=timezone.now(),
            )
            record(
                "project.contribution_reviewed",
                actor=actor,
                target=contribution,
                metadata={"decision": status},
            )
        return contribution

    def request_analysis(self, actor, project, objective, language):
        require_permission(actor, "projects.analyze")
        require_maintainer(actor, project, self.repo)
        if not project.ai_consent_at:
            raise Conflict(
                "Le propriétaire doit autoriser l’envoi des extraits à OpenAI."
            )
        if project.status == "archived" or project.repository.status != "ready":
            raise Conflict("Le dépôt doit être prêt et le projet actif.")
        model = config("OPENAI_MODEL")
        if not model or not config("OPENAI_API_KEY"):
            raise ExternalUnavailable(
                "Configurez le modèle et la clé OpenAI côté serveur."
            )
        sha = self.forge.head(project.repository)
        key = hashlib.sha256(
            json.dumps(
                [project.pk, sha, objective, language, model, "contribution-v1"]
            ).encode()
        ).hexdigest()
        with transaction.atomic():
            self.repo.locked_project(project.pk)
            daily, project_daily = self.repo.reserve_analysis(actor, project, {})
            cached = self.repo.cached_analysis(key)
            if cached:
                return cached
            if daily >= int(config("AI_DAILY_LIMIT", 20)) or project_daily >= 2:
                raise QuotaExceeded()
            return self.repo.create_analysis(
                actor,
                project,
                objective=objective,
                language=language,
                model=model,
                cache_key=key,
                commit_sha=sha,
            )

    def link_discussion(self, actor, project, data):
        require_permission(actor, "projects.discuss")
        task = self.repo.task(actor, data["task_id"]) if data.get("task_id") else None
        if task and task.project_id != project.pk:
            raise ValidationError("La tâche appartient à un autre projet.")
        with transaction.atomic():
            self.repo.locked_project(project.pk)
            existing = self.repo.discussion(data["request_key"])
            if existing:
                if (
                    existing.project_id != project.pk
                    or existing.requested_by_id != actor.pk
                    or existing.title != data["title"]
                    or existing.body != data["body"]
                    or existing.task_id != (task.pk if task else None)
                ):
                    raise Conflict(
                        "Clé d’idempotence déjà utilisée pour une autre demande."
                    )
                return existing
            adapter_path = config("FORUM_ADAPTER")
            if not adapter_path:
                raise ExternalUnavailable("Le module forum n’est pas encore raccordé.")
            adapter = import_string(adapter_path)
            topic_id = adapter(
                actor=actor,
                project=project,
                task=task,
                title=data["title"],
                body=data["body"],
                request_key=str(data["request_key"]),
            )
            if not topic_id:
                raise ExternalUnavailable(
                    "Le forum n’a pas confirmé la création du sujet."
                )
            return self.repo.create_discussion(
                project=project,
                task=task,
                requested_by=actor,
                forum_topic_id=str(topic_id),
                **{k: data[k] for k in ("request_key", "title", "body")}
            )
