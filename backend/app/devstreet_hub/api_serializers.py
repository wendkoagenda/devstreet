"""Contrats d'entrée/sortie des workflows, spécialisés au-delà du CRUD généré."""

from urllib.parse import quote
from rest_framework import serializers
from app.devstreet_hub.conf import config
from app.devstreet_hub.models import (
    Project,
    Technology,
    Repository,
    ContributionTask,
    Contribution,
    AIAnalysis,
    ProjectMember,
    ProjectDiscussionLink,
)
from app.devstreet_hub.repositories.workflow_repository import WorkflowRepository


class RepositorySerializer(serializers.ModelSerializer):
    clone_url = serializers.SerializerMethodField()
    browse_url = serializers.SerializerMethodField()
    is_empty = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = (
            "id",
            "status",
            "namespace",
            "name",
            "default_branch",
            "current_sha",
            "is_empty",
            "clone_url",
            "browse_url",
        )
        read_only_fields = fields

    def get_browse_url(self, obj):
        # URL technique pour dériver le clone ; l'UI Hub ne doit pas imposer
        # une visite de l'interface Gitea.
        url = config("GITEA_PUBLIC_URL", config("GITEA_URL")).rstrip("/")
        return (
            f"{url}/{quote(obj.namespace)}/{quote(obj.name)}"
            if url and obj.status == "ready"
            else None
        )

    def get_clone_url(self, obj):
        url = self.get_browse_url(obj)
        return url + ".git" if url else None

    def get_is_empty(self, obj):
        return obj.status == "ready" and not bool(obj.current_sha)


class ProjectQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True, max_length=200)
    technology = serializers.SlugField(required=False)
    owner = serializers.IntegerField(required=False, min_value=1)


class TaskQuerySerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=False, min_value=1)


class ContributionQuerySerializer(TaskQuerySerializer):
    task_id = serializers.IntegerField(required=False, min_value=1)
    author_id = serializers.IntegerField(required=False, min_value=1)


class ProjectWriteSerializer(serializers.ModelSerializer):
    technologies = serializers.PrimaryKeyRelatedField(
        queryset=Technology.objects.all(), many=True, required=False
    )
    slug = serializers.CharField(
        required=False, allow_blank=True, max_length=100
    )
    problem = serializers.CharField(
        required=False, allow_blank=True, max_length=2000
    )
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=10000
    )
    demo_url = serializers.URLField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "problem",
            "description",
            "demo_url",
            "declared_license",
            "technologies",
        )

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le titre ne peut pas être vide.")
        return value.strip()

    def validate_slug(self, value):
        from app.devstreet_hub.services.project_slug import (
            is_valid_slug,
            normalize_slug,
        )

        value = (value or "").strip()
        if not value:
            return ""
        slug = normalize_slug(value)
        if not is_valid_slug(slug):
            raise serializers.ValidationError("Slug invalide.")
        return slug

    def validate_declared_license(self, value):
        if value not in ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"):
            raise serializers.ValidationError(
                "Choisissez une licence permissive prise en charge pour ce MVP."
            )
        return value


class ProjectSetupSerializer(serializers.Serializer):
    """État d'orchestration renvoyé après création ou reprise."""

    draft = serializers.ChoiceField(choices=("ok",))
    identity = serializers.ChoiceField(
        choices=("pending", "ok", "failed", "conflict")
    )
    repository = serializers.ChoiceField(
        choices=("pending", "ok", "failed")
    )


class InitializeRepositorySerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=("readme", "push_existing"))


class InitializeRepositoryResponseSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=("readme", "push_existing"))
    initialized = serializers.BooleanField()
    is_empty = serializers.BooleanField()
    repository = RepositorySerializer()


class CodeQuerySerializer(serializers.Serializer):
    ref = serializers.CharField(required=False, allow_blank=True, max_length=255)
    path = serializers.CharField(required=False, allow_blank=True, max_length=500)


class CodeArchiveQuerySerializer(serializers.Serializer):
    ref = serializers.CharField(required=False, allow_blank=True, max_length=255)
    # Éviter `format` : réservé par DRF pour la négociation de contenu.
    archive_format = serializers.ChoiceField(
        choices=("zip", "tar.gz"), required=False, default="zip"
    )


class ProjectSerializer(serializers.ModelSerializer):
    repository = RepositorySerializer(read_only=True)
    star_count = serializers.SerializerMethodField()
    technologies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "owner_id",
            "title",
            "slug",
            "problem",
            "description",
            "demo_url",
            "declared_license",
            "status",
            "technologies",
            "star_count",
            "repository",
            "ai_consent_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_star_count(self, obj):
        if hasattr(obj, "star_count"):
            return obj.star_count
        return WorkflowRepository().star_count(obj)


class ProjectCreateResponseSerializer(ProjectSerializer):
    forge_access = serializers.DictField(required=False, allow_null=True)
    setup = ProjectSetupSerializer()


class TaskWriteSerializer(serializers.ModelSerializer):
    acceptance_criteria = serializers.ListField(
        child=serializers.CharField(max_length=500), max_length=10, required=False
    )

    class Meta:
        model = ContributionTask
        fields = ("title", "description", "acceptance_criteria")


class TaskUpdateSerializer(TaskWriteSerializer):
    class Meta(TaskWriteSerializer.Meta):
        fields = TaskWriteSerializer.Meta.fields + ("status",)


class TaskSerializer(serializers.ModelSerializer):
    source_references = serializers.SerializerMethodField()

    def get_source_references(self, obj):
        if not obj.analysis_id or not obj.analysis.snapshot_id:
            return []
        analysis = obj.analysis
        base = RepositorySerializer(analysis.snapshot.repository).data["browse_url"]
        return [
            {
                "source_id": source["source_id"],
                "path": source["path"],
                "commit_sha": analysis.commit_sha,
                "url": (
                    f"{base}/src/commit/{analysis.commit_sha}/{quote(source['path'], safe='/')}"
                    if base
                    else None
                ),
            }
            for source in analysis.snapshot.sources
        ]

    class Meta:
        model = ContributionTask
        fields = (
            "id",
            "project_id",
            "analysis_id",
            "title",
            "description",
            "acceptance_criteria",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            "source_references",
        )
        read_only_fields = fields


class ContributionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = ("summary", "pull_request_number", "artifact_sha")

    def validate_artifact_sha(self, value):
        import re

        if value and not re.fullmatch(r"[a-fA-F0-9]{40,64}", value):
            raise serializers.ValidationError("SHA de commit invalide.")
        return value


class ContributionSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(source="task.project_id", read_only=True)
    validation_kind = serializers.SerializerMethodField()

    class Meta:
        model = Contribution
        fields = (
            "id",
            "task_id",
            "project_id",
            "author_id",
            "summary",
            "pull_request_number",
            "artifact_sha",
            "status",
            "reviewed_by_id",
            "review_note",
            "reviewed_at",
            "created_at",
            "validation_kind",
        )
        read_only_fields = fields

    def get_validation_kind(self, obj):
        return "maintainer_review" if obj.status == "accepted" else None


class ReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=("accepted", "rejected"))
    note = serializers.CharField(max_length=3000)


class ConsentSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()


class MemberWriteSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    role = serializers.ChoiceField(choices=("maintainer", "contributor"))


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ("id", "user_id", "role")


class AnalysisRequestSerializer(serializers.Serializer):
    objective = serializers.CharField(max_length=2000)
    language = serializers.ChoiceField(choices=("fr", "en"), default="fr")


class AnalysisSerializer(serializers.ModelSerializer):
    sources = serializers.SerializerMethodField()

    class Meta:
        model = AIAnalysis
        fields = (
            "id",
            "project_id",
            "commit_sha",
            "objective",
            "language",
            "status",
            "model",
            "prompt_version",
            "result",
            "error_code",
            "input_tokens",
            "output_tokens",
            "sources",
            "created_at",
            "finished_at",
        )
        read_only_fields = fields

    def get_sources(self, obj):
        return (
            [
                {"source_id": s["source_id"], "path": s["path"]}
                for s in obj.snapshot.sources
            ]
            if obj.snapshot_id
            else []
        )


class AdoptSuggestionSerializer(serializers.Serializer):
    analysis_id = serializers.IntegerField(min_value=1)
    suggestion_index = serializers.IntegerField(min_value=0, max_value=2)


class DiscussionWriteSerializer(serializers.Serializer):
    request_key = serializers.UUIDField()
    task_id = serializers.IntegerField(required=False, min_value=1)
    title = serializers.CharField(max_length=180)
    body = serializers.CharField(max_length=5000)


class AssistantChatSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=8000)
    conversation_id = serializers.IntegerField(required=False, min_value=1)
    task_id = serializers.IntegerField(required=False, min_value=1)
    include_repo = serializers.BooleanField(required=False, default=True)


class DiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDiscussionLink
        fields = (
            "id",
            "project_id",
            "task_id",
            "forum_topic_id",
            "request_key",
            "title",
            "body",
            "created_at",
        )
