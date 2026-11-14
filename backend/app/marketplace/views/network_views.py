"""Vues de découverte : paquet de cartes, swipes, vivier, connexions et fiche publique d'un profil."""
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.marketplace.services.network_service import NetworkService


class SwipeInputSerializer(serializers.Serializer):
    target_id = serializers.IntegerField()
    direction = serializers.ChoiceField(choices=["like", "pass"])
    context = serializers.ChoiceField(choices=["recruit", "network"])
    # Profil avec lequel on agit dans le réseau (sinon : le profil dev, ou à défaut le profil entreprise)
    acting = serializers.ChoiceField(choices=["dev", "entreprise"], required=False)


def _context(request) -> str:
    return request.query_params.get("context", "")


def _acting(request):
    return request.query_params.get("acting") or None


@swagger_auto_schema(method="get", tags=["V1 - Marketplace réseau"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def deck(request):
    """GET /marketplace/me/deck?context=recruit|network : profils à découvrir."""
    return Response(NetworkService.deck(request.user, _context(request), _acting(request)))


@swagger_auto_schema(method="post", tags=["V1 - Marketplace réseau"])
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def swipe(request):
    """POST /marketplace/me/swipes : like ou passe ; la réponse indique une connexion créée (`matched`)."""
    serializer = SwipeInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    result = NetworkService.swipe(
        request.user, data["target_id"], data["direction"], data["context"], data.get("acting")
    )
    return Response(result, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method="delete", tags=["V1 - Marketplace réseau"])
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def undo_swipe(request):
    """DELETE /marketplace/me/swipes/last?context= : annule le dernier choix du contexte."""
    return Response(NetworkService.undo_last_swipe(request.user, _context(request), _acting(request)))


@swagger_auto_schema(method="get", tags=["V1 - Marketplace réseau"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def network_requests(request):
    """GET /marketplace/me/network-requests : demandes de connexion envoyées en attente et demandes reçues."""
    return Response(NetworkService.requests(request.user))


@swagger_auto_schema(method="get", tags=["V1 - Marketplace réseau"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pool(request):
    """GET /marketplace/me/pool : vivier de talents de mon entreprise."""
    return Response(NetworkService.pool(request.user))


@swagger_auto_schema(method="get", tags=["V1 - Marketplace réseau"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def talents_directory(request):
    """GET /marketplace/talents : annuaire filtrable (compétence, pays, dispo, remote) — UC-08."""
    return Response(
        NetworkService.search_talents(
            request.user,
            {
                "search": request.query_params.get("search"),
                "skill": request.query_params.get("skill"),
                "country": request.query_params.get("country"),
                "remote": request.query_params.get("remote"),
                "available": request.query_params.get("available"),
            },
        )
    )


@swagger_auto_schema(method="get", tags=["V1 - Marketplace réseau"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def connections(request):
    """GET /marketplace/me/connections : mes connexions."""
    return Response(NetworkService.connections(request.user))


@swagger_auto_schema(method="get", tags=["V1 - Marketplace réseau"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def public_profile(request, profil_id):
    """GET /marketplace/profils/<id> : fiche d'un profil (expériences, compétences, avis publics)."""
    return Response(NetworkService.public_profile(request.user, profil_id))
