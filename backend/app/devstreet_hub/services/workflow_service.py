"""Règles de DevStreet Hub ; toutes les requêtes ORM sont déléguées au repository."""

import hashlib
import json
from django.db import transaction
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework.exceptions import ValidationError, PermissionDenied
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


class WorkflowService:
    def __init__(self, repository=None, forge=None):
        self.repo = repository or WorkflowRepository()
        self._forge = forge

    @property
    def forge(self):
        return self._forge or GiteaClient()

    def project(self, actor, pk):
        return self.repo.visible_project(actor, pk)

    def create_project(self, actor, data):
        require_permission(actor, "projects.create")
        data = dict(data)
        technologies = data.pop("technologies", [])
        with transaction.atomic():
            project = self.repo.create_project(actor, data, technologies)
            record("project.created", actor=actor, target=project)
        return project

    def update_project(self, actor, project, data):
        require_permission(actor, "projects.update")
        require_maintainer(actor, project, self.repo)
        data = dict(data)
        with transaction.atomic():
            project = self.repo.locked_project(project.pk)
            if project.status == "archived":
                raise Conflict("Un projet archivé ne se modifie plus.")
            technologies = data.pop("technologies", None)
            if technologies is not None:
                self.repo.set_technologies(project, technologies)
            self.repo.save(project, updated_by=actor.pk, **data)
        return project

    def provision_identity(self, actor):
        require_permission(actor, "projects.create")
        with transaction.atomic():
            self.repo.lock_actor(actor)
            identity = self.repo.identity(actor)
            if identity:
                return {"login": identity.login, "created": False}
            user, password = self.forge.provision_identity(actor)
            identity = self.repo.create_identity(actor, user)
            record("project.forge_identity_created", actor=actor, target=identity)
        # Le secret n'est jamais sauvegardé ni journalisé ; affichage une seule fois.
        return {
            "login": identity.login,
            "created": True,
            "initial_password": password,
            "change_password_required": True,
        }

    def provision_repository(self, actor, project):
        require_permission(actor, "projects.create")
        require_owner(actor, project)
        try:
            with transaction.atomic():
                project = self.repo.locked_project(project.pk)
                repository = project.repository
                if repository.status == "ready":
                    return repository
                identity = self.repo.identity(actor)
                if not identity:
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
