"""Workflow spécialisé après génération CRUD."""

from app.devstreet_hub.views.workflow_viewsets import (
    TaskViewSet as ContributionTaskViewSet,
)

__all__ = ["ContributionTaskViewSet"]
