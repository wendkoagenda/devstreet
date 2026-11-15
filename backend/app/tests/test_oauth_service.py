"""
Tests du service OAuth social (Google / GitHub) : résolution utilisateur et providers.
Les appels HTTP vers les IdP sont mockés.
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from rest_framework.test import APIClient

from app.core.models import SocialAccount
from app.core.services.oauth_service import (
    OAuthError,
    OAuthProfile,
    assert_provider_configured,
    configured_providers,
    resolve_user,
    sign_state,
    unsign_state,
)

User = get_user_model()


@override_settings(
    GOOGLE_OAUTH_CLIENT_ID='google-id',
    GOOGLE_OAUTH_CLIENT_SECRET='google-secret',
    OAUTH_GITHUB_CLIENT_ID='github-id',
    OAUTH_GITHUB_CLIENT_SECRET='github-secret',
    FRONTEND_URL='http://localhost:5173',
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class OAuthServiceTests(TestCase):
    def test_configured_providers(self):
        flags = configured_providers()
        self.assertTrue(flags['google'])
        self.assertTrue(flags['github'])

    @override_settings(GOOGLE_OAUTH_CLIENT_ID=None, GOOGLE_OAUTH_CLIENT_SECRET=None)
    def test_google_not_configured(self):
        self.assertFalse(configured_providers()['google'])
        with self.assertRaises(OAuthError) as ctx:
            assert_provider_configured('google')
        self.assertEqual(ctx.exception.code, 'not_configured')

    def test_state_roundtrip(self):
        state = sign_state('google')
        unsign_state(state, 'google')
        with self.assertRaises(OAuthError):
            unsign_state(state, 'github')

    def test_resolve_creates_user(self):
        profile = OAuthProfile(
            provider='google',
            provider_user_id='g-1',
            email='new.oauth@example.com',
            first_name='Ada',
            last_name='Lovelace',
        )
        user = resolve_user(profile)
        self.assertEqual(user.email, 'new.oauth@example.com')
        self.assertFalse(user.has_usable_password())
        self.assertTrue(
            SocialAccount.objects.filter(
                user=user, provider='google', provider_user_id='g-1'
            ).exists()
        )
        # Le rôle et le type de compte sont attribués à l'onboarding, pas à la création du compte
        self.assertEqual(user.roles.count(), 0)
        self.assertEqual(user.account_type, '')

    def test_resolve_links_existing_email(self):
        existing = User.objects.create_user(
            email='same@example.com',
            username='sameuser',
            password='password12345',
            first_name='Sam',
            last_name='User',
        )
        profile = OAuthProfile(
            provider='github',
            provider_user_id='gh-99',
            email='same@example.com',
            first_name='Sam',
            last_name='User',
        )
        user = resolve_user(profile)
        self.assertEqual(user.id, existing.id)
        self.assertTrue(
            SocialAccount.objects.filter(
                user=existing, provider='github', provider_user_id='gh-99'
            ).exists()
        )

    def test_resolve_reuses_social_account(self):
        existing = User.objects.create_user(
            email='linked@example.com',
            username='linked',
            password='password12345',
            first_name='Li',
            last_name='Nked',
        )
        SocialAccount.objects.create(
            user=existing,
            provider='google',
            provider_user_id='g-reuse',
            email='linked@example.com',
        )
        profile = OAuthProfile(
            provider='google',
            provider_user_id='g-reuse',
            email='linked@example.com',
            first_name='Li',
            last_name='Nked',
        )
        user = resolve_user(profile)
        self.assertEqual(user.id, existing.id)
        self.assertEqual(SocialAccount.objects.filter(provider_user_id='g-reuse').count(), 1)

    def test_resolve_inactive_refused(self):
        existing = User.objects.create_user(
            email='off@example.com',
            username='offuser',
            password='password12345',
            first_name='Off',
            last_name='User',
            is_active=False,
        )
        profile = OAuthProfile(
            provider='google',
            provider_user_id='g-off',
            email='off@example.com',
            first_name='Off',
            last_name='User',
        )
        with self.assertRaises(OAuthError) as ctx:
            resolve_user(profile)
        self.assertEqual(ctx.exception.code, 'inactive')
        self.assertFalse(SocialAccount.objects.filter(user=existing).exists())


@override_settings(
    GOOGLE_OAUTH_CLIENT_ID=None,
    GOOGLE_OAUTH_CLIENT_SECRET=None,
    OAUTH_GITHUB_CLIENT_ID=None,
    OAUTH_GITHUB_CLIENT_SECRET=None,
    FRONTEND_URL='http://localhost:5173',
)
class OAuthViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_providers_endpoint_all_false(self):
        response = self.client.get('/api/auth/oauth/providers')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'google': False, 'github': False})

    def test_start_not_configured_returns_503(self):
        response = self.client.get('/api/auth/oauth/google/start')
        self.assertEqual(response.status_code, 503)


@override_settings(
    GOOGLE_OAUTH_CLIENT_ID='google-id',
    GOOGLE_OAUTH_CLIENT_SECRET='google-secret',
    OAUTH_GITHUB_CLIENT_ID=None,
    OAUTH_GITHUB_CLIENT_SECRET=None,
    FRONTEND_URL='http://localhost:5173',
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class OAuthStartConfiguredTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = RequestFactory()

    def test_providers_google_only(self):
        response = self.client.get('/api/auth/oauth/providers')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'google': True, 'github': False})

    def test_start_redirects_to_google(self):
        response = self.client.get('/api/auth/oauth/google/start')
        self.assertEqual(response.status_code, 302)
        self.assertIn('accounts.google.com', response['Location'])

    @patch('app.core.views.oauth_views.complete_oauth')
    def test_callback_sets_cookies_and_redirects(self, mock_complete):
        user = User.objects.create_user(
            email='cb@example.com',
            username='cbuser',
            password='password12345',
            first_name='Cb',
            last_name='User',
        )
        mock_complete.return_value = (user, 'access-token', 'refresh-token')
        response = self.client.get(
            '/api/auth/oauth/google/callback',
            {'code': 'abc', 'state': 'ignored-by-mock'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?oauth=1', response['Location'])
        self.assertIn('access_token', response.cookies)
