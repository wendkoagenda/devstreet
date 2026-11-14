"""Vues du profil : calendrier de disponibilité, expériences, prestations et CV automatique."""
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.marketplace.cv_settings import COLOR_PRESETS, DEFAULTS, SECTIONS, merged_settings, validated_settings
from app.marketplace.market_serializers import (
    AvailabilityWriteSerializer,
    ExperienceWriteSerializer,
    PrestationWriteSerializer,
)
from app.marketplace.services.calendar_service import CalendarService, ExperienceService
from app.marketplace.services.cv_service import cv_data, cv_filename, get_cv_profil, render_cv_pdf
from app.marketplace.services.me_service import MeService
from app.marketplace.services.prestation_me_service import PrestationMeService
from app.marketplace.services.review_me_service import ReviewMeService


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


@swagger_auto_schema(method="get", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="post", tags=["V1 - Marketplace profil"])
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def my_prestations(request):
    """GET/POST /marketplace/me/prestations : mes services packagés (UC-14)."""
    if request.method == "POST":
        data = _valid(PrestationWriteSerializer, request)
        return Response(PrestationMeService.create(request.user, data), status=status.HTTP_201_CREATED)
    return Response(PrestationMeService.list_mine(request.user))


@swagger_auto_schema(method="patch", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="delete", tags=["V1 - Marketplace profil"])
@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def my_prestation(request, prestation_id):
    """PATCH/DELETE /marketplace/me/prestations/<id>."""
    if request.method == "DELETE":
        PrestationMeService.delete(request.user, prestation_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = _valid(PrestationWriteSerializer, request, partial=True)
    return Response(PrestationMeService.update(request.user, prestation_id, data))


def _preview_settings(request) -> dict:
    """
    Réglages de style passés dans l'adresse pour l'aperçu de mon CV (sans enregistrer), ex. `?color=bleu&font=serif`.
    `hidden_sections` est une liste séparée par des virgules (vide : tout afficher).
    """
    params = {key: request.query_params[key] for key in DEFAULTS if key in request.query_params}
    if "hidden_sections" in params:
        params["hidden_sections"] = [item for item in params["hidden_sections"].split(",") if item]
    return params


def _cv_response(request, profil_id):
    # Mon CV : profil dev obligatoire ; le CV d'un autre : le lecteur peut être un recruteur (profil entreprise)
    viewer = MeService.get_profil(request.user)
    if viewer is None and profil_id is not None:
        viewer = MeService.get_entreprise_profil(request.user)
    if viewer is None:
        raise PermissionDenied("Créez d'abord votre profil marketplace.")
    profil = get_cv_profil(profil_id, viewer)
    data = cv_data(profil)
    if profil.id == viewer.id:
        # Aperçu de mon propre CV avec des réglages pas encore enregistrés : le CV des autres suit toujours leurs réglages
        preview = _preview_settings(request)
        if preview:
            data["settings"] = validated_settings(preview, profil.cv_settings)
    response = HttpResponse(render_cv_pdf(data), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{cv_filename(data)}"'
    response["Cache-Control"] = "no-store"
    return response


@swagger_auto_schema(method="get", tags=["V1 - Marketplace profil"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_reviews_pending(request):
    """GET /marketplace/me/reviews/pending : missions acceptées à noter (UC-12)."""
    return Response(ReviewMeService.pending(request.user))


@swagger_auto_schema(method="get", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="post", tags=["V1 - Marketplace profil"])
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def my_reviews(request):
    """GET/POST /marketplace/me/reviews : avis déposés / dépôt d'un avis post-mission."""
    if request.method == "POST":
        data = {
            "candidature_id": request.data.get("candidature_id"),
            "rating": request.data.get("rating"),
            "comment": request.data.get("comment", ""),
            "is_public": request.data.get("is_public", True),
        }
        if data["rating"] is None:
            return Response({"rating": ["Ce champ est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data["rating"] = int(data["rating"])
        except (TypeError, ValueError):
            return Response({"rating": ["Note invalide."]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ReviewMeService.create(request.user, data), status=status.HTTP_201_CREATED)
    return Response(ReviewMeService.list_mine(request.user))


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


def _settings_payload(profil) -> dict:
    return {
        "settings": merged_settings(profil.cv_settings),
        "defaults": DEFAULTS,
        "presets": COLOR_PRESETS,
        "sections": list(SECTIONS),
    }


@swagger_auto_schema(method="get", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="patch", tags=["V1 - Marketplace profil"])
@swagger_auto_schema(method="delete", tags=["V1 - Marketplace profil"])
@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def my_cv_settings(request):
    """
    /marketplace/me/cv-settings : réglages de style de mon CV (couleur, police, mise en page…).
    GET les lit (avec les valeurs par défaut et les couleurs proposées), PATCH les enregistre, DELETE les réinitialise.
    """
    profil = MeService.get_profil(request.user)
    if profil is None:
        raise PermissionDenied("Créez d'abord votre profil marketplace.")
    if request.method == "PATCH":
        profil.cv_settings = validated_settings(request.data, profil.cv_settings)
        profil.updated_by = request.user.id
        profil.save(update_fields=["cv_settings", "updated_by", "updated_at"])
    elif request.method == "DELETE":
        profil.cv_settings = {}
        profil.updated_by = request.user.id
        profil.save(update_fields=["cv_settings", "updated_by", "updated_at"])
    return Response(_settings_payload(profil))
