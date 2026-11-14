"""
Vues OAuth Google / GitHub : start, callback, liste des providers configurés.
"""
import logging
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.core.cookies import set_auth_cookies
from app.core.models import SocialAccount
from app.core.services import audit_service
from app.core.services.audit_service import Actions
from app.core.services.oauth_service import (
    OAuthError,
    authorization_url,
    complete_oauth,
    configured_providers,
)
from app.core.throttles import (
    OAuthCallbackThrottle,
    OAuthProvidersThrottle,
    OAuthStartThrottle,
)

logger = logging.getLogger(__name__)

VALID_PROVIDERS = {
    SocialAccount.PROVIDER_GOOGLE,
    SocialAccount.PROVIDER_GITHUB,
}


def _frontend_login_redirect(**params) -> HttpResponseRedirect:
    query = urlencode({k: v for k, v in params.items() if v is not None})
    url = f'{settings.FRONTEND_URL}/login'
    if query:
        url = f'{url}?{query}'
    return redirect(url)


@swagger_auto_schema(
    method='get',
    operation_description="Providers OAuth configurés (google, github).",
    responses={200: openapi.Response('Liste des providers')},
    tags=['Auth'],
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([OAuthProvidersThrottle])
def oauth_providers_view(request):
    return Response(configured_providers(), status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Démarre le flux OAuth : redirection vers Google ou GitHub.",
    responses={302: 'Redirection IdP', 503: 'Provider non configuré'},
    tags=['Auth'],
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([OAuthStartThrottle])
def oauth_start_view(request, provider: str):
    provider = (provider or '').lower()
    if provider not in VALID_PROVIDERS:
        return Response({'detail': 'Provider inconnu'}, status=status.HTTP_404_NOT_FOUND)
    try:
        url = authorization_url(request, provider)
    except OAuthError as exc:
        if exc.code == 'not_configured':
            return Response(
                {'detail': 'OAuth non configuré pour ce provider'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        logger.info('OAuth %s démarrage refusé : %s', provider, exc.code)
        return Response(
            {'detail': 'Requête OAuth invalide'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return redirect(url)


@swagger_auto_schema(
    method='get',
    operation_description="Callback OAuth : échange le code, pose les cookies JWT, redirige vers le front.",
    responses={302: 'Redirection frontend'},
    tags=['Auth'],
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([OAuthCallbackThrottle])
def oauth_callback_view(request, provider: str):
    provider = (provider or '').lower()
    if provider not in VALID_PROVIDERS:
        return _frontend_login_redirect(oauth_error='invalid_provider')

    try:
        user, access, refresh = complete_oauth(
            request,
            provider,
            code=request.query_params.get('code'),
            state=request.query_params.get('state'),
            error=request.query_params.get('error'),
        )
    except OAuthError as exc:
        logger.info('OAuth %s échoué : %s', provider, exc.code)
        return _frontend_login_redirect(oauth_error=exc.code)
    except Exception:
        logger.exception('OAuth %s erreur inattendue', provider)
        return _frontend_login_redirect(oauth_error='exchange_failed')

    audit_service.record(
        Actions.LOGIN_SUCCESS,
        actor=user,
        target=user,
        subject=audit_service.account_key(user.email),
        request=request,
        metadata={'method': f'oauth:{provider}'},
    )

    response = _frontend_login_redirect(oauth='1')
    return set_auth_cookies(response, access, refresh)
