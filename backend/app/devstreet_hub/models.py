import uuid
from app.devstreet_hub.image_storage import ProjectImageStorage

from django.contrib.auth import get_user_model
from django.db import models

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


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    file = models.FileField(storage=ProjectImageStorage(), upload_to='')
    display_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']


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


class GitDeviceAuthRequest(models.Model):
    """Demande d'autorisation CLI ↔ navigateur DevStreet (pas Gitea)."""

    STATUS_PENDING = "pending"
    STATUS_AUTHORIZED = "authorized"
    STATUS_DENIED = "denied"
    STATUS_EXPIRED = "expired"
    STATUS_CONSUMED = "consumed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_AUTHORIZED, "Autorisée"),
        (STATUS_DENIED, "Refusée"),
        (STATUS_EXPIRED, "Expirée"),
        (STATUS_CONSUMED, "Consommée"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="git_device_auth_requests",
    )
    computer_name = models.CharField(max_length=120)
    hub_base_url = models.URLField(max_length=400)
    code_challenge = models.CharField(max_length=128)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    grant_payload = models.TextField(blank=True, default="")
    poll_count = models.PositiveIntegerField(default=0)
    last_poll_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    decided_at = models.DateTimeField(null=True, blank=True)
    connected_computer = models.ForeignKey(
        "GitConnectedComputer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="auth_requests",
    )

    class Meta:
        db_table = "projects_git_device_auth_request"
        indexes = [
            models.Index(
                fields=["status", "expires_at"],
                name="projects_gi_status_3c8e2b_idx",
            ),
        ]


class GitConnectedComputer(models.Model):
    """Ordinateur autorisé : PAT Gitea réel lié à ForgeIdentity."""

    STATUS_ACTIVE = "active"
    STATUS_REVOKED = "revoked"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Actif"),
        (STATUS_REVOKED, "Révoqué"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="git_connected_computers"
    )
    name = models.CharField(max_length=120)
    forge_login = models.CharField(max_length=40)
    gitea_token_id = models.BigIntegerField()
    token_last_eight = models.CharField(max_length=8)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "projects_git_connected_computer"
        indexes = [
            models.Index(
                fields=["user", "status"],
                name="projects_gi_user_id_7f2a1c_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "gitea_token_id"],
                name="unique_user_gitea_token",
            )
        ]


class GitOAuthAuthorization(models.Model):
    """Demande OAuth2 (GCM) : confirmation navigateur DevStreet → code → PAT Gitea."""

    STATUS_PENDING = "pending"
    STATUS_AUTHORIZED = "authorized"
    STATUS_DENIED = "denied"
    STATUS_EXPIRED = "expired"
    STATUS_CONSUMED = "consumed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_AUTHORIZED, "Autorisée"),
        (STATUS_DENIED, "Refusée"),
        (STATUS_EXPIRED, "Expirée"),
        (STATUS_CONSUMED, "Consommée"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="git_oauth_authorizations",
    )
    client_id = models.CharField(max_length=80)
    redirect_uri = models.CharField(max_length=400)
    state = models.CharField(max_length=200, blank=True, default="")
    code_challenge = models.CharField(max_length=128)
    code_challenge_method = models.CharField(max_length=10, default="S256")
    scope = models.CharField(max_length=200, blank=True, default="")
    computer_name = models.CharField(max_length=120, default="Git Credential Manager")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    authorization_code = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    decided_at = models.DateTimeField(null=True, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)
    connected_computer = models.ForeignKey(
        "GitConnectedComputer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="oauth_authorizations",
    )

    class Meta:
        db_table = "projects_git_oauth_authorization"
        indexes = [
            models.Index(
                fields=["status", "expires_at"],
                name="projects_gi_oauth_st_idx",
            ),
            models.Index(
                fields=["authorization_code"],
                name="projects_gi_oauth_code_idx",
            ),
        ]
