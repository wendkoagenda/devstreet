"""
Tests du flux « mot de passe oublié » (challenge e-mail).
"""
import re
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app.core.models import PasswordResetChallenge
from app.core.services.email_service import EmailService
from app.core.services.forgot_password_service import (
    CODE_TTL_MINUTES,
    GENERIC_REQUEST_MESSAGE,
    INVALID_CODE_MESSAGE,
    INVALID_TOKEN_MESSAGE,
    MAX_ATTEMPTS,
    RESET_TOKEN_TTL_MINUTES,
)

User = get_user_model()

FORGOT_URL = '/api/auth/forgot-password'
VERIFY_URL = '/api/auth/verify-reset-code'
RESET_URL = '/api/auth/reset-password'
LOGIN_URL = '/api/auth/login'
REFRESH_URL = '/api/auth/token/refresh'

OLD_PASSWORD = 'OldPass123!x'
NEW_PASSWORD = 'NewPass456!y'
EMAIL = 'jean.dupont@example.com'


class PasswordResetBaseTestCase(APITestCase):
    """Fabrique commune : un utilisateur actif, un cache vide (limitation de débit), une boîte mail vide."""

    def setUp(self):
        cache.clear()
        mail.outbox = []
        self.user = User.objects.create_user(
            username='jdupont',
            email=EMAIL,
            password=OLD_PASSWORD,
            first_name='Jean',
            last_name='Dupont',
        )

    # --- helpers -----------------------------------------------------------
    def request_code(self, email=EMAIL):
        return self.client.post(FORGOT_URL, {'email': email}, format='json')

    def last_code(self):
        """Code à 6 chiffres lu dans le dernier e-mail envoyé."""
        match = re.search(r'\b(\d{6})\b', mail.outbox[-1].body)
        self.assertIsNotNone(match, "Aucun code à 6 chiffres dans l'e-mail")
        return match.group(1)

    def verify(self, code, email=EMAIL):
        return self.client.post(VERIFY_URL, {'email': email, 'code': code}, format='json')

    def reset(self, token, password=NEW_PASSWORD, confirm=None):
        return self.client.post(
            RESET_URL,
            {
                'reset_token': token,
                'new_password': password,
                'new_password_confirm': password if confirm is None else confirm,
            },
            format='json',
        )

    def get_reset_token(self):
        """Parcourt les étapes 1 et 2 et retourne le reset_token."""
        self.request_code()
        response = self.verify(self.last_code())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['reset_token']

    def age_challenges(self, seconds):
        """Vieillit les challenges (created_at est automatique) pour passer le délai entre deux demandes."""
        PasswordResetChallenge.objects.update(created_at=timezone.now() - timedelta(seconds=seconds))


class PasswordResetFlowTests(PasswordResetBaseTestCase):
    """Parcours nominal et sécurité des secrets."""

    def test_full_flow_changes_password(self):
        response = self.request_code()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], GENERIC_REQUEST_MESSAGE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [EMAIL])

        code = self.last_code()
        verify = self.verify(code)
        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        token = verify.data['reset_token']
        self.assertTrue(token)

        done = self.reset(token)
        self.assertEqual(done.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(OLD_PASSWORD))

        login = self.client.post(LOGIN_URL, {'email': EMAIL, 'password': NEW_PASSWORD}, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_secrets_are_never_stored_in_clear(self):
        token = self.get_reset_token()
        code = self.last_code()
        challenge = PasswordResetChallenge.objects.get(user=self.user)

        self.assertNotEqual(challenge.code_hash, code)
        self.assertNotEqual(challenge.reset_token_hash, token)
        self.assertEqual(len(challenge.code_hash), 64)
        self.assertEqual(len(challenge.reset_token_hash), 64)
        self.assertNotIn(code, challenge.code_hash)

    def test_email_contains_code_and_ttl_without_html_escaping(self):
        self.user.first_name = "Jean-O'Brien"
        self.user.save()
        self.request_code()
        message = mail.outbox[0]
        self.assertIn("Jean-O'Brien", message.body)
        self.assertIn(str(CODE_TTL_MINUTES), message.body)
        self.assertEqual(message.alternatives[0][1], 'text/html')

    def test_password_is_not_changed_before_last_step(self):
        self.request_code()
        self.verify(self.last_code())
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(OLD_PASSWORD))

    def test_public_routes_ignore_a_stale_authorization_header(self):
        """Un ancien token (expiré ou invalide) ne doit pas provoquer de 401 sur les routes publiques."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token.expire.invalide')
        response = self.request_code()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetEnumerationTests(PasswordResetBaseTestCase):
    """Aucune différence de réponse selon que le compte existe ou non."""

    def test_same_response_for_known_unknown_and_inactive_accounts(self):
        User.objects.create_user(
            username='inactif', email='inactif@example.com', password=OLD_PASSWORD,
            first_name='In', last_name='Actif', is_active=False,
        )
        known = self.request_code(EMAIL)
        unknown = self.request_code('personne@example.com')
        inactive = self.request_code('inactif@example.com')

        self.assertEqual(known.status_code, unknown.status_code)
        self.assertEqual(known.status_code, inactive.status_code)
        self.assertEqual(known.json(), unknown.json())
        self.assertEqual(known.json(), inactive.json())
        # un seul e-mail : celui du compte actif
        self.assertEqual(len(mail.outbox), 1)

    def test_email_is_matched_case_insensitively(self):
        response = self.request_code('  Jean.DUPONT@Example.com ')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_malformed_email_is_rejected(self):
        response = self.client.post(FORGOT_URL, {'email': 'pas-un-email'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_verify_does_not_reveal_whether_the_account_exists(self):
        self.request_code()
        wrong_for_known = self.verify('000000')
        unknown_account = self.verify('000000', email='personne@example.com')
        self.assertEqual(wrong_for_known.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(wrong_for_known.json(), unknown_account.json())
        self.assertEqual(wrong_for_known.data['error'], INVALID_CODE_MESSAGE)

    def test_email_failure_returns_the_generic_response_and_leaves_no_challenge(self):
        with mock.patch.object(EmailService, 'send_templated', side_effect=RuntimeError('SMTP indisponible')):
            with self.assertLogs('app.core.services.forgot_password_service', level='ERROR'):
                response = self.request_code()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], GENERIC_REQUEST_MESSAGE)
        self.assertEqual(PasswordResetChallenge.objects.count(), 0)


class PasswordResetCodeTests(PasswordResetBaseTestCase):
    """Étape 2 : tentatives, expiration, remplacement du code."""

    def test_wrong_code_increments_attempts(self):
        self.request_code()
        response = self.verify('000000' if self.last_code() != '000000' else '111111')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], INVALID_CODE_MESSAGE)
        self.assertEqual(PasswordResetChallenge.objects.get().attempts, 1)

    def test_code_is_locked_after_max_attempts_even_with_the_right_code(self):
        self.request_code()
        good = self.last_code()
        bad = '000000' if good != '000000' else '111111'
        for _ in range(MAX_ATTEMPTS):
            self.assertEqual(self.verify(bad).status_code, status.HTTP_400_BAD_REQUEST)

        locked = self.verify(good)
        self.assertEqual(locked.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(locked.data['error'], INVALID_CODE_MESSAGE)
        self.assertEqual(PasswordResetChallenge.objects.get().attempts, MAX_ATTEMPTS)

    def test_expired_code_is_rejected(self):
        self.request_code()
        code = self.last_code()
        later = timezone.now() + timedelta(minutes=CODE_TTL_MINUTES, seconds=1)
        with mock.patch('app.core.services.forgot_password_service.timezone.now', return_value=later):
            response = self.verify(code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], INVALID_CODE_MESSAGE)

    def test_code_is_single_use(self):
        self.request_code()
        code = self.last_code()
        self.assertEqual(self.verify(code).status_code, status.HTTP_200_OK)
        self.assertEqual(self.verify(code).status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_request_invalidates_the_previous_code(self):
        self.request_code()
        old_code = self.last_code()
        self.age_challenges(120)  # passe le délai minimal entre deux demandes

        self.request_code()
        self.assertEqual(len(mail.outbox), 2)
        new_code = self.last_code()

        if old_code != new_code:  # (1 chance sur un million d'obtenir deux fois le même code)
            self.assertEqual(self.verify(old_code).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.verify(new_code).status_code, status.HTTP_200_OK)

    def test_requests_too_close_together_send_a_single_email(self):
        self.request_code()
        second = self.request_code()
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(second.data['message'], GENERIC_REQUEST_MESSAGE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(PasswordResetChallenge.objects.count(), 1)

    def test_code_must_have_six_digits(self):
        self.request_code()
        for bad in ('12345', '1234567', 'abcdef', ''):
            response = self.verify(bad)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, bad)


class PasswordResetTokenTests(PasswordResetBaseTestCase):
    """Étape 3 : token à usage unique, validation du mot de passe, sessions."""

    def test_token_is_single_use(self):
        token = self.get_reset_token()
        self.assertEqual(self.reset(token).status_code, status.HTTP_200_OK)

        again = self.reset(token, password='Another789!z')
        self.assertEqual(again.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(again.data['error'], INVALID_TOKEN_MESSAGE)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))

    def test_expired_token_is_rejected(self):
        token = self.get_reset_token()
        later = timezone.now() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES, seconds=1)
        with mock.patch('app.core.services.forgot_password_service.timezone.now', return_value=later):
            response = self.reset(token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], INVALID_TOKEN_MESSAGE)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(OLD_PASSWORD))

    def test_unknown_token_is_rejected(self):
        response = self.reset('token-inconnu')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], INVALID_TOKEN_MESSAGE)

    def test_passwords_must_match(self):
        token = self.get_reset_token()
        response = self.reset(token, confirm='Different123!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_short_password_is_rejected(self):
        token = self.get_reset_token()
        self.assertEqual(self.reset(token, password='Ab1!').status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_is_rejected_without_consuming_the_token(self):
        token = self.get_reset_token()
        weak = self.reset(token, password='12345678')  # 100 % numérique : refusé par les validateurs Django
        self.assertEqual(weak.status_code, status.HTTP_400_BAD_REQUEST)

        # le même token reste utilisable avec un mot de passe valide
        self.assertEqual(self.reset(token).status_code, status.HTTP_200_OK)

    def test_reset_blacklists_existing_refresh_tokens(self):
        login = self.client.post(LOGIN_URL, {'email': EMAIL, 'password': OLD_PASSWORD}, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        old_refresh = login.cookies['refresh_token'].value

        token = self.get_reset_token()
        self.assertEqual(self.reset(token).status_code, status.HTTP_200_OK)

        refreshed = self.client.post(REFRESH_URL, {'refresh': old_refresh}, format='json')
        self.assertEqual(refreshed.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reset_invalidates_other_open_challenges(self):
        self.request_code()
        first_code = self.last_code()
        self.age_challenges(120)
        token = self.get_reset_token()  # deuxième challenge
        self.assertEqual(self.reset(token).status_code, status.HTTP_200_OK)

        if first_code != self.last_code():
            self.assertEqual(self.verify(first_code).status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_cannot_complete_the_reset(self):
        token = self.get_reset_token()
        self.user.is_active = False
        self.user.save()
        response = self.reset(token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], INVALID_TOKEN_MESSAGE)


class PasswordResetThrottleTests(PasswordResetBaseTestCase):
    """Limitation de débit par IP (5 demandes de code par heure par défaut)."""

    def test_forgot_password_is_rate_limited(self):
        for index in range(5):
            response = self.request_code(f'inconnu{index}@example.com')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        blocked = self.request_code('inconnu-de-plus@example.com')
        self.assertEqual(blocked.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class PurgePasswordResetChallengesCommandTests(PasswordResetBaseTestCase):
    """Commande purge_password_reset_challenges."""

    def test_purges_only_old_challenges(self):
        self.request_code()
        self.age_challenges(60 * 60 * 24 * 10)  # le premier challenge date de 10 jours
        old_id = PasswordResetChallenge.objects.get().id

        self.request_code()  # nouveau challenge (le délai minimal entre deux demandes est dépassé)
        self.assertEqual(PasswordResetChallenge.objects.count(), 2)

        out = StringIO()
        call_command('purge_password_reset_challenges', '--days', '7', stdout=out)

        self.assertFalse(PasswordResetChallenge.objects.filter(id=old_id).exists())
        self.assertEqual(PasswordResetChallenge.objects.count(), 1)
        self.assertIn('1 challenge', out.getvalue())
