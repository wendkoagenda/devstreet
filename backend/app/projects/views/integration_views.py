from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import throttle_classes
from app.projects.throttles import PublicProjectThrottle, GiteaWebhookThrottle
from app.projects.permissions.webhook import SignedGiteaWebhook
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.projects.api_serializers import ProjectSerializer, ContributionSerializer
from app.projects.repositories.workflow_repository import WorkflowRepository
from app.projects.services.integration_service import (
    receive_webhook,
    validate_application_evidence,
)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(type="object"),
    responses={200: "Livraison acceptée"},
    tags=["Chantier - Intégrations"],
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([SignedGiteaWebhook])
@throttle_classes([GiteaWebhookThrottle])
def webhook(request):
    return Response(
        receive_webhook(
            request.body,
            request.headers.get("X-Gitea-Signature", ""),
            request.headers.get("X-Gitea-Delivery", ""),
            request.headers.get("X-Gitea-Event", ""),
        )
    )


@swagger_auto_schema(
    method="get",
    responses={200: "Projets et réalisations publics du profil"},
    tags=["Chantier - Intégrations"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
@throttle_classes([PublicProjectThrottle])
def profile_projects(request, user_id):
    repo = WorkflowRepository()
    # Vue publique bornée ; les listes détaillées restent paginées sur leurs routes dédiées.
    projects = repo.visible_projects(request.user, owner=user_id).filter(
        status="published"
    )[:20]
    contributions = repo.public_evidence(user_id)[:20]
    return Response(
        {
            "user_id": user_id,
            "projects": ProjectSerializer(projects, many=True).data,
            "contributions": ContributionSerializer(contributions, many=True).data,
            "limit": 20,
        }
    )


@swagger_auto_schema(
    method="get",
    responses={200: ContributionSerializer},
    tags=["Chantier - Intégrations"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def evidence(request, contribution_id):
    return Response(
        ContributionSerializer(
            validate_application_evidence(request.user, contribution_id)
        ).data
    )
