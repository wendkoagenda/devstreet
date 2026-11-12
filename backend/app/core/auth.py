"""
Authentification DRF : cookie HttpOnly d'abord, en-tête Bearer en repli.

- Cookie `access_token` valide  -> utilisateur authentifié, protection CSRF OBLIGATOIRE
  (un cookie est envoyé automatiquement par le navigateur : sans CSRF, un site tiers pourrait agir à votre place).
- Cookie absent, expiré ou invalide -> pas d'erreur immédiate : la requête reste anonyme (401 par les permissions),
  ce qui laisse le front appeler /auth/token/refresh puis rejouer la requête.
- En-tête `Authorization: Bearer <jwt>` (Swagger, tests, scripts) -> comportement SimpleJWT habituel, sans CSRF.
"""
import logging

from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)


def _enforce_csrf(request):
    """Même contrôle que SessionAuthentication de DRF (cookie csrftoken + en-tête X-CSRFToken)."""
    check = CSRFCheck(lambda req: None)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        if self.get_header(request) is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get(settings.AUTH_COOKIE_ACCESS)
        if not raw_token:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
        except (InvalidToken, TokenError, exceptions.AuthenticationFailed) as error:
            # Voulu : un cookie expiré laisse la requête anonyme (401), le front renouvelle puis rejoue
            logger.debug("Cookie %s refusé : %s", settings.AUTH_COOKIE_ACCESS, error)
            return None

        _enforce_csrf(request)
        return user, validated_token
