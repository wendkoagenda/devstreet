"""Données géographiques des formulaires : villes d'un pays."""
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.core.services.geo_service import cities_for


@swagger_auto_schema(
    method='get',
    operation_description=(
        "Villes d'un pays (code ISO à 2 lettres) : grandes villes d'abord, puis la liste complète. "
        "`available` vaut false si aucune liste n'est disponible (le formulaire passe en saisie libre)."
    ),
    responses={200: "Villes du pays", 401: "Non authentifié"},
    tags=['Géographie'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def country_cities_view(request, country_code: str):
    """Liste des villes d'un pays, servie depuis le cache du serveur."""
    return Response(cities_for(country_code), status=status.HTTP_200_OK)
