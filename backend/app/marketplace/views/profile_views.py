"""Vues du profil : calendrier de disponibilité, expériences et CV automatique."""
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.marketplace.market_serializers import AvailabilityWriteSerializer, ExperienceWriteSerializer
from app.marketplace.services.calendar_service import CalendarService, ExperienceService
from app.marketplace.services.cv_service import cv_data, cv_filename, get_cv_profil, render_cv_pdf
from app.marketplace.services.me_service import MeService


def _valid(serializer_class, request, partial=False):
    serializer = serializer_class(data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    return dict(serializer.validated_data)


@swagger_auto_schema(method="get", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="post", tags=["V1 - Marketplace profil"])
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def my_availabilities(request):
    """GET/POST /marketplace/me/availabilities : mes périodes de disponibilité."""
    if request.method == "POST":
        data = _valid(AvailabilityWriteSerializer, request)
        return Response(CalendarService.create(request.user, data), status=status.HTTP_201_CREATED)
    return Response(CalendarService.list_mine(request.user))


@swagger_auto_schema(method="patch", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="delete", tags=["V1 - Marketplace profil"])
@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def my_availability(request, availability_id):
    """PATCH/DELETE /marketplace/me/availabilities/<id> : modifier ou supprimer une période saisie à la main."""
    if request.method == "DELETE":
        CalendarService.delete(request.user, availability_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = _valid(AvailabilityWriteSerializer, request, partial=True)
    return Response(CalendarService.update(request.user, availability_id, data))


@swagger_auto_schema(method="get", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="post", tags=["V1 - Marketplace profil"])
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def my_experiences(request):
    """GET/POST /marketplace/me/experiences : mes expériences professionnelles."""
    if request.method == "POST":
        data = _valid(ExperienceWriteSerializer, request)
        return Response(ExperienceService.create(request.user, data), status=status.HTTP_201_CREATED)
    return Response(ExperienceService.list_mine(request.user))


@swagger_auto_schema(method="patch", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="delete", tags=["V1 - Marketplace profil"])
@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def my_experience(request, experience_id):
    """PATCH/DELETE /marketplace/me/experiences/<id>."""
    if request.method == "DELETE":
        ExperienceService.delete(request.user, experience_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = _valid(ExperienceWriteSerializer, request, partial=True)
    return Response(ExperienceService.update(request.user, experience_id, data))


def _cv_response(request, profil_id):
    viewer = MeService.get_profil(request.user)
    if viewer is None:
        raise PermissionDenied("Créez d'abord votre profil marketplace.")
    data = cv_data(get_cv_profil(profil_id, viewer))
    response = HttpResponse(render_cv_pdf(data), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{cv_filename(data)}"'
    response["Cache-Control"] = "no-store"
    return response


@swagger_auto_schema(method="get", tags=["V1 - Marketplace profil"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_cv(request):
    """GET /marketplace/me/cv : mon CV automatique en PDF."""
    return _cv_response(request, None)


@swagger_auto_schema(method="get", tags=["V1 - Marketplace profil"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profil_cv(request, profil_id):
    """GET /marketplace/profils/<id>/cv : CV d'un profil en PDF, selon sa visibilité (public, entreprises, privé)."""
    return _cv_response(request, profil_id)
