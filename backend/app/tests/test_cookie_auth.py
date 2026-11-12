"""
Tests de l'authentification par cookies HttpOnly : cookies posés, CSRF obligatoire avec un cookie,
repli Bearer, refresh par cookie, déconnexion.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()

LOGIN = '/api/auth/login'
REFRESH = '/api/auth/token/refresh'
LOGOUT = '/api/auth/logout'
ME = '/api/auth/me'
CSRF = '/api/auth/csrf'
CHANGE_PASSWORD = '/api/auth/change-password'

EMAIL = 'cookie@example.com'
PASSWORD = 'MotDePasse-Solide-42'


class CookieAuthTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.user = User.objects.create_user(username='cookie', email=EMAIL, password=PASSWORD)
        # Client qui applique les contrôles CSRF comme un vrai navigateur
        self.browser = APIClient(enforce_csrf_checks=True)

    def login(self, client=None):
        client = client or self.browser
        response = client.post(LOGIN, {'email': EMAIL, 'password': PASSWORD}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def csrf_token(self, client=None):
        client = client or self.browser
        return client.get(CSRF).data['csrfToken']

    # ------------------------------------------------------------ login
    def test_login_sets_httponly_cookies_and_hides_tokens(self):
        response = self.login()
        self.assertEqual(set(response.data), {'user'})
        access, refresh = response.cookies['access_token'], response.cookies['refresh_token']
        for cookie in (access, refresh):
            self.assertTrue(cookie['httponly'])
            self.assertEqual(cookie['samesite'], 'Lax')
        self.assertEqual(access['path'], '/')
        self.assertEqual(refresh['path'], '/api/auth')

    def test_failed_login_sets_no_cookie(self):
        response = self.browser.post(LOGIN, {'email': EMAIL, 'password': 'mauvais'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access_token', response.cookies)

    def test_jwt_contains_no_roles_or_permissions(self):
        token = AccessToken(self.login().cookies['access_token'].value)
        self.assertEqual(token['user_id'], self.user.id)
        for claim in ('permissions', 'roles', 'is_superuser', 'is_staff'):
            self.assertNotIn(claim, token.payload)

    # ------------------------------------------------------------ authentification par cookie
    def test_me_works_with_cookie_alone(self):
        self.login()
        response = self.browser.get(ME)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], EMAIL)
        self.assertIn('permissions', response.data)

    def test_me_requires_authentication(self):
        self.assertEqual(APIClient().get(ME).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cookie_mutation_without_csrf_is_refused(self):
        self.login()
        response = self.browser.post(CHANGE_PASSWORD, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('CSRF', str(response.data))

    def test_cookie_mutation_with_csrf_is_accepted(self):
        self.login()
        token = self.csrf_token()
        response = self.browser.post(CHANGE_PASSWORD, {}, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # passe CSRF, échoue sur les données

    def test_bearer_header_needs_no_csrf(self):
        access = str(RefreshToken.for_user(self.user).access_token)
        client = APIClient(enforce_csrf_checks=True)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = client.post(CHANGE_PASSWORD, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_cookie_is_anonymous_not_an_error(self):
        client = APIClient()
        client.cookies['access_token'] = 'pas.un.jeton'
        self.assertEqual(client.get(ME).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_access_cookie_gives_401(self):
        token = AccessToken.for_user(self.user)
        token.set_exp(lifetime=-timedelta(minutes=5))
        client = APIClient()
        client.cookies['access_token'] = str(token)
        self.assertEqual(client.get(ME).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_cookie_gives_401(self):
        self.login()
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        self.assertEqual(self.browser.get(ME).status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------ refresh
    def test_refresh_uses_the_cookie_and_rotates_both_cookies(self):
        first = self.login()
        old_refresh = first.cookies['refresh_token'].value
        response = self.browser.post(REFRESH, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {'detail'})  # pas de jeton dans le corps
        self.assertNotEqual(response.cookies['refresh_token'].value, old_refresh)
        self.assertTrue(response.cookies['access_token']['httponly'])

    def test_old_refresh_is_blacklisted_after_rotation(self):
        old_refresh = self.login().cookies['refresh_token'].value
        self.browser.post(REFRESH, {}, format='json')
        replay = APIClient()
        replay.cookies['refresh_token'] = old_refresh
        self.assertEqual(replay.post(REFRESH, {}, format='json').status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_without_any_token_gives_401(self):
        self.assertEqual(APIClient().post(REFRESH, {}, format='json').status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_with_body_token_still_works_for_scripts(self):
        refresh = str(RefreshToken.for_user(self.user))
        response = APIClient().post(REFRESH, {'refresh': refresh}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    # ------------------------------------------------------------ logout
    def test_logout_clears_cookies_and_blacklists_refresh(self):
        refresh = self.login().cookies['refresh_token'].value
        response = self.browser.post(LOGOUT, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies['access_token'].value, '')
        self.assertEqual(response.cookies['refresh_token'].value, '')
        replay = APIClient()
        replay.cookies['refresh_token'] = refresh
        self.assertEqual(replay.post(REFRESH, {}, format='json').status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_works_even_without_a_session(self):
        response = APIClient().post(LOGOUT, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------ csrf
    def test_csrf_endpoint_sets_cookie_and_returns_token(self):
        response = APIClient().get(CSRF)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['csrfToken'])
        self.assertIn('csrftoken', response.cookies)
        self.assertFalse(response.cookies['csrftoken']['httponly'])  # lisible par le JS


class CodePermissionTests(APITestCase):
    """has_permission : rôles pour les comptes normaux, toutes les permissions pour un superutilisateur actif."""

    def test_regular_user_without_role_has_no_permission(self):
        user = User.objects.create_user(username='simple', email='simple@example.com', password=PASSWORD)
        self.assertFalse(user.has_permission('users.view'))

    def test_active_superuser_has_every_permission(self):
        user = User.objects.create_user(username='chef', email='chef@example.com', password=PASSWORD, is_superuser=True)
        self.assertTrue(user.has_permission('nimporte.quoi'))

    def test_inactive_superuser_has_none(self):
        user = User.objects.create_user(username='ancien', email='ancien@example.com', password=PASSWORD,
                                        is_superuser=True, is_active=False)
        self.assertFalse(user.has_permission('users.view'))

    def test_anonymous_visitor_gets_401_not_500_on_a_code_protected_route(self):
        self.assertEqual(APIClient().get('/api/v1/elitests').status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(APIClient().get('/api/v1/users').status_code, status.HTTP_401_UNAUTHORIZED)
