"""API d'autorisation Git navigateur (DevStreet) pour le CLI local."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from drf_yasg.utils import swagger_auto_schema

from app.core.pagination import StandardPagination
from app.devstreet_hub.api_serializers_git_auth import (
    GitConnectedComputerSerializer,
    GitDevicePollSerializer,
    GitDeviceRequestSerializer,
    GitDeviceStartSerializer,
)
from app.devstreet_hub.services.git_auth_service import GitAuthService


def validated(serializer_class, data):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class GitDeviceAuthThrottle(AnonRateThrottle):
    rate = "30/minute"


class GitAuthViewSet(viewsets.ViewSet):
    """Parcours device-auth : start/poll publics ; authorize/deny authentifiés."""

    swagger_tags = ["DevStreet Hub - Git Auth"]
    lookup_value_regex = r"[0-9a-fA-F-]{36}"

    def get_permissions(self):
        if self.action in ("start", "poll", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_throttles(self):
        if self.action in ("start", "poll"):
            return [GitDeviceAuthThrottle()]
        return [UserRateThrottle()]

    @swagger_auto_schema(
        method="post",
        request_body=GitDeviceStartSerializer,
        tags=["V1 - GitAuth"],
    )
    @action(detail=False, methods=["post"], url_path="device/start")
    def start(self, request):
        data = validated(GitDeviceStartSerializer, request.data)
        result = GitAuthService().start_device_auth(**data)
        return Response(result, status=201)

    @swagger_auto_schema(
        responses={200: GitDeviceRequestSerializer},
        tags=["V1 - GitAuth"],
    )
    def retrieve(self, request, pk=None):
        return Response(GitAuthService().get_request_public(pk))

    @swagger_auto_schema(
        method="post",
        request_body=GitDevicePollSerializer,
        tags=["V1 - GitAuth"],
    )
    @action(detail=True, methods=["post"], url_path="poll")
    def poll(self, request, pk=None):
        data = validated(GitDevicePollSerializer, request.data)
        result = GitAuthService().poll(request_id=pk, **data)
        return Response(result)

    @swagger_auto_schema(method="post", tags=["V1 - GitAuth"])
    @action(detail=True, methods=["post"], url_path="authorize")
    def authorize(self, request, pk=None):
        result = GitAuthService().authorize(request.user, pk)
        return Response(result)

    @swagger_auto_schema(method="post", tags=["V1 - GitAuth"])
    @action(detail=True, methods=["post"], url_path="deny")
    def deny(self, request, pk=None):
        result = GitAuthService().deny(request.user, pk)
        return Response(result)


class GitConnectedComputerViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    swagger_tags = ["DevStreet Hub - Git Auth"]

    @swagger_auto_schema(tags=["V1 - GitConnectedComputer"])
    def list(self, request):
        qs = GitAuthService().list_computers(request.user)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        serializer = GitConnectedComputerSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(tags=["V1 - GitConnectedComputer"])
    def destroy(self, request, pk=None):
        GitAuthService().revoke_computer(request.user, int(pk))
        return Response(status=204)
