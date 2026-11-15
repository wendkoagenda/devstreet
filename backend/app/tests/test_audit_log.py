"""
Journal d'audit et verrouillage de la connexion par compte : événements enregistrés, aucune donnée sensible,
verrouillage identique pour un compte connu ou inconnu, fenêtre glissante, entrées non modifiables, purge.
"""
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from app.core.models import AuditLog
from app.core.services import audit_service, login_lockout
from app.core.services.audit_service import Actions

User = get_user_model()

LOGIN = '/api/auth/login'
CHANGE_PASSWORD = '/api/auth/change-password'
EMAIL = 'audit@example.com'
PASSWORD = 'MotDePasse-Solide-42'


class AuditTestCase(APITestCase):
    def setUp(self):
        cache.clear()  # la limite par IP ne doit pas interférer avec ces tests
        self.addCleanup(cache.clear)
        self.user = User.objects.create_user(username='audit', email=EMAIL, password=PASSWORD)

    def attempt(self, email=EMAIL, password=PASSWORD, client=None):
        return (client or APIClient()).post(LOGIN, {'email': email, 'password': password}, format='json')

    def entries(self, action):
        return AuditLog.objects.filter(action=action)


class LoginAuditTests(AuditTestCase):
    def test_successful_login_is_recorded_with_author_target_and_address(self):
        self.assertEqual(self.attempt().status_code, status.HTTP_200_OK)
        entry = self.entries(Actions.LOGIN_SUCCESS).get()
        self.assertEqual(entry.actor, self.user)
        self.assertEqual(entry.target_id, str(self.user.pk))
        self.assertEqual(entry.ip_address, '127.0.0.1')

    def test_an_action_without_request_has_no_address(self):
        self.assertEqual(audit_service.record(Actions.USER_UPDATED).ip_address, '')

    def test_failed_login_for_a_known_account_targets_it(self):
        self.assertEqual(self.attempt(password='mauvais').status_code, status.HTTP_401_UNAUTHORIZED)
        entry = self.entries(Actions.LOGIN_FAILED).get()
        self.assertIsNone(entry.actor)
        self.assertEqual(entry.target_id, str(self.user.pk))

    def test_failed_login_for_an_unknown_account_has_no_target(self):
        self.attempt(email='inconnu@example.com', password='mauvais')
        entry = self.entries(Actions.LOGIN_FAILED).get()
        self.assertEqual(entry.target_id, '')

    def test_journal_never_stores_the_email_or_the_password(self):
        self.attempt(password='mauvais-mot-de-passe')
        self.attempt()
        for entry in AuditLog.objects.all():
            dump = f'{entry.subject} {entry.metadata} {entry.target_id} {entry.action}'
            self.assertNotIn(EMAIL, dump)
            self.assertNotIn('mauvais-mot-de-passe', dump)
            self.assertNotIn(PASSWORD, dump)

    def test_account_key_ignores_case_and_spaces(self):
        self.assertEqual(audit_service.account_key(' Audit@Example.COM '), audit_service.account_key(EMAIL))
        self.assertEqual(audit_service.account_key(None), '')
        self.assertEqual(audit_service.account_key(''), '')
        self.assertEqual(audit_service.account_key(123), '')

    def change_code(self):
        """Demande le code de changement de mot de passe et le lit dans l'e-mail envoyé."""
        import re
        from django.core import mail
        from app.core.services.password_change_service import PasswordChangeCodeService

        mail.outbox = []
        PasswordChangeCodeService().request_code(self.user)
        return re.search(r'\b(\d{6})\b', mail.outbox[-1].body).group(1)

    def test_password_change_is_recorded(self):
        client = APIClient()
        self.attempt(client=client)
        client.credentials()  # la session est dans les cookies posés par la connexion
        code = self.change_code()
        response = client.post(CHANGE_PASSWORD, {'old_password': PASSWORD, 'new_password': 'Nouveau-Mot-De-Passe-77',
                                                 'new_password_confirm': 'Nouveau-Mot-De-Passe-77', 'code': code},
                               format='json')
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(self.entries(Actions.PASSWORD_CHANGED).get().actor, self.user)
        else:  # le client de test n'envoie pas le CSRF d'une session par cookie : on passe par l'en-tête Bearer
            from rest_framework_simplejwt.tokens import RefreshToken
            bearer = APIClient()
            bearer.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.user).access_token}')
            response = bearer.post(CHANGE_PASSWORD, {'old_password': PASSWORD, 'new_password': 'Nouveau-Mot-De-Passe-77',
                                                     'new_password_confirm': 'Nouveau-Mot-De-Passe-77', 'code': code},
                                   format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(self.entries(Actions.PASSWORD_CHANGED).get().actor, self.user)


@override_settings(LOGIN_LOCKOUT_MAX_FAILURES=3, LOGIN_LOCKOUT_MINUTES=15)
class LoginLockoutTests(AuditTestCase):
    def fail(self, times, email=EMAIL):
        for _ in range(times):
            self.assertEqual(self.attempt(email=email, password='mauvais').status_code, status.HTTP_401_UNAUTHORIZED)

    def test_account_is_locked_after_the_maximum_of_failures_even_with_the_right_password(self):
        self.fail(3)
        response = self.attempt()
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response['Retry-After'], '900')
        self.assertNotIn('access_token', response.cookies)

    def test_below_the_maximum_the_account_still_works(self):
        self.fail(2)
        self.assertEqual(self.attempt().status_code, status.HTTP_200_OK)

    def test_unknown_email_is_locked_the_same_way_so_accounts_are_not_revealed(self):
        self.fail(3)
        self.fail(3, email='inconnu@example.com')
        known, unknown = self.attempt(), self.attempt(email='inconnu@example.com')
        self.assertEqual(known.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(unknown.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(known.data, unknown.data)

    def test_lock_applies_whatever_the_case_of_the_email(self):
        self.fail(3)
        self.assertEqual(self.attempt(email=EMAIL.upper()).status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_other_accounts_are_not_affected(self):
        User.objects.create_user(username='autre', email='autre@example.com', password=PASSWORD)
        self.fail(3)
        self.assertEqual(self.attempt(email='autre@example.com').status_code, status.HTTP_200_OK)

    def test_a_successful_login_resets_the_count(self):
        self.fail(2)
        self.attempt()
        self.fail(2)
        self.assertEqual(self.attempt().status_code, status.HTTP_200_OK)

    def test_lock_ends_when_failures_leave_the_window(self):
        self.fail(3)
        self.assertTrue(login_lockout.is_locked(audit_service.account_key(EMAIL)))
        AuditLog.objects.filter(action=Actions.LOGIN_FAILED).update(created_at=timezone.now() - timedelta(minutes=16))
        self.assertFalse(login_lockout.is_locked(audit_service.account_key(EMAIL)))
        self.assertEqual(self.attempt().status_code, status.HTTP_200_OK)

    def test_missing_email_is_never_locked(self):
        self.assertFalse(login_lockout.is_locked(''))


class JournalIntegrityTests(AuditTestCase):
    def test_an_entry_cannot_be_modified(self):
        entry = audit_service.record(Actions.USER_UPDATED, actor=self.user, target=self.user)
        entry.action = 'autre'
        with self.assertRaises(ValueError):
            entry.save()

    def test_actor_may_be_anonymous(self):
        from django.contrib.auth.models import AnonymousUser
        entry = audit_service.record(Actions.LOGIN_FAILED, actor=AnonymousUser())
        self.assertIsNone(entry.actor)

    def test_deleting_the_actor_keeps_the_entry(self):
        entry = audit_service.record(Actions.USER_UPDATED, actor=self.user)
        self.user.delete()
        entry.refresh_from_db()
        self.assertIsNone(entry.actor)

    def test_django_admin_exposes_the_journal_read_only(self):
        from django.contrib import admin
        model_admin = admin.site._registry[AuditLog]
        for check in (model_admin.has_add_permission, model_admin.has_change_permission, model_admin.has_delete_permission):
            self.assertFalse(check(None))


class PurgeTests(AuditTestCase):
    @override_settings(AUDIT_RETENTION_DAYS=30)
    def test_purge_deletes_only_entries_older_than_the_retention(self):
        old = audit_service.record(Actions.USER_UPDATED)
        recent = audit_service.record(Actions.USER_UPDATED)
        AuditLog.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=31))
        self.assertEqual(audit_service.purge_older_than_retention(), 1)
        self.assertFalse(AuditLog.objects.filter(pk=old.pk).exists())
        self.assertTrue(AuditLog.objects.filter(pk=recent.pk).exists())

    @override_settings(AUDIT_RETENTION_DAYS=30)
    def test_purge_command_runs_every_cleanup(self):
        out = StringIO()
        call_command('purge_expired_data', stdout=out)
        text = out.getvalue()
        self.assertIn('challenge(s) de réinitialisation supprimé(s)', text)
        self.assertIn("entrée(s) du journal d'audit supprimée(s)", text)
