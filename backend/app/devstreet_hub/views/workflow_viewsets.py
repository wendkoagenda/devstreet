"""Routes de workflows. Les règles sont dans WorkflowService, l'auth reste celle du core."""

from django.db.models import Q
from django.http import HttpResponse, FileResponse, Http404
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from app.devstreet_hub.throttles import PublicProjectThrottle
from drf_yasg.utils import swagger_auto_schema, no_body
from drf_yasg import openapi
from app.devstreet_hub.api_serializers import (
    ProjectSerializer,
    ProjectWriteSerializer,
    ProjectCreateResponseSerializer,
    InitializeRepositorySerializer,
    InitializeRepositoryResponseSerializer,
    CodeArchiveQuerySerializer,
    CodeQuerySerializer,
    RepositorySerializer,
    TaskSerializer,
    TaskWriteSerializer,
    TaskUpdateSerializer,
    ContributionSerializer,
    ContributionWriteSerializer,
    ReviewSerializer,
    ConsentSerializer,
    MemberWriteSerializer,
    MemberSerializer,
    AnalysisRequestSerializer,
    AnalysisSerializer,
    AdoptSuggestionSerializer,
    DiscussionWriteSerializer,
    DiscussionSerializer,
    ForumPostWriteSerializer,
    ForumPostListQuerySerializer,
    ForumLinkedPublicationSerializer,
    AssistantChatSerializer,
)
from app.ai.serializers import AiChatResponseSerializer
from app.devstreet_hub.presentation_serializers import PresentationWriteSerializer, PresentationSuggestionSerializer
from app.devstreet_hub.services.presentation_service import PresentationService
from app.devstreet_hub.services.workflow_service import WorkflowService
from app.devstreet_hub.api_serializers import (
    ProjectQuerySerializer,
    TaskQuerySerializer,
    ContributionQuerySerializer,
)


def validated(serializer_class, data):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class ProjectViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    throttle_classes = [PublicProjectThrottle, UserRateThrottle]
    serializer_class = ProjectSerializer
    lookup_value_regex = "[0-9]+"
    swagger_tags = ["DevStreet Hub - Projets"]

    @swagger_auto_schema(query_serializer=ProjectQuerySerializer, tags=["V1 - Project"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        return (
            [IsAuthenticatedOrReadOnly()]
            if self.request.method in ("GET", "HEAD", "OPTIONS")
            else [IsAuthenticated()]
        )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return WorkflowService().repo.visible_projects(self.request.user).none()
        return WorkflowService().repo.visible_projects(
            self.request.user,
            **validated(ProjectQuerySerializer, self.request.query_params)
        )

    @swagger_auto_schema(
        request_body=ProjectWriteSerializer,
        responses={201: ProjectCreateResponseSerializer},
        tags=["V1 - Project"],
    )
    def create(self, request):
        result = WorkflowService().create_and_setup(
            request.user, validated(ProjectWriteSerializer, request.data)
        )
        data = ProjectSerializer(result["project"]).data
        data["setup"] = result["setup"]
        if result.get("forge_access") is not None:
            data["forge_access"] = result["forge_access"]
        return Response(data, status=201)

    @swagger_auto_schema(
        request_body=ProjectWriteSerializer,
        responses={200: ProjectSerializer},
        tags=["V1 - Project"],
    )
    def partial_update(self, request, pk=None):
        obj = self.get_object()
        serializer = ProjectWriteSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = WorkflowService().update_project(
            request.user, obj, serializer.validated_data
        )
        return Response(ProjectSerializer(obj).data)

    @swagger_auto_schema(
        method='put', request_body=no_body, responses={200: ProjectSerializer}, tags=['V1 - Project'],
        manual_parameters=[
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('problem', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('base_updated_at', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=True),
            openapi.Parameter('images', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Facultatif ; repeter ce champ pour joindre jusqu a quatre images.'),
            openapi.Parameter('remove_image_ids', openapi.IN_FORM, type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), collectionFormat='multi'),
        ],
    )
    @action(detail=True, methods=['put'], url_path='presentation', parser_classes=[MultiPartParser, FormParser])
    def presentation(self, request, pk=None):
        obj = self.get_object()
        obj = PresentationService().save(request.user, obj, validated(PresentationWriteSerializer, request.data))
        return Response(ProjectSerializer(obj).data)

    @swagger_auto_schema(method='post', request_body=PresentationSuggestionSerializer, responses={202: AnalysisSerializer}, tags=['V1 - Project'])
    @action(detail=True, methods=['post'], url_path='presentation/suggestions')
    def presentation_suggestion(self, request, pk=None):
        obj = PresentationService().suggest(request.user, self.get_object(), **validated(PresentationSuggestionSerializer, request.data))
        return Response(AnalysisSerializer(obj).data, status=202 if obj.status in ('queued', 'running') else 200)

    @swagger_auto_schema(method='get', responses={200: openapi.Response('Image JPEG protegee', schema=openapi.Schema(type=openapi.TYPE_FILE))}, tags=['V1 - Project'])
    @action(detail=True, methods=['get'], url_path=r'presentation/images/(?P<image_id>[0-9]+)')
    def presentation_image(self, request, pk=None, image_id=None):
        image = WorkflowService().repo.project_image(self.get_object(), image_id)
        try:
            response = FileResponse(image.file.open('rb'), content_type='image/jpeg')
        except (FileNotFoundError, OSError, ValueError):
            raise Http404('Image indisponible.')
        response['Cache-Control'] = 'private, no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response

    @swagger_auto_schema(
        method="post",
        request_body=ConsentSerializer,
        responses={200: ProjectSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["post"], url_path="ai-consent")
    def ai_consent(self, request, pk=None):
        obj = WorkflowService().consent(
            request.user,
            self.get_object(),
            **validated(ConsentSerializer, request.data)
        )
        return Response(ProjectSerializer(obj).data)

    @swagger_auto_schema(
        method="post",
        request_body=AssistantChatSerializer,
        responses={200: AiChatResponseSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["post"], url_path="assistant/chat")
    def assistant_chat(self, request, pk=None):
        result = WorkflowService().assistant_chat(
            request.user,
            self.get_object(),
            validated(AssistantChatSerializer, request.data),
        )
        return Response(AiChatResponseSerializer(result).data)

    @swagger_auto_schema(tags=["V1 - Project"], methods=["post"])
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        return Response(
            ProjectSerializer(
                WorkflowService().transition(
                    request.user, self.get_object(), "published"
                )
            ).data
        )

    @swagger_auto_schema(tags=["V1 - Project"], methods=["post"])
    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        return Response(
            ProjectSerializer(
                WorkflowService().transition(
                    request.user, self.get_object(), "archived"
                )
            ).data
        )

    @swagger_auto_schema(tags=["V1 - Project"], methods=["post"])
    @action(detail=True, methods=["post"])
    def provision(self, request, pk=None):
        obj = WorkflowService().provision_repository(request.user, self.get_object())
        return Response(RepositorySerializer(obj).data)

    @swagger_auto_schema(
        method="post",
        responses={200: ProjectCreateResponseSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["post"], url_path="setup")
    def setup(self, request, pk=None):
        """Reprend identité forge + dépôt après échec partiel (idempotent)."""
        result = WorkflowService().resume_setup(request.user, self.get_object())
        data = ProjectSerializer(result["project"]).data
        data["setup"] = result["setup"]
        if result.get("forge_access") is not None:
            data["forge_access"] = result["forge_access"]
        return Response(data)

    @swagger_auto_schema(
        method="post",
        request_body=InitializeRepositorySerializer,
        responses={200: InitializeRepositoryResponseSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["post"], url_path="initialize")
    def initialize(self, request, pk=None):
        result = WorkflowService().initialize_repository(
            request.user,
            self.get_object(),
            **validated(InitializeRepositorySerializer, request.data),
        )
        return Response(
            {
                "mode": result["mode"],
                "initialized": result["initialized"],
                "is_empty": result["is_empty"],
                "repository": RepositorySerializer(result["repository"]).data,
            }
        )

    @swagger_auto_schema(tags=["V1 - Project"], methods=["get"])
    @action(detail=True, methods=["get"])
    def repository(self, request, pk=None):
        return Response(RepositorySerializer(self.get_object().repository).data)

    @swagger_auto_schema(tags=["V1 - Project"], methods=["get"])
    @action(detail=True, methods=["get"], url_path="code/summary")
    def code_summary(self, request, pk=None):
        result = WorkflowService().code_summary(request.user, self.get_object())
        repository = result.pop("repository")
        result["repository"] = RepositorySerializer(repository).data
        return Response(result)

    @swagger_auto_schema(tags=["V1 - Project"], methods=["get"])
    @action(detail=True, methods=["get"], url_path="code/branches")
    def code_branches(self, request, pk=None):
        return Response(
            WorkflowService().code_branches(request.user, self.get_object())
        )

    @swagger_auto_schema(
        query_serializer=CodeQuerySerializer,
        tags=["V1 - Project"],
        methods=["get"],
    )
    @action(detail=True, methods=["get"], url_path="code/tree")
    def code_tree(self, request, pk=None):
        query = validated(CodeQuerySerializer, request.query_params)
        return Response(
            WorkflowService().code_tree(
                request.user,
                self.get_object(),
                ref=query.get("ref") or None,
                path=query.get("path") or None,
            )
        )

    @swagger_auto_schema(
        query_serializer=CodeQuerySerializer,
        tags=["V1 - Project"],
        methods=["get"],
    )
    @action(detail=True, methods=["get"], url_path="code/blob")
    def code_blob(self, request, pk=None):
        query = validated(CodeQuerySerializer, request.query_params)
        return Response(
            WorkflowService().code_blob(
                request.user,
                self.get_object(),
                ref=query.get("ref") or None,
                path=query.get("path") or None,
            )
        )

    @swagger_auto_schema(
        query_serializer=CodeArchiveQuerySerializer,
        tags=["V1 - Project"],
        methods=["get"],
    )
    @action(detail=True, methods=["get"], url_path="code/archive")
    def code_archive(self, request, pk=None):
        query = validated(CodeArchiveQuerySerializer, request.query_params)
        result = WorkflowService().code_archive(
            request.user,
            self.get_object(),
            ref=query.get("ref") or None,
            fmt=query.get("archive_format") or "zip",
        )
        response = HttpResponse(
            result["content"], content_type=result["content_type"]
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{result["filename"]}"'
        )
        response["Content-Length"] = str(len(result["content"]))
        return response

    @swagger_auto_schema(tags=["V1 - Project"], methods=["put", "delete"])
    @action(detail=True, methods=["put", "delete"])
    def star(self, request, pk=None):
        count = WorkflowService().star(
            request.user, self.get_object(), request.method == "PUT"
        )
        return Response({"starred": request.method == "PUT", "star_count": count})

    @swagger_auto_schema(
        method="post",
        request_body=MemberWriteSerializer,
        responses={200: MemberSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["get", "post"])
    def members(self, request, pk=None):
        project = self.get_object()
        service = WorkflowService()
        if request.method == "POST":
            obj = service.member(
                request.user, project, **validated(MemberWriteSerializer, request.data)
            )
            return Response(MemberSerializer(obj).data)
        return self.get_paginated_response(
            MemberSerializer(
                self.paginate_queryset(service.repo.members(project)), many=True
            ).data
        )

    @swagger_auto_schema(tags=["V1 - Project"], methods=["delete"])
    @action(detail=True, methods=["delete"], url_path="members/(?P<user_id>[0-9]+)")
    def remove_member(self, request, pk=None, user_id=None):
        WorkflowService().member(request.user, self.get_object(), int(user_id))
        return Response(status=204)

    @swagger_auto_schema(
        method="post",
        request_body=TaskWriteSerializer,
        responses={201: TaskSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["get", "post"])
    def tasks(self, request, pk=None):
        project = self.get_object()
        service = WorkflowService()
        if request.method == "POST":
            obj = service.create_task(
                request.user, project, validated(TaskWriteSerializer, request.data)
            )
            return Response(TaskSerializer(obj).data, status=201)
        qs = service.repo.visible_tasks(request.user, project_id=project.pk)
        status_counts = {
            "open": qs.filter(status="open").count(),
            "closed": qs.filter(status="closed").count(),
            "draft": qs.filter(status="draft").count(),
        }
        status_filter = (request.query_params.get("status") or "").strip().lower()
        if status_filter in ("open", "closed", "draft"):
            qs = qs.filter(status=status_filter)
        search = (
            request.query_params.get("search") or request.query_params.get("q") or ""
        ).strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        response = self.get_paginated_response(
            TaskSerializer(self.paginate_queryset(qs), many=True).data
        )
        response.data["status_counts"] = status_counts
        return response

    @swagger_auto_schema(
        method="post",
        request_body=AdoptSuggestionSerializer,
        responses={201: TaskSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["post"], url_path="tasks/from-analysis")
    def adopt_suggestion(self, request, pk=None):
        obj = WorkflowService().task_from_analysis(
            request.user,
            self.get_object(),
            **validated(AdoptSuggestionSerializer, request.data)
        )
        return Response(TaskSerializer(obj).data, status=201)

    @swagger_auto_schema(
        method="post",
        request_body=AnalysisRequestSerializer,
        responses={202: AnalysisSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["post"])
    def analyses(self, request, pk=None):
        obj = WorkflowService().request_analysis(
            request.user,
            self.get_object(),
            **validated(AnalysisRequestSerializer, request.data)
        )
        return Response(
            AnalysisSerializer(obj).data,
            status=200 if obj.status == "succeeded" else 202,
        )

    @swagger_auto_schema(
        method="post",
        request_body=DiscussionWriteSerializer,
        responses={201: DiscussionSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["post"])
    def discussions(self, request, pk=None):
        obj = WorkflowService().link_discussion(
            request.user,
            self.get_object(),
            validated(DiscussionWriteSerializer, request.data),
        )
        return Response(DiscussionSerializer(obj).data, status=201)

    @swagger_auto_schema(
        method="get",
        query_serializer=ForumPostListQuerySerializer,
        responses={200: ForumLinkedPublicationSerializer(many=True)},
        tags=["V1 - Project"],
    )
    @swagger_auto_schema(
        method="post",
        request_body=ForumPostWriteSerializer,
        responses={201: DiscussionSerializer},
        tags=["V1 - Project"],
    )
    @action(detail=True, methods=["get", "post"], url_path="forum-posts")
    def forum_posts(self, request, pk=None):
        project = self.get_object()
        service = WorkflowService()
        if request.method == "GET":
            query = validated(ForumPostListQuerySerializer, request.query_params)
            items = service.list_forum_posts(
                request.user, project, kind=query.get("kind")
            )
            page = self.paginate_queryset(items)
            serializer = ForumLinkedPublicationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        obj = service.link_forum_post(
            request.user,
            project,
            validated(ForumPostWriteSerializer, request.data),
        )
        return Response(DiscussionSerializer(obj).data, status=201)


class TaskViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    throttle_classes = [PublicProjectThrottle, UserRateThrottle]
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_value_regex = "[0-9]+"
    swagger_tags = ["DevStreet Hub - Contributions"]

    @swagger_auto_schema(query_serializer=TaskQuerySerializer, tags=["V1 - Task"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return WorkflowService().repo.visible_tasks(
            self.request.user,
            **validated(TaskQuerySerializer, self.request.query_params)
        )

    def get_permissions(self):
        return (
            [IsAuthenticatedOrReadOnly()]
            if self.request.method in ("GET", "HEAD", "OPTIONS")
            else [IsAuthenticated()]
        )

    @swagger_auto_schema(
        request_body=TaskUpdateSerializer,
        responses={200: TaskSerializer},
        tags=["V1 - Task"],
    )
    def partial_update(self, request, pk=None):
        task = self.get_object()
        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = WorkflowService().update_task(
            request.user, task, serializer.validated_data
        )
        return Response(TaskSerializer(obj).data)

    @swagger_auto_schema(
        method="post",
        request_body=ContributionWriteSerializer,
        responses={201: ContributionSerializer},
        tags=["V1 - Task"],
    )
    @action(detail=True, methods=["post"])
    def contributions(self, request, pk=None):
        obj = WorkflowService().submit(
            request.user,
            self.get_object(),
            validated(ContributionWriteSerializer, request.data),
        )
        return Response(ContributionSerializer(obj).data, status=201)


class ContributionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    throttle_classes = [PublicProjectThrottle, UserRateThrottle]
    serializer_class = ContributionSerializer
    lookup_value_regex = "[0-9]+"
    swagger_tags = ["DevStreet Hub - Contributions"]

    @swagger_auto_schema(
        query_serializer=ContributionQuerySerializer, tags=["V1 - Contribution"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        return (
            [IsAuthenticated()]
            if self.action == "review"
            else [IsAuthenticatedOrReadOnly()]
        )

    def get_queryset(self):
        return WorkflowService().repo.contributions(
            self.request.user,
            **validated(ContributionQuerySerializer, self.request.query_params)
        )

    @swagger_auto_schema(
        method="post",
        request_body=ReviewSerializer,
        responses={200: ContributionSerializer},
        tags=["V1 - Contribution"],
    )
    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        obj = WorkflowService().review(
            request.user, self.get_object(), **validated(ReviewSerializer, request.data)
        )
        return Response(ContributionSerializer(obj).data)


class AnalysisViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer
    lookup_value_regex = "[0-9]+"
    swagger_tags = ["DevStreet Hub - IA"]

    def get_queryset(self):
        return WorkflowService().repo.empty_analyses()

    @swagger_auto_schema(tags=["V1 - Analysis"])
    def retrieve(self, request, pk=None):
        return Response(
            AnalysisSerializer(WorkflowService().repo.analysis(request.user, pk)).data
        )


class ForgeAccessViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Identité Git, secret initial uniquement à la première création"
            )
        },
        tags=["V1 - ForgeAccess"],
    )
    def create(self, request):
        return Response(WorkflowService().provision_identity(request.user))

    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={
            200: openapi.Response(
                "Nouveau secret Git (une seule fois) ; login issu de la ForgeIdentity locale"
            )
        },
        tags=["V1 - ForgeAccess"],
    )
    @action(detail=False, methods=["post"], url_path="reset-password")
    def reset_password(self, request):
        """Réinitialise le mot de passe forge de l'utilisateur connecté uniquement."""
        # Tout login éventuel dans le body est ignoré volontairement.
        return Response(WorkflowService().reset_forge_password(request.user))
