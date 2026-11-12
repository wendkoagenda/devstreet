from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ContributionTask(models.Model):
    """
    ContributionTask model.
    """

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="tasks"
    )
    analysis = models.ForeignKey(
        "AIAnalysis",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
    )
    acceptance_criteria = models.JSONField(default=list)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        default="draft",
        choices=[("draft", "Brouillon"), ("open", "Ouverte"), ("closed", "Fermée")],
    )
    created_by = models.IntegerField(
        verbose_name="Créé par", help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par", help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création", auto_now_add=True, auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification", auto_now_add=False, auto_now=True
    )

    class Meta:
        db_table = "projects_contribution_task"
        verbose_name = "Tâche de contribution"
        verbose_name_plural = "Tâches de contribution"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return f"/projects/contribution-tasks/{self.id}/"


class Project(models.Model):
    """
    Project model.
    """

    owner = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="chantier_projects"
    )
    ai_consent_at = models.DateTimeField(null=True, blank=True)
    technologies = models.ManyToManyField(
        "Technology", through="ProjectTechnology", related_name="projects"
    )
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=100, unique=True)
    problem = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    demo_url = models.URLField(blank=True, default="")
    declared_license = models.CharField(max_length=50, default="MIT")
    status = models.CharField(
        max_length=20,
        default="draft",
        choices=[
            ("draft", "Brouillon"),
            ("published", "Publié"),
            ("archived", "Archivé"),
        ],
    )
    created_by = models.IntegerField(
        verbose_name="Créé par", help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par", help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création", auto_now_add=True, auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification", auto_now_add=False, auto_now=True
    )

    class Meta:
        db_table = "projects_project"
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return f"/projects/projects/{self.id}/"


class Technology(models.Model):
    """
    Technology model.
    """

    label = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)
    created_by = models.IntegerField(
        verbose_name="Créé par", help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par", help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création", auto_now_add=True, auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification", auto_now_add=False, auto_now=True
    )

    class Meta:
        db_table = "projects_technology"
        verbose_name = "Technologie"
        verbose_name_plural = "Technologies"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.label}"

    def get_absolute_url(self):
        return f"/projects/technologies/{self.id}/"


class ProjectTechnology(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    technology = models.ForeignKey(Technology, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "technology"], name="unique_project_technology"
            )
        ]


class ProjectMember(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chantier_memberships"
    )
    role = models.CharField(
        max_length=20,
        choices=[("maintainer", "Mainteneur"), ("contributor", "Contributeur")],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="unique_project_member"
            )
        ]


class Star(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="stars")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chantier_stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="unique_project_star"
            )
        ]


class ForgeIdentity(models.Model):
    """Liaison explicite Django ↔ Gitea. Le login opaque n'est jamais une preuve d'appartenance seul."""

    STATUS_PENDING = "pending"
    STATUS_LINKED = "linked"
    STATUS_CONFLICT = "conflict"
    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente de confirmation distante"),
        (STATUS_LINKED, "Liée"),
        (STATUS_CONFLICT, "Conflit — réparation administrative"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, related_name="forge_identity"
    )
    login = models.CharField(max_length=40, unique=True)
    # Null tant que la création distante n'est pas confirmée et liée.
    gitea_user_id = models.BigIntegerField(unique=True, null=True, blank=True)
    # Clé opaque persistée avant l'appel Gitea ; sert de preuve de corrélation.
    provisioning_key = models.UUIDField(unique=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    conflict_reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    linked_at = models.DateTimeField(null=True, blank=True)


class Repository(models.Model):
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="repository"
    )
    gitea_repo_id = models.BigIntegerField(null=True, unique=True)
    namespace = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    default_branch = models.CharField(max_length=100, default="main")
    current_sha = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[("pending", "En attente"), ("ready", "Prêt"), ("failed", "Échec")],
    )


class RepositorySnapshot(models.Model):
    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name="snapshots"
    )
    commit_sha = models.CharField(max_length=64)
    content_hash = models.CharField(max_length=64)
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["repository", "commit_sha"], name="unique_repository_sha"
            )
        ]


class AIAnalysis(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="analyses"
    )
    snapshot = models.ForeignKey(
        RepositorySnapshot, null=True, on_delete=models.PROTECT, related_name="analyses"
    )
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT)
    objective = models.TextField()
    language = models.CharField(max_length=2, default="fr")
    commit_sha = models.CharField(max_length=64)
    cache_key = models.CharField(max_length=64, db_index=True)
    status = models.CharField(
        max_length=20,
        default="queued",
        choices=[
            ("queued", "En attente"),
            ("running", "En cours"),
            ("succeeded", "Terminée"),
            ("failed", "Échec"),
        ],
    )
    model = models.CharField(max_length=100)
    prompt_version = models.CharField(max_length=30, default="contribution-v1")
    result = models.JSONField(default=dict)
    error_code = models.CharField(max_length=50, blank=True)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cache_key"],
                condition=models.Q(status__in=["queued", "running", "succeeded"]),
                name="unique_live_analysis_cache",
            )
        ]


class Contribution(models.Model):
    task = models.ForeignKey(
        ContributionTask, on_delete=models.PROTECT, related_name="contributions"
    )
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="chantier_contributions"
    )
    summary = models.TextField()
    pull_request_number = models.PositiveIntegerField(null=True, blank=True)
    artifact_sha = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=20,
        default="submitted",
        choices=[
            ("submitted", "Soumise"),
            ("accepted", "Acceptée"),
            ("rejected", "Refusée"),
        ],
    )
    reviewed_by = models.ForeignKey(
        User, null=True, on_delete=models.PROTECT, related_name="chantier_reviews"
    )
    review_note = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(author=models.F("reviewed_by")),
                name="contribution_no_self_review",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status="submitted",
                    reviewed_by__isnull=True,
                    reviewed_at__isnull=True,
                )
                | (
                    models.Q(
                        status__in=["accepted", "rejected"],
                        reviewed_by__isnull=False,
                        reviewed_at__isnull=False,
                    )
                    & ~models.Q(review_note="")
                ),
                name="contribution_review_complete",
            ),
        ]


class ProjectDiscussionLink(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="discussions"
    )
    task = models.ForeignKey(ContributionTask, null=True, on_delete=models.SET_NULL)
    forum_topic_id = models.CharField(max_length=100, unique=True)
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT)
    request_key = models.UUIDField(unique=True)
    title = models.CharField(max_length=180)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class WebhookDelivery(models.Model):
    delivery_id = models.CharField(max_length=100, unique=True)
    received_at = models.DateTimeField(auto_now_add=True)
