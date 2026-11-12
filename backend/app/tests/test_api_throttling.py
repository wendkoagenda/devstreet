"""
Limitation de débit de l'API : limite par défaut sur toutes les routes, limites propres sur les routes publiques,
comptage par adresse réelle derrière un proxy.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import SimpleTestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework.throttling import UserRateThrottle

from app.core.throttles import CsrfThrottle, LogoutThrottle, TokenVerifyThrottle

BACKEND_DIR = Path(__file__).resolve().parents[2]
User = get_user_model()


class DefaultThrottleSettingsTests(SimpleTestCase):
    def test_every_route_has_a_default_rate_limit(self):
        classes = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES']
        self.assertIn('rest_framework.throttling.AnonRateThrottle', classes)
        self.assertIn('rest_framework.throttling.UserRateThrottle', classes)

    def test_default_rates_are_defined(self):
        rates = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
        self.assertEqual(rates['anon'], '60/minute')
        self.assertEqual(rates['user'], '600/minute')

    def test_public_routes_have_their_own_rates(self):
        rates = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
        for scope in ('login', 'token_refresh', 'token_verify', 'logout', 'csrf',
                      'password_reset_request', 'password_reset_verify', 'password_reset_confirm'):
            self.assertIn(scope, rates)


class RouteThrottlingTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.user = User.objects.create_user(username='limite', email='limite@example.com', password='Mot-de-passe-42')

    def test_authenticated_routes_are_limited_by_the_default_user_rate(self):
        self.client.force_authenticate(self.user)
        with patch.dict(UserRateThrottle.THROTTLE_RATES, {'user': '2/minute'}):
            codes = [self.client.get('/api/auth/me').status_code for _ in range(3)]
        self.assertEqual(codes, [200, 200, 429])

    def test_the_default_limit_is_per_user_not_shared(self):
        other = User.objects.create_user(username='autre', email='autre@example.com', password='Mot-de-passe-42')
        with patch.dict(UserRateThrottle.THROTTLE_RATES, {'user': '1/minute'}):
            self.client.force_authenticate(self.user)
            self.assertEqual(self.client.get('/api/auth/me').status_code, 200)
            self.assertEqual(self.client.get('/api/auth/me').status_code, 429)
            self.client.force_authenticate(other)
            self.assertEqual(self.client.get('/api/auth/me').status_code, 200)

    def assert_limited(self, throttle, scope, method, url):
        with patch.dict(throttle.THROTTLE_RATES, {scope: '2/minute'}):
            codes = [getattr(APIClient(), method)(url, {}, format='json').status_code for _ in range(3)]
        self.assertNotIn(429, codes[:2])
        self.assertEqual(codes[2], 429)

    def test_csrf_route_is_limited(self):
        self.assert_limited(CsrfThrottle, 'csrf', 'get', '/api/auth/csrf')

    def test_logout_route_is_limited(self):
        self.assert_limited(LogoutThrottle, 'logout', 'post', '/api/auth/logout')

    def test_token_verify_route_is_limited(self):
        self.assert_limited(TokenVerifyThrottle, 'token_verify', 'post', '/api/auth/token/verify')


class ProxyAwareThrottlingTests(SimpleTestCase):
    """Derrière un reverse proxy, la limite compte l'adresse réelle du visiteur et non celle du proxy (sinon tous partageraient un seul compteur)."""

    def num_proxies(self, behind_proxy):
        env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings',
               'USE_X_FORWARDED_PROTO': 'true' if behind_proxy else 'false'}
        code = ('import json, django\ndjango.setup()\nfrom django.conf import settings\n'
                'print(json.dumps(settings.REST_FRAMEWORK["NUM_PROXIES"]))\n')
        out = subprocess.run([sys.executable, '-c', code], cwd=BACKEND_DIR, env=env,
                             capture_output=True, text=True, check=True)
        return json.loads(out.stdout.strip().splitlines()[-1])

    def test_one_trusted_proxy_behind_a_reverse_proxy(self):
        self.assertEqual(self.num_proxies(True), 1)

    def test_no_proxy_otherwise(self):
        # 0 et non None : None ferait confiance à un X-Forwarded-For forgé par le client
        self.assertEqual(self.num_proxies(False), 0)


class ForgedForwardedForTests(SimpleTestCase):
    def ident(self, num_proxies, forwarded):
        from django.conf import settings
        from django.test import RequestFactory, override_settings
        from rest_framework.throttling import BaseThrottle
        rest_framework = {**settings.REST_FRAMEWORK, 'NUM_PROXIES': num_proxies}
        with override_settings(REST_FRAMEWORK=rest_framework):
            request = RequestFactory().get('/', HTTP_X_FORWARDED_FOR=forwarded, REMOTE_ADDR='203.0.113.9')
            return BaseThrottle().get_ident(request)

    def test_without_proxy_a_forged_header_is_ignored(self):
        self.assertEqual(self.ident(0, '198.51.100.1'), '203.0.113.9')

    def test_behind_one_proxy_the_address_added_by_the_proxy_is_used(self):
        self.assertEqual(self.ident(1, '198.51.100.1, 192.0.2.7'), '192.0.2.7')
