from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.devstreet_hub.views.workflow_viewsets import (
    ProjectViewSet,
    TaskViewSet,
    ContributionViewSet,
    AnalysisViewSet,
    ForgeAccessViewSet,
)
from app.devstreet_hub.views.integration_views import (
    webhook,
    profile_projects,
    evidence,
)
from app.devstreet_hub.views.technology_viewset import TechnologyViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"contribution-tasks", TaskViewSet, basename="contribution-tasks")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"technologies", TechnologyViewSet, basename="technologies")
router.register(r"contributions", ContributionViewSet, basename="contributions")
router.register(r"analyses", AnalysisViewSet, basename="analyses")
router.register(r"forge-access", ForgeAccessViewSet, basename="forge-access")

urlpatterns = [
    path("v1/integrations/gitea/webhook", webhook, name="gitea-webhook"),
    path("v1/project-profiles/<int:user_id>", profile_projects, name="project-profile"),
    path(
        "v1/project-evidence/<int:contribution_id>", evidence, name="project-evidence"
    ),
    path("v1/", include(router.urls)),
]

app_name = "devstreet_hub"
