"""Accès ORM de l'agrégat DevStreet Hub ; les services ne font pas de requêtes ORM."""

from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from app.devstreet_hub.models import (
    Project,
    Technology,
    ProjectMember,
    Star,
    Repository,
    ForgeIdentity,
    RepositorySnapshot,
    AIAnalysis,
    ContributionTask,
    Contribution,
    ProjectDiscussionLink,
    WebhookDelivery,
    ProjectImage,
)
from app.devstreet_hub.repositories.project_repository import ProjectRepository


class WorkflowRepository(ProjectRepository):
    def empty_analyses(self):
        return AIAnalysis.objects.none()

    def lock_actor(self, actor):
        return get_user_model().objects.select_for_update().get(pk=actor.pk)

    def visible_projects(self, actor, *, search="", technology="", owner=None):
        visible = Q(status="published")
        if getattr(actor, "is_authenticated", False) and actor.is_active:
            visible |= Q(owner=actor) | Q(members__user=actor)
        qs = (
            Project.objects.filter(visible)
            .select_related("owner", "repository")
            .prefetch_related("technologies", "images")
            .annotate(star_count=Count("stars", distinct=True))
            .distinct()
        )
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(problem__icontains=search)
            )
        if technology:
            qs = qs.filter(technologies__slug=technology)
        if owner is not None:
            qs = qs.filter(owner_id=owner)
        return qs.order_by("-created_at", "-id")

    def visible_project(self, actor, pk):
        return get_object_or_404(self.visible_projects(actor), pk=pk)

    def locked_project(self, pk):
        return Project.objects.select_for_update().get(pk=pk)

    def save(self, instance, **values):
        for key, value in values.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def is_maintainer(self, project, actor):
        return (
            project.owner_id == actor.pk
            or ProjectMember.objects.filter(
                project=project, user=actor, role="maintainer"
            ).exists()
        )

    def slug_exists(self, slug: str, *, exclude_pk=None) -> bool:
        qs = Project.objects.filter(slug=slug)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

    def allocate_repository_name(self, project) -> str:
        """Nom du dépôt forge = slug Hub ; fallback slug-{pk} si collision locale."""
        base = (project.slug or f"project-{project.pk}")[:100]
        taken = (
            Repository.objects.filter(name=base)
            .exclude(project_id=project.pk)
            .exists()
        )
        if not taken:
            return base
        return f"{project.slug}-{project.pk}"[:100]

    def create_project(self, actor, data, technologies):
        project = self.create(
            owner=actor, created_by=actor.pk, updated_by=actor.pk, **data
        )
        project.technologies.set(technologies)
        Repository.objects.create(
            project=project, name=self.allocate_repository_name(project)
        )
        return project

    def set_technologies(self, project, technologies):
        project.technologies.set(technologies)

    def technologies(self):
        return Technology.objects.order_by("label", "id")

    def set_member(self, project, user_id, role):
        user = get_object_or_404(get_user_model(), pk=user_id, is_active=True)
        return ProjectMember.objects.update_or_create(
            project=project, user=user, defaults={"role": role}
        )[0]

    def members(self, project):
        return ProjectMember.objects.filter(project=project).order_by("id")

    def remove_member(self, project, user_id):
        ProjectMember.objects.filter(project=project, user_id=user_id).delete()

    def set_star(self, project, actor, active):
        if active:
            Star.objects.get_or_create(project=project, user=actor)
        else:
            Star.objects.filter(project=project, user=actor).delete()
        return Star.objects.filter(project=project).count()

    def star_count(self, project):
        return Star.objects.filter(project=project).count()

    def project_images(self, project):
        return list(ProjectImage.objects.filter(project=project))

    def project_image(self, project, image_id):
        return get_object_or_404(ProjectImage, project=project, pk=image_id)

    def create_project_image(self, project, file, display_name):
        image = ProjectImage(project=project, display_name=display_name)
        try:
            image.file.save(file.name, file, save=False)
            image.save()
        except Exception:
            if image.file.name:
                image.file.storage.delete(image.file.name)
            raise
        return image

    def delete_project_image(self, image):
        image.delete()

    def public_evidence(self, user_id=None):
        qs = (
            Contribution.objects.filter(
                status="accepted", task__project__status="published"
            )
            .select_related("task__project", "author", "reviewed_by")
            .order_by("-id")
        )
        return qs.filter(author_id=user_id) if user_id is not None else qs

    def identity(self, actor):
        return ForgeIdentity.objects.filter(user=actor).first()

    def locked_identity(self, actor):
        return (
            ForgeIdentity.objects.select_for_update()
            .filter(user=actor)
            .first()
        )

    def create_pending_identity(self, actor, *, login, provisioning_key):
        return ForgeIdentity.objects.create(
            user=actor,
            login=login,
            provisioning_key=provisioning_key,
            gitea_user_id=None,
            status=ForgeIdentity.STATUS_PENDING,
        )

    def mark_identity_linked(self, identity, *, gitea_user_id, login=None):
        from django.utils import timezone

        values = {
            "gitea_user_id": gitea_user_id,
            "status": ForgeIdentity.STATUS_LINKED,
            "conflict_reason": "",
            "linked_at": timezone.now(),
        }
        if login:
            values["login"] = login
        return self.save(identity, **values)

    def mark_identity_conflict(self, identity, reason: str):
        return self.save(
            identity,
            status=ForgeIdentity.STATUS_CONFLICT,
            conflict_reason=reason[:255],
        )

    def create_identity(self, actor, data):
        """Compatibilité tests historiques : crée une identité déjà liée."""
        from app.devstreet_hub.services.forge_identity_tokens import (
            new_provisioning_key,
        )
        from django.utils import timezone

        key = data.get("provisioning_key") or new_provisioning_key()
        return ForgeIdentity.objects.create(
            user=actor,
            login=data["login"],
            gitea_user_id=data["id"],
            provisioning_key=key,
            status=ForgeIdentity.STATUS_LINKED,
            linked_at=timezone.now(),
        )

    def visible_tasks(self, actor, project_id=None):
        public = Q(project__status="published", status__in=["open", "closed"])
        if getattr(actor, "is_authenticated", False):
            public |= Q(project__owner=actor) | Q(
                project__members__user=actor, project__members__role="maintainer"
            )
        qs = (
            ContributionTask.objects.filter(public)
            .select_related("project", "analysis__snapshot__repository")
            .distinct()
            .order_by("-id")
        )

        return qs.filter(project_id=project_id) if project_id is not None else qs

    def task(self, actor, pk):
        return get_object_or_404(self.visible_tasks(actor), pk=pk)

    def create_task(self, project, actor, data):
        return ContributionTask.objects.create(
            project=project, created_by=actor.pk, updated_by=actor.pk, **data
        )

    def contributions(self, actor, project_id=None, task_id=None, author_id=None):
        qs = Contribution.objects.select_related(
            "task__project", "author", "reviewed_by"
        )
        public = Q(status="accepted", task__project__status="published")
        if getattr(actor, "is_authenticated", False):
            public |= (
                Q(author=actor)
                | Q(task__project__owner=actor)
                | Q(
                    task__project__members__user=actor,
                    task__project__members__role="maintainer",
                )
            )
        qs = qs.filter(public).distinct().order_by("-id")
        if project_id is not None:
            qs = qs.filter(task__project_id=project_id)
        if task_id is not None:
            qs = qs.filter(task_id=task_id)
        if author_id is not None:
            qs = qs.filter(author_id=author_id)
        return qs

    def contribution(self, actor, pk, lock=False):
        obj = get_object_or_404(self.contributions(actor), pk=pk)
        if lock:
            return (
                Contribution.objects.select_for_update()
                .select_related("task__project")
                .get(pk=obj.pk)
            )
        return obj

    def create_contribution(self, task, actor, data):
        return Contribution.objects.create(task=task, author=actor, **data)

    def cached_analysis(self, key):
        return AIAnalysis.objects.filter(
            cache_key=key, status__in=["queued", "running", "succeeded"]
        ).first()

    def reserve_analysis(self, actor, project, data):
        # Verrouille le demandeur pour que deux projets simultanés partagent le même plafond.
        get_user_model().objects.select_for_update().get(pk=actor.pk)
        daily = AIAnalysis.objects.filter(
            requested_by=actor, created_at__date=timezone.now().date()
        ).count()
        project_daily = AIAnalysis.objects.filter(
            project=project, created_at__date=timezone.now().date()
        ).count()
        return daily, project_daily

    def create_analysis(self, actor, project, **data):
        return AIAnalysis.objects.create(project=project, requested_by=actor, **data)

    def analysis(self, actor, pk):
        obj = get_object_or_404(
            AIAnalysis.objects.select_related("project", "snapshot"), pk=pk
        )
        if not actor.is_authenticated or (
            obj.requested_by_id != actor.pk
            and not self.is_maintainer(obj.project, actor)
        ):
            from rest_framework.exceptions import NotFound

            raise NotFound()
        return obj

    def claim_job(self, job_id=None):
        jobs = AIAnalysis.objects.select_for_update(skip_locked=True).filter(status="queued")
        if job_id is not None:
            jobs = jobs.filter(pk=job_id)
        obj = jobs.order_by("id").first()
        if obj:
            self.save(obj, status="running", started_at=timezone.now())
        return obj

    def expire_jobs(self):
        from datetime import timedelta

        return AIAnalysis.objects.filter(
            status="running", started_at__lt=timezone.now() - timedelta(minutes=5)
        ).update(
            status="failed", error_code="worker_expired", finished_at=timezone.now()
        )

    def snapshot(self, repository, sha, sources, content_hash):
        return RepositorySnapshot.objects.get_or_create(
            repository=repository,
            commit_sha=sha,
            defaults={"sources": sources, "content_hash": content_hash},
        )[0]

    def discussion(self, key):
        return ProjectDiscussionLink.objects.filter(request_key=key).first()

    def create_discussion(self, **data):
        return ProjectDiscussionLink.objects.create(**data)

    def register_delivery(self, delivery_id):
        return WebhookDelivery.objects.get_or_create(delivery_id=delivery_id)[1]

    def repository_by_forge_id(self, forge_id):
        return Repository.objects.filter(gitea_repo_id=forge_id).first()
