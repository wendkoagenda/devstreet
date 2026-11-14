"""
Connexion / inscription OAuth (Google, GitHub).

Flux Authorization Code : start → IdP → callback → utilisateur + cookies JWT.
Les secrets client sont facultatifs : provider absent → non configuré (503).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode

import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.db import transaction

from app.core.models import Role, SocialAccount
from app.core.username_rules import check_username

logger = logging.getLogger(__name__)

User = get_user_model()

STATE_SALT = 'oauth-social-state'
STATE_MAX_AGE_SECONDS = 600

PROVIDERS = (SocialAccount.PROVIDER_GOOGLE, SocialAccount.PROVIDER_GITHUB)


class OAuthError(Exception):
    """Erreur métier OAuth (message court pour query string front)."""

    def __init__(self, code: str, detail: str = ''):
        self.code = code
        self.detail = detail
        super().__init__(code)


@dataclass(frozen=True)
class OAuthProfile:
    provider: str
    provider_user_id: str
    email: str
    first_name: str
    last_name: str


def configured_providers() -> Dict[str, bool]:
    """Providers pour lesquels client_id et secret sont tous deux définis."""
    return {
        SocialAccount.PROVIDER_GOOGLE: bool(
            settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET
        ),
        SocialAccount.PROVIDER_GITHUB: bool(
            settings.OAUTH_GITHUB_CLIENT_ID and settings.OAUTH_GITHUB_CLIENT_SECRET
        ),
    }


def assert_provider_configured(provider: str) -> None:
    if provider not in PROVIDERS:
        raise OAuthError('invalid_provider')
    if not configured_providers().get(provider):
        raise OAuthError('not_configured')


def sign_state(provider: str) -> str:
    return signing.dumps({'provider': provider}, salt=STATE_SALT)


def unsign_state(state: str, expected_provider: str) -> None:
    try:
        data = signing.loads(state, salt=STATE_SALT, max_age=STATE_MAX_AGE_SECONDS)
    except signing.BadSignature as exc:
        raise OAuthError('invalid_state') from exc
    if data.get('provider') != expected_provider:
        raise OAuthError('invalid_state')


def _callback_uri(request, provider: str) -> str:
    """
    URI de callback déclarée chez Google/GitHub.

    On ancre sur FRONTEND_URL (même origine que le SPA + proxy Vite /api),
    sinon les cookies HttpOnly posés sur :8000 ne seraient pas renvoyés
    quand le front appelle /api via :5173.
    """
    del request  # signature stable pour les appels existants
    base = settings.FRONTEND_URL.rstrip('/')
    return f'{base}/api/auth/oauth/{provider}/callback'


def authorization_url(request, provider: str) -> str:
    assert_provider_configured(provider)
    state = sign_state(provider)
    redirect_uri = _callback_uri(request, provider)

    if provider == SocialAccount.PROVIDER_GOOGLE:
        params = {
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'online',
            'prompt': 'select_account',
        }
        return f'https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}'

    params = {
        'client_id': settings.OAUTH_GITHUB_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'read:user user:email',
        'state': state,
        'allow_signup': 'true',
    }
    return f'https://github.com/login/oauth/authorize?{urlencode(params)}'


def _exchange_google(code: str, redirect_uri: str) -> OAuthProfile:
    token_resp = httpx.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        },
        timeout=20.0,
    )
    if token_resp.status_code >= 400:
        logger.info('Google token exchange failed: %s', token_resp.text[:200])
        raise OAuthError('exchange_failed')
    access_token = token_resp.json().get('access_token')
    if not access_token:
        raise OAuthError('exchange_failed')

    user_resp = httpx.get(
        'https://openidconnect.googleapis.com/v1/userinfo',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=20.0,
    )
    if user_resp.status_code >= 400:
        raise OAuthError('exchange_failed')
    data = user_resp.json()
    email = (data.get('email') or '').strip().lower()
    if not email or not data.get('email_verified', True):
        raise OAuthError('email_required')
    sub = str(data.get('sub') or '').strip()
    if not sub:
        raise OAuthError('exchange_failed')
    return OAuthProfile(
        provider=SocialAccount.PROVIDER_GOOGLE,
        provider_user_id=sub,
        email=email,
        first_name=(data.get('given_name') or data.get('name') or email.split('@')[0])[:150],
        last_name=(data.get('family_name') or '')[:150] or '—',
    )


def _exchange_github(code: str, redirect_uri: str) -> OAuthProfile:
    token_resp = httpx.post(
        'https://github.com/login/oauth/access_token',
        headers={'Accept': 'application/json'},
        data={
            'client_id': settings.OAUTH_GITHUB_CLIENT_ID,
            'client_secret': settings.OAUTH_GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': redirect_uri,
        },
        timeout=20.0,
    )
    if token_resp.status_code >= 400:
        logger.info('GitHub token exchange failed: %s', token_resp.text[:200])
        raise OAuthError('exchange_failed')
    access_token = token_resp.json().get('access_token')
    if not access_token:
        raise OAuthError('exchange_failed')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    user_resp = httpx.get('https://api.github.com/user', headers=headers, timeout=20.0)
    if user_resp.status_code >= 400:
        raise OAuthError('exchange_failed')
    data = user_resp.json()
    provider_user_id = str(data.get('id') or '').strip()
    if not provider_user_id:
        raise OAuthError('exchange_failed')

    email = (data.get('email') or '').strip().lower()
    if not email:
        emails_resp = httpx.get(
            'https://api.github.com/user/emails',
            headers=headers,
            timeout=20.0,
        )
        if emails_resp.status_code < 400:
            for entry in emails_resp.json():
                if entry.get('primary') and entry.get('verified') and entry.get('email'):
                    email = str(entry['email']).strip().lower()
                    break
            if not email:
                for entry in emails_resp.json():
                    if entry.get('verified') and entry.get('email'):
                        email = str(entry['email']).strip().lower()
                        break
    if not email:
        raise OAuthError('email_required')

    full_name = (data.get('name') or '').strip()
    if full_name and ' ' in full_name:
        first_name, last_name = full_name.split(' ', 1)
    elif full_name:
        first_name, last_name = full_name, '—'
    else:
        login = (data.get('login') or email.split('@')[0])[:150]
        first_name, last_name = login, '—'

    return OAuthProfile(
        provider=SocialAccount.PROVIDER_GITHUB,
        provider_user_id=provider_user_id,
        email=email,
        first_name=first_name[:150],
        last_name=last_name[:150],
    )


def fetch_profile(provider: str, code: str, redirect_uri: str) -> OAuthProfile:
    assert_provider_configured(provider)
    if provider == SocialAccount.PROVIDER_GOOGLE:
        return _exchange_google(code, redirect_uri)
    return _exchange_github(code, redirect_uri)


def _unique_username(base: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9._-]', '', base)[:24] or 'user'
    candidate = cleaned
    n = 0
    while check_username(candidate) is not None:
        n += 1
        suffix = str(n)
        candidate = f'{cleaned[: 24 - len(suffix)]}{suffix}'
    return candidate


def _ensure_member_role_name() -> str:
    """Délègue la création du rôle membre au helper auth existant."""
    from app.core.views.auth_views import _ensure_default_member_role

    return _ensure_default_member_role()


@transaction.atomic
def resolve_user(profile: OAuthProfile):
    """
    Retrouve ou crée l'utilisateur DevStreet pour un profil OAuth.
    - SocialAccount existant → cet utilisateur
    - E-mail déjà en base → lie le provider puis connecte
    - Sinon → crée un compte (mot de passe inutilisable) + rôle membre
    """
    existing_link = (
        SocialAccount.objects.select_related('user')
        .filter(provider=profile.provider, provider_user_id=profile.provider_user_id)
        .first()
    )
    if existing_link:
        user = existing_link.user
        if not user.is_active:
            raise OAuthError('inactive')
        if profile.email and existing_link.email != profile.email:
            existing_link.email = profile.email
            existing_link.save(update_fields=['email', 'updated_at'])
        return user

    user = User.objects.filter(email__iexact=profile.email).first()
    if user:
        if not user.is_active:
            raise OAuthError('inactive')
        SocialAccount.objects.create(
            user=user,
            provider=profile.provider,
            provider_user_id=profile.provider_user_id,
            email=profile.email,
        )
        return user

    role_name = _ensure_member_role_name()
    role = Role.objects.get(name=role_name)
    username = _unique_username(profile.email.split('@')[0])
    user = User(
        email=profile.email,
        username=username,
        first_name=profile.first_name or username,
        last_name=profile.last_name or '—',
        is_active=True,
    )
    user.set_unusable_password()
    user.save()
    user.roles.add(role)
    SocialAccount.objects.create(
        user=user,
        provider=profile.provider,
        provider_user_id=profile.provider_user_id,
        email=profile.email,
    )
    return user


def issue_tokens_for_user(user) -> Tuple[str, str]:
    """Access + refresh JWT enrichis (même claims que l'inscription)."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    refresh['user_id'] = user.id
    refresh['email'] = user.email
    refresh['full_name'] = user.full_name
    access = refresh.access_token
    access['user_id'] = user.id
    access['email'] = user.email
    access['full_name'] = user.full_name
    return str(access), str(refresh)


def complete_oauth(
    request,
    provider: str,
    *,
    code: Optional[str],
    state: Optional[str],
    error: Optional[str],
) -> Tuple[Any, str, str]:
    """
    Valide le callback IdP et retourne (user, access, refresh).
    Lève OAuthError en cas d'échec.
    """
    if error:
        raise OAuthError('denied')
    if not code or not state:
        raise OAuthError('invalid_state')
    assert_provider_configured(provider)
    unsign_state(state, provider)
    redirect_uri = _callback_uri(request, provider)
    profile = fetch_profile(provider, code, redirect_uri)
    user = resolve_user(profile)
    access, refresh = issue_tokens_for_user(user)
    return user, access, refresh
