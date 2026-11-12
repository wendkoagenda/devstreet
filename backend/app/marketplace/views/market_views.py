"""Vues des écrans utilisateur : offres, candidatures, compétences (tout utilisateur connecté, règles dans le service)."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.marketplace.market_serializers import (
    ApplySerializer,
    DecisionSerializer,
    OfferWriteSerializer,
    ProfilSkillsSerializer,
)
from app.marketplace.services.market_service import MarketService


def _valid(serializer_class, request, partial=False):
    serializer = serializer_class(data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skills_list(request):
    """GET /marketplace/skills?search= : référentiel des compétences."""
    return Response(MarketService.list_skills(request.query_params.get("search")))


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def my_skills(request):
    """GET/PUT /marketplace/me/skills : compétences du profil (PUT remplace la liste)."""
    if request.method == "PUT":
        data = _valid(ProfilSkillsSerializer, request)
        return Response(MarketService.set_my_skills(request.user, [dict(item) for item in data["skills"]]))
    return Response(MarketService.get_my_skills(request.user))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def offers_list(request):
    """GET /marketplace/offers : offres ouvertes, triées par score pour l'utilisateur."""
    params = request.query_params
    return Response(
        MarketService.list_open_offers(request.user, params.get("search"), params.get("type"), params.get("work_mode"))
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def offer_detail(request, offer_id):
    """GET /marketplace/offers/<id> : fiche d'une offre avec le détail du score."""
    return Response(MarketService.get_offer(request.user, offer_id))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def offer_apply(request, offer_id):
    """POST /marketplace/offers/<id>/apply : postuler à une offre."""
    data = _valid(ApplySerializer, request)
    return Response(MarketService.apply(request.user, offer_id, data["message"]), status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_candidatures(request):
    """GET /marketplace/me/candidatures : mes candidatures avec leur offre."""
    return Response(MarketService.my_candidatures(request.user))


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def my_offers(request):
    """GET/POST /marketplace/me/offers : offres de mon entreprise (recruteur)."""
    if request.method == "POST":
        data = _valid(OfferWriteSerializer, request)
        return Response(MarketService.create_offer(request.user, dict(data)), status=status.HTTP_201_CREATED)
    return Response(MarketService.my_offers(request.user))


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def my_offer_detail(request, offer_id):
    """GET/PATCH /marketplace/me/offers/<id> : lire ou modifier (dont changer le statut) une offre de mon entreprise."""
    if request.method == "PATCH":
        data = _valid(OfferWriteSerializer, request, partial=True)
        return Response(MarketService.update_offer(request.user, offer_id, dict(data)))
    return Response(MarketService.get_my_offer(request.user, offer_id))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def offer_candidatures(request, offer_id):
    """GET /marketplace/me/offers/<id>/candidatures : candidatures reçues, triées par score."""
    return Response(MarketService.offer_candidatures(request.user, offer_id))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def offer_recommended_profils(request, offer_id):
    """GET /marketplace/me/offers/<id>/recommended-profils : talents classés par score pour l'offre."""
    return Response(MarketService.recommended_profils(request.user, offer_id))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def candidature_decision(request, candidature_id):
    """POST /marketplace/candidatures/<id>/decision : présélectionner, refuser ou accepter."""
    data = _valid(DecisionSerializer, request)
    return Response(MarketService.decide(request.user, candidature_id, data["status"]))
