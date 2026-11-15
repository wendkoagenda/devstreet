"""Tests de l'onboarding par type de compte : choix du type, rôles, droits et rattrapage des comptes existants."""
import importlib

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from app.core.account_types import ROLE_DEV, ROLE_ENTREPRISE, LEGACY_MEMBER_ROLE
from app.core.models import Role
from app.marketplace.models import Profil
from app.marketplace.services.me_service import MeService

User = get_user_model()

FAST_HASHER = ['django.contrib.auth.hashers.MD5PasswordHasher']


def make_user(email='membre@example.com', username='membre'):
    return User.objects.create_user(
        email=email, username=username, password='motdepasse123', first_name='Mem', last_name='Bre'
    )


@override_settings(PASSWORD_HASHERS=FAST_HASHER)
class AccountTypeApiTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def _choose(self, account_type):
        return self.client.post('/api/auth/account-type', {'account_type': account_type}, format='json')

    def test_nouveau_compte_sans_type_ni_role_doit_passer_par_l_onboarding(self):
        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data['user']
        self.assertEqual(user['account_type'], '')
        self.assertTrue(user['onboarding_required'])
        self.assertFalse(user['is_admin'])
        self.assertEqual(user['roles'], [])

    def test_choix_dev_donne_le_role_dev_sans_droit_d_administration(self):
        response = self._choose('dev')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['account_type'], 'dev')
        self.assertFalse(response.data['user']['onboarding_required'])
        self.assertEqual(response.data['user']['roles'], [ROLE_DEV])
        permissions = set(response.data['permissions'])
        self.assertIn('projects.create', permissions)
        self.assertIn('publications.view', permissions)
        for code in ('companies.view', 'profils.delete', 'users.view', 'roles.view'):
            self.assertNotIn(code, permissions)

    def test_choix_entreprise_se_limite_a_la_marketplace_et_a_la_messagerie(self):
        response = self._choose('entreprise')
        self.assertEqual(response.data['user']['roles'], [ROLE_ENTREPRISE])
        permissions = set(response.data['permissions'])
        self.assertIn('messages.view', permissions)
        for code in ('publications.view', 'projects.create', 'espaces.view', 'companies.view', 'users.view'):
            self.assertNotIn(code, permissions)

    def test_choix_les_deux_cumule_les_deux_roles(self):
        response = self._choose('both')
        self.assertEqual(response.data['user']['account_type'], 'both')
        self.assertCountEqual(response.data['user']['roles'], [ROLE_DEV, ROLE_ENTREPRISE])

    def test_ajout_d_un_type_ne_retire_jamais_l_autre(self):
        self._choose('dev')
        response = self._choose('entreprise')
        self.assertEqual(response.data['user']['account_type'], 'both')
        self.assertCountEqual(response.data['user']['roles'], [ROLE_DEV, ROLE_ENTREPRISE])
        # Redemander un seul type ne retire rien
        response = self._choose('dev')
        self.assertEqual(response.data['user']['account_type'], 'both')

    def test_choix_est_idempotent(self):
        self._choose('dev')
        self._choose('dev')
        self.assertEqual(self.user.roles.filter(name=ROLE_DEV).count(), 1)

    def test_type_invalide_refuse(self):
        self.assertEqual(self._choose('admin').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self._choose('').status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.account_type, '')

    def test_non_authentifie_refuse(self):
        response = APIClient().post('/api/auth/account-type', {'account_type': 'dev'}, format='json')
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_un_membre_ne_peut_pas_lister_utilisateurs_ni_roles(self):
        self._choose('both')
        self.assertEqual(self.client.get('/api/v1/users').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get('/api/v1/roles').status_code, status.HTTP_403_FORBIDDEN)

    def test_un_membre_ne_peut_pas_utiliser_l_administration_marketplace(self):
        self._choose('both')
        self.assertEqual(self.client.get('/api/v1/companies').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get('/api/v1/profils').status_code, status.HTTP_403_FORBIDDEN)

    def test_administrateur_exclu_de_l_onboarding(self):
        admin_role = Role.objects.get_or_create(name='Admin')[0]
        admin = make_user('admin2@example.com', 'admin2')
        admin.roles.add(admin_role)
        client = APIClient()
        client.force_authenticate(admin)
        user = client.get('/api/auth/me').data['user']
        self.assertTrue(user['is_admin'])
        self.assertFalse(user['onboarding_required'])


@override_settings(PASSWORD_HASHERS=FAST_HASHER)
class AccountTypeFollowsProfilesTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_creer_un_profil_dev_donne_le_type_dev(self):
        MeService.create_profil(self.user, {'country': 'FR'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.account_type, 'dev')
        self.assertTrue(self.user.roles.filter(name=ROLE_DEV).exists())

    def test_creer_une_entreprise_donne_le_type_entreprise(self):
        MeService.create_company(self.user, {'name': 'Acme', 'sector': 'fintech', 'country': 'FR'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.account_type, 'entreprise')
        self.assertTrue(self.user.roles.filter(name=ROLE_ENTREPRISE).exists())

    def test_profil_dev_puis_entreprise_donne_les_deux(self):
        MeService.create_profil(self.user, {'country': 'FR'})
        MeService.create_company(self.user, {'name': 'Acme', 'sector': 'fintech', 'country': 'FR'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.account_type, 'both')


@override_settings(PASSWORD_HASHERS=FAST_HASHER)
class BackfillAccountTypesTests(TestCase):
    def _run_backfill(self):
        module = importlib.import_module('app.marketplace.migrations.0009_backfill_account_types')
        module.backfill_account_types(django_apps, None)

    def setUp(self):
        self.legacy = Role.objects.get_or_create(name=LEGACY_MEMBER_ROLE)[0]

    def _member(self, email, username):
        user = make_user(email, username)
        user.roles.add(self.legacy)
        return user

    def test_rattrapage_selon_les_profils_existants(self):
        dev = self._member('dev@example.com', 'devuser')
        Profil.objects.create(
            user=dev, type=Profil.TYPE_DEV, slug='dev-user', country='FR', created_by=dev.id, updated_by=dev.id
        )
        recruteur = self._member('rec@example.com', 'recruteur')
        MeService.create_company(recruteur, {'name': 'Acme', 'sector': 'fintech', 'country': 'FR'})
        # create_company a déjà posé le type ; on le remet à zéro pour tester le rattrapage seul
        recruteur.account_type = ''
        recruteur.roles.clear()
        recruteur.roles.add(self.legacy)
        recruteur.save()
        vide = self._member('vide@example.com', 'videuser')

        self._run_backfill()

        for user in (dev, recruteur, vide):
            user.refresh_from_db()
        self.assertEqual(dev.account_type, 'dev')
        self.assertEqual(list(dev.roles.values_list('name', flat=True)), [ROLE_DEV])
        self.assertEqual(recruteur.account_type, 'entreprise')
        self.assertEqual(list(recruteur.roles.values_list('name', flat=True)), [ROLE_ENTREPRISE])
        # Sans profil : plus de rôle, type vide, donc assistant à la prochaine connexion
        self.assertEqual(vide.account_type, '')
        self.assertEqual(vide.roles.count(), 0)

    def test_les_administrateurs_ne_sont_pas_touches(self):
        admin_role = Role.objects.get_or_create(name='Admin')[0]
        admin = make_user('adm@example.com', 'adm')
        admin.roles.add(admin_role, self.legacy)
        superuser = User.objects.create_superuser(username='root', email='root@example.com', password='x')

        self._run_backfill()

        admin.refresh_from_db()
        superuser.refresh_from_db()
        self.assertEqual(admin.account_type, '')
        self.assertTrue(admin.roles.filter(name=LEGACY_MEMBER_ROLE).exists())
        self.assertEqual(superuser.account_type, '')


@override_settings(PASSWORD_HASHERS=FAST_HASHER)
class BackfillWithHistoricalModelsTests(TestCase):
    """Le rattrapage tourne avec les modèles historiques (état des migrations), pas les vrais modèles."""

    def test_rattrapage_avec_l_etat_historique_des_migrations(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        legacy = Role.objects.get_or_create(name=LEGACY_MEMBER_ROLE)[0]
        membre = make_user('hist@example.com', 'histuser')
        membre.roles.add(legacy)
        Profil.objects.create(
            user=membre, type=Profil.TYPE_DEV, slug='hist-user', country='FR',
            created_by=membre.id, updated_by=membre.id,
        )

        executor = MigrationExecutor(connection)
        state = executor.loader.project_state(
            [('core', '0009_user_account_type'), ('marketplace', '0008_profil_cv_settings')]
        )
        module = importlib.import_module('app.marketplace.migrations.0009_backfill_account_types')
        module.backfill_account_types(state.apps, None)

        membre.refresh_from_db()
        self.assertEqual(membre.account_type, 'dev')
        self.assertEqual(list(membre.roles.values_list('name', flat=True)), [ROLE_DEV])
