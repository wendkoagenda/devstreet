"""Vues « mon espace marketplace » : profil et entreprise de l'utilisateur connecté."""
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.marketplace.serializers import (
    CompanySerializer,
    MeCompanyWriteSerializer,
    MeProfilWriteSerializer,
    ProfilSerializer,
)
from app.marketplace.services.me_service import MeService


def _space_response(user, http_status=status.HTTP_200_OK):
    """Réponse commune : profil et entreprise de l'utilisateur (null si absents)."""
    profil, company = MeService.get_space(user)
    return Response(
        {
            "profil": ProfilSerializer(profil).data if profil else None,
            "company": CompanySerializer(company).data if company else None,
        },
        status=http_status,
    )


def _error(exc: ValidationError):
    return Response({"error": " ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """GET /marketplace/me : profil et entreprise de l'utilisateur."""

    permission_classes = [IsAuthenticated]
    swagger_tags = ["V1 - Mon espace"]

    def get(self, request):
        return _space_response(request.user)


class MeProfilView(APIView):
    """POST /marketplace/me/profil (création) et PATCH (mise à jour) du profil de l'utilisateur."""

    permission_classes = [IsAuthenticated]
    swagger_tags = ["V1 - Mon espace"]

    def post(self, request):
        serializer = MeProfilWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            MeService.create_profil(request.user, serializer.validated_data)
        except ValidationError as exc:
            return _error(exc)
        return _space_response(request.user, status.HTTP_201_CREATED)

    def patch(self, request):
        serializer = MeProfilWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if MeService.update_profil(request.user, serializer.validated_data) is None:
            return Response({"error": "Profil non trouvé"}, status=status.HTTP_404_NOT_FOUND)
        return _space_response(request.user)


class MeCompanyView(APIView):
    """POST /marketplace/me/company (création, rattachée au profil) et PATCH (mise à jour) de l'entreprise."""

    permission_classes = [IsAuthenticated]
    swagger_tags = ["V1 - Mon espace"]

    def post(self, request):
        serializer = MeCompanyWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            MeService.create_company(request.user, serializer.validated_data)
        except ValidationError as exc:
            return _error(exc)
        return _space_response(request.user, status.HTTP_201_CREATED)

    def patch(self, request):
        serializer = MeCompanyWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            company = MeService.update_company(request.user, serializer.validated_data)
        except ValidationError as exc:
            return Response({"error": " ".join(exc.messages)}, status=status.HTTP_403_FORBIDDEN)
        if company is None:
            return Response({"error": "Entreprise non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        return _space_response(request.user)
