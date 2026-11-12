"""
Route de santé : utilisée par les vérifications de santé Docker et par le contrôle de bout en bout du déploiement.
"""
import logging

from django.db import connection
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.core.throttles import HealthThrottle

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='get',
    operation_description="Santé de l'application : 200 si Django répond et que la base répond, 503 sinon",
    responses={200: "Application et base opérationnelles", 503: "Base indisponible"},
    tags=['Santé']
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([HealthThrottle])
def health_view(request):
    """Répond 200 si la base répond à un `SELECT 1`. Aucun détail n'est renvoyé (ni version, ni message d'erreur)."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception:
        # Le détail va au journal du serveur, jamais dans la réponse publique
        logger.exception("Vérification de santé : base de données injoignable")
        return Response({'status': 'error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)
