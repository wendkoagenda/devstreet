"""
Cookies d'authentification : les jetons JWT vivent dans des cookies HttpOnly, jamais lisibles par le JavaScript.

- access_token  : chemin « / », envoyé sur toutes les requêtes de l'API.
- refresh_token : chemin « /api/auth » seulement (login, refresh, logout), jamais sur les routes métier.
"""
from django.conf import settings


def _common():
    return {
        'httponly': True,
        'secure': settings.AUTH_COOKIE_SECURE,
        'samesite': settings.AUTH_COOKIE_SAMESITE,
        'domain': settings.AUTH_COOKIE_DOMAIN,
    }


def set_auth_cookies(response, access=None, refresh=None):
    """Pose les cookies JWT (seulement ceux dont la valeur est fournie)."""
    lifetimes = settings.SIMPLE_JWT
    if access:
        response.set_cookie(
            settings.AUTH_COOKIE_ACCESS, str(access), path=settings.AUTH_COOKIE_ACCESS_PATH,
            max_age=int(lifetimes['ACCESS_TOKEN_LIFETIME'].total_seconds()), **_common(),
        )
    if refresh:
        response.set_cookie(
            settings.AUTH_COOKIE_REFRESH, str(refresh), path=settings.AUTH_COOKIE_REFRESH_PATH,
            max_age=int(lifetimes['REFRESH_TOKEN_LIFETIME'].total_seconds()), **_common(),
        )
    return response


def clear_auth_cookies(response):
    """Supprime les cookies JWT (mêmes chemin et domaine que ceux utilisés pour les poser)."""
    for name, path in (
        (settings.AUTH_COOKIE_ACCESS, settings.AUTH_COOKIE_ACCESS_PATH),
        (settings.AUTH_COOKIE_REFRESH, settings.AUTH_COOKIE_REFRESH_PATH),
    ):
        response.delete_cookie(
            name, path=path, domain=settings.AUTH_COOKIE_DOMAIN, samesite=settings.AUTH_COOKIE_SAMESITE,
        )
    return response
