"""Profil public d'un membre (mur) + suivi + recherche pour mentions."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.communaute.services.suiviutilisateur_service import SuiviUtilisateurService
from app.core.serializers import PublicProfileSerializer

User = get_user_model()


def _err(exc: ValidationError) -> str:
    if hasattr(exc, 'messages'):
        return '; '.join(str(m) for m in exc.messages)
    if hasattr(exc, 'message'):
        return str(exc.message)
    return str(exc)


def _membre_brief(user) -> dict:
    return {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'photo': (getattr(user, 'photo', None) or '') or '',
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def membre_search_view(request):
    """Recherche de membres actifs pour les mentions (@username)."""
    query = (request.query_params.get('q') or '').strip()
    if len(query) < 1:
        return Response([])
    qs = (
        User.objects.filter(is_active=True)
        .filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )
        .exclude(pk=request.user.id)
        .order_by('username')[:8]
    )
    return Response([_membre_brief(user) for user in qs])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def membre_suivis_view(request):
    """Liste les membres suivis par l'utilisateur connecté (DM / Messages)."""
    search = (request.query_params.get('q') or '').strip() or None
    try:
        limit = int(request.query_params.get('limit') or 50)
    except (TypeError, ValueError):
        limit = 50
    membres = SuiviUtilisateurService().list_membres_suivis(
        request.user, search=search, limit=limit
    )
    return Response([_membre_brief(user) for user in membres])


def _profile_payload(request, user):
    data = PublicProfileSerializer(user).data
    data['is_following'] = False
    if request.user.id != user.id:
        data['is_following'] = SuiviUtilisateurService().est_suivi(
            suiveur=request.user, suivi_id=user.id
        )
    return data


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def membre_profile_view(request, user_id: int):
    """Retourne le profil public d'un utilisateur actif."""
    user = User.objects.filter(pk=user_id, is_active=True).first()
    if user is None:
        return Response(
            {'error': 'Profil introuvable'},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(_profile_payload(request, user), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def membre_by_username_view(request, username: str):
    """Résout un @username vers le profil public."""
    user = (
        User.objects.filter(is_active=True, username__iexact=username.strip())
        .first()
    )
    if user is None:
        return Response(
            {'error': 'Profil introuvable'},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(_profile_payload(request, user), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def membre_suivre_view(request, user_id: int):
    """Bascule le suivi d'un membre (suivre / ne plus suivre)."""
    try:
        result = SuiviUtilisateurService().toggle_suivi(
            suiveur=request.user, suivi_id=int(user_id)
        )
        return Response(result, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)
