"""Badges d'activité non lue pour la sidebar."""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.communaute.services.activity_service import ActivityService


@swagger_auto_schema(method='get', tags=['V1 - Activity'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_badges_view(request):
    """Retourne {messages, communautes, chaines} — compteurs de badges."""
    badges = ActivityService().badges_for(request.user)
    return Response(badges)
