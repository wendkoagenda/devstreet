"""Endpoints OAuth2 publics pour Git Credential Manager (PKCE)."""

import logging

from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from app.devstreet_hub.services.errors import Conflict, ExternalUnavailable
from app.devstreet_hub.services.git_oauth_service import GitOAuthService
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


logger = logging.getLogger(__name__)

# Messages génériques : le détail des exceptions reste dans les journaux serveur.
MESSAGE_SERVICE_INDISPONIBLE = "Service Git indisponible ou non configuré."
MESSAGE_DEMANDE_NON_ECHANGEABLE = "La demande d'autorisation ne peut pas être échangée."


class GitOAuthThrottle(AnonRateThrottle):
    rate = "60/minute"


class GitOAuthViewSet(viewsets.ViewSet):
    """authorize (redirect) + token (GCM) ; approve/deny authentifiés."""

    swagger_tags = ["DevStreet Hub - Git OAuth"]
    lookup_value_regex = r"[0-9a-fA-F-]{36}"
    authentication_classes_token = []

    def get_permissions(self):
        if self.action in ("authorize", "token", "client_config", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_throttles(self):
        if self.action in ("authorize", "token"):
            return [GitOAuthThrottle()]
        return [UserRateThrottle()]

    def get_authenticators(self):
        # Le POST token de GCM n'envoie pas de session Django.
        if getattr(self, "action", None) == "token" or self.request.path.endswith(
            "/git-oauth/token"
        ):
            return []
        return super().get_authenticators()

    @swagger_auto_schema(tags=["V1 - GitOAuth"])
    @action(detail=False, methods=["get"], url_path="client-config")
    def client_config(self, request):
        try:
            return Response(GitOAuthService().client_config())
        except ExternalUnavailable:
            logger.exception("Configuration OAuth Git indisponible")
            return Response({"detail": MESSAGE_SERVICE_INDISPONIBLE}, status=503)

    @swagger_auto_schema(tags=["V1 - GitOAuth"])
    @action(detail=False, methods=["get"], url_path="authorize")
    def authorize(self, request):
        try:
            started = GitOAuthService().start_authorize(request.query_params.dict())
        except ValidationError as error:
            return Response(error.detail, status=400)
        except ExternalUnavailable:
            logger.exception("Démarrage de l'autorisation OAuth Git impossible")
            return Response({"detail": MESSAGE_SERVICE_INDISPONIBLE}, status=503)
        return redirect(started["confirm_url"])

    @swagger_auto_schema(tags=["V1 - GitOAuth"])
    @action(detail=False, methods=["post"], url_path="token")
    def token(self, request):
        # GCM envoie application/x-www-form-urlencoded ou JSON.
        data = request.data
        if hasattr(data, "dict"):
            data = data.dict()
        try:
            payload = GitOAuthService().exchange_token(data)
            return Response(payload)
        except ValidationError as error:
            detail = error.detail
            if isinstance(detail, dict) and "error" in detail:
                return Response(detail, status=400)
            return Response({"error": "invalid_request", "error_description": detail}, status=400)
        except PermissionDenied:
            return Response({"error": "invalid_grant"}, status=400)
        except Conflict:
            logger.warning("Échange de jeton OAuth Git refusé (conflit)", exc_info=True)
            return Response(
                {
                    "error": "server_error",
                    "error_description": MESSAGE_DEMANDE_NON_ECHANGEABLE,
                },
                status=409,
            )
        except ExternalUnavailable:
            logger.exception("Échange de jeton OAuth Git impossible")
            return Response(
                {
                    "error": "temporarily_unavailable",
                    "error_description": MESSAGE_SERVICE_INDISPONIBLE,
                },
                status=503,
            )

    @swagger_auto_schema(tags=["V1 - GitOAuth"])
    def retrieve(self, request, pk=None):
        try:
            return Response(GitOAuthService().get_public(pk))
        except NotFound:
            raise

    @swagger_auto_schema(tags=["V1 - GitOAuth"])
    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        result = GitOAuthService().approve(request.user, pk)
        return Response(result)

    @swagger_auto_schema(tags=["V1 - GitOAuth"])
    @action(detail=True, methods=["post"], url_path="deny")
    def deny(self, request, pk=None):
        result = GitOAuthService().deny(request.user, pk)
        return Response(result)
