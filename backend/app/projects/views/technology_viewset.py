"""CRUD généré spécialisé : validation DRF et IAM existant conservés."""

from django.db.models.deletion import ProtectedError
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from app.projects.serializers import TechnologySerializer
from app.projects.services.technology_service import TechnologyService
from app.projects.services.errors import Conflict
from app.projects.permissions.technology_permissions import (
    CanCreateTechnology,
    CanUpdateTechnology,
    CanDeleteTechnology,
)


class TechnologyViewSet(viewsets.ModelViewSet):
    serializer_class = TechnologySerializer
    lookup_value_regex = "[0-9]+"
    swagger_tags = ["Chantier - Technologies"]

    def get_permissions(self):
        cls = {
            "create": CanCreateTechnology,
            "update": CanUpdateTechnology,
            "partial_update": CanUpdateTechnology,
            "destroy": CanDeleteTechnology,
        }.get(self.action, AllowAny)
        return [cls()]

    def get_queryset(self):
        try:
            return TechnologyService().get_all(
                search=self.request.query_params.get("search"),
                ordering=self.request.query_params.get("ordering"),
            )
        except ValueError as error:
            raise ValidationError("Tri invalide.") from error

    def perform_create(self, serializer):
        serializer.instance = TechnologyService().create(
            {
                **serializer.validated_data,
                "created_by": self.request.user.pk,
                "updated_by": self.request.user.pk,
            }
        )

    def perform_update(self, serializer):
        serializer.instance = TechnologyService().update(
            serializer.instance.pk,
            {**serializer.validated_data, "updated_by": self.request.user.pk},
            partial=serializer.partial,
        )

    def perform_destroy(self, instance):
        try:
            TechnologyService().delete(instance.pk)
        except ProtectedError as error:
            raise Conflict("Cette technologie est utilisée par un projet.") from error
