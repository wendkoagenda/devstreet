"""E-mails transactionnels : socle (envoi différé, gabarits), compte, mot de passe, marketplace."""
import re
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from app.core.models import PasswordResetChallenge
from app.core.services import email_catalog
from app.core.services.email_service import EmailService, mask_email
from app.core.services.forgot_password_service import ForgotPasswordService
from app.core.services.oauth_service import OAuthProfile, resolve_user
from app.core.services.password_change_service import PasswordChangeCodeService, PasswordChangeError
from app.marketplace.factories import make_company, make_offer, make_profil, make_user
from app.marketplace.services.invitation_service import InvitationService
from app.marketplace.services.market_service import MarketService
from app.marketplace.services.network_service import NetworkService

User = get_user_model()

FAST = dict(
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    EMAIL_SEND_IN_THREAD=False,
    FRONTEND_URL='http://app.devstreet.test',
)
PASSWORD = 'MotDePasse-Solide-42'
CODE_RE = re.compile(r'\b(\d{6})\b')


def html_of(message) -> str:
    """Version HTML d'un e-mail (alternative attachée au message)."""
    return next(content for content, mimetype in message.alternatives if mimetype == 'text/html')


# ── Socle ───────────────────────────────────────────────────────────────────

@override_settings(**FAST)
class EmailFoundationTests(TestCase):
    def test_chaque_email_du_catalogue_se_rend_en_html_et_en_texte(self):
        out = StringIO()
        call_command('preview_emails', '--out', self._tmp(), stdout=out)
        self.assertIn('10 aperçu(s)', out.getvalue())

    def _tmp(self):
        import tempfile

        path = tempfile.mkdtemp(prefix='devstreet-emails-')
        self.addCleanup(lambda: __import__('shutil').rmtree(path, ignore_errors=True))
        return path

    def test_le_texte_n_est_pas_echappe_et_le_html_l_est(self):
        spec = email_catalog.application_received(
            'a@example.com', 'Moussa', 'Ada <script>', '', "Offre d'été", 3, "J'ai <b>hâte</b>"
        )
        text, html = EmailService().render(spec.template_name, spec.context)
        self.assertIn("J'ai <b>hâte</b>", text)
        self.assertIn('Ada &lt;script&gt;', html)
        self.assertNotIn('<script>', html)
        self.assertIn('http://app.devstreet.test/marketplace/my-offers/3', html)

    def test_rien_n_est_envoye_si_la_transaction_est_annulee(self):
        from django.db import transaction

        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    EmailService().queue(email_catalog.welcome('a@example.com', 'Ada'))
                    raise RuntimeError('annulation')
            except RuntimeError:
                pass
        self.assertEqual(len(mail.outbox), 0)

    def test_un_echec_d_envoi_est_journalise_sans_lever(self):
        with patch.object(EmailService, 'send', side_effect=ConnectionError('SMTP injoignable')):
            with self.assertLogs('app.core.services.email_service', level='ERROR') as logs:
                with self.captureOnCommitCallbacks(execute=True):
                    EmailService().queue(email_catalog.welcome('ada@example.com', 'Ada'))
        self.assertIn('a***@example.com', logs.output[0])
        self.assertNotIn('ada@example.com', logs.output[0])

    def test_masquage_de_l_adresse(self):
        self.assertEqual(mask_email('ada@example.com'), 'a***@example.com')
        self.assertEqual(mask_email('invalide'), '***')


# ── M1 : bienvenue ──────────────────────────────────────────────────────────

@override_settings(**FAST)
class WelcomeEmailTests(TestCase):
    def register(self):
        cache.clear()
        with self.captureOnCommitCallbacks(execute=True):
            return APIClient().post('/api/auth/register', {
                'email': 'nouveau@example.com', 'username': 'ada_nouvelle', 'first_name': 'Ada', 'last_name': 'L',
                'password': PASSWORD, 'password_confirm': PASSWORD,
            }, format='json')

    def test_inscription_envoie_un_seul_email_de_bienvenue(self):
        response = self.register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['nouveau@example.com'])
        self.assertEqual(message.subject, 'Bienvenue sur DevStreet')
        self.assertIn('Ada', message.body)
        self.assertIn('http://app.devstreet.test/onboarding', html_of(message))

    def test_smtp_injoignable_n_empeche_pas_l_inscription(self):
        with patch.object(EmailService, 'send', side_effect=ConnectionError('SMTP injoignable')):
            response = self.register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='nouveau@example.com').exists())

    def test_oauth_nouveau_compte_bienvenue_puis_reconnexion_sans_email(self):
        profile = OAuthProfile(provider='google', provider_user_id='g-1', email='oauth@example.com',
                               first_name='Grace', last_name='H')
        with self.captureOnCommitCallbacks(execute=True):
            resolve_user(profile)
        self.assertEqual([m.subject for m in mail.outbox], ['Bienvenue sur DevStreet'])
        with self.captureOnCommitCallbacks(execute=True):
            resolve_user(profile)
        self.assertEqual(len(mail.outbox), 1)


# ── M2 : sécurité du compte ─────────────────────────────────────────────────

@override_settings(**FAST)
class AccountSecurityEmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='secu@example.com', username='secu', password=PASSWORD, first_name='Sam', last_name='U'
        )

    def test_code_mot_de_passe_oublie_sur_le_gabarit_commun(self):
        ForgotPasswordService().request_password_reset('secu@example.com')
        message = mail.outbox[-1]
        code = CODE_RE.search(message.body).group(1)
        self.assertIn(code, html_of(message))
        self.assertIn('15 minutes', message.body)
        self.assertIn('DevStreet', html_of(message))

    def test_reinitialisation_envoie_l_alerte_mot_de_passe_modifie(self):
        service = ForgotPasswordService()
        service.request_password_reset('secu@example.com')
        code = CODE_RE.search(mail.outbox[-1].body).group(1)
        token = service.verify_reset_code('secu@example.com', code)
        with self.captureOnCommitCallbacks(execute=True):
            service.confirm_password_reset(token, 'Un-Nouveau-Mot-De-Passe-99')
        self.assertEqual(mail.outbox[-1].subject, 'Votre mot de passe a été modifié')
        self.assertIn('http://app.devstreet.test/forgot-password', html_of(mail.outbox[-1]))

    def test_lier_un_fournisseur_a_un_compte_existant_n_envoie_rien(self):
        profile = OAuthProfile(provider='github', provider_user_id='gh-7', email='secu@example.com',
                               first_name='Sam', last_name='U')
        with self.captureOnCommitCallbacks(execute=True):
            resolve_user(profile)
        self.assertEqual(mail.outbox, [])


# ── M3 : changement de mot de passe par code ────────────────────────────────

@override_settings(**FAST)
class PasswordChangeCodeTests(TestCase):
    URL = '/api/auth/change-password'
    CODE_URL = '/api/auth/change-password/code'

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.user = User.objects.create_user(
            email='change@example.com', username='change', password=PASSWORD, first_name='Lin', last_name='U'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def request_code(self):
        mail.outbox = []
        response = self.client.post(self.CODE_URL, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return CODE_RE.search(mail.outbox[-1].body).group(1)

    def change(self, code, new='Nouveau-Mot-De-Passe-77'):
        payload = {'old_password': PASSWORD, 'new_password': new, 'new_password_confirm': new}
        if code is not None:
            payload['code'] = code
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(self.URL, payload, format='json')

    def test_sans_code_le_changement_est_refuse(self):
        response = self.change(None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_code_faux_refuse(self):
        self.request_code()
        response = self.change('000000')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_parcours_complet_puis_code_a_usage_unique(self):
        code = self.request_code()
        self.assertEqual(mail.outbox[-1].subject, 'Confirmez le changement de votre mot de passe')
        response = self.change(code)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Nouveau-Mot-De-Passe-77'))
        self.assertEqual(mail.outbox[-1].subject, 'Votre mot de passe a été modifié')
        # Le même code ne sert pas deux fois
        self.client.force_authenticate(self.user)
        again = self.client.post(self.URL, {
            'old_password': 'Nouveau-Mot-De-Passe-77', 'new_password': 'Encore-Un-Autre-88',
            'new_password_confirm': 'Encore-Un-Autre-88', 'code': code,
        }, format='json')
        self.assertEqual(again.status_code, status.HTTP_400_BAD_REQUEST)

    def test_un_code_de_reinitialisation_ne_sert_pas_au_changement(self):
        ForgotPasswordService().request_password_reset('change@example.com')
        reset_code = CODE_RE.search(mail.outbox[-1].body).group(1)
        response = self.change(reset_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mauvais_ancien_mot_de_passe_ne_consomme_pas_le_code(self):
        code = self.request_code()
        bad = self.client.post(self.URL, {
            'old_password': 'faux', 'new_password': 'Nouveau-Mot-De-Passe-77',
            'new_password_confirm': 'Nouveau-Mot-De-Passe-77', 'code': code,
        }, format='json')
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.change(code).status_code, status.HTTP_200_OK)

    def test_nouvelle_demande_trop_rapprochee_refusee(self):
        self.request_code()
        response = self.client.post(self.CODE_URL, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_nouvelle_demande_invalide_le_code_precedent(self):
        first = self.request_code()
        PasswordResetChallenge.objects.filter(user=self.user).update(
            created_at=PasswordResetChallenge.objects.get(user=self.user).created_at.replace(year=2000)
        )
        second = self.request_code()
        if first != second:
            self.assertEqual(self.change(first).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.change(second).status_code, status.HTTP_200_OK)

    def test_trop_de_tentatives_bloque_le_code(self):
        code = self.request_code()
        wrong = '111111' if code != '111111' else '222222'
        for _ in range(5):
            self.change(wrong)
        self.assertEqual(self.change(code).status_code, status.HTTP_400_BAD_REQUEST)

    def test_compte_sans_mot_de_passe_refuse_avec_message(self):
        self.user.set_unusable_password()
        self.user.save()
        with self.assertRaises(PasswordChangeError):
            PasswordChangeCodeService().request_code(self.user)

    def test_echec_d_envoi_du_code_est_signale(self):
        with patch.object(EmailService, 'send', side_effect=ConnectionError('SMTP injoignable')):
            response = self.client.post(self.CODE_URL, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertFalse(PasswordResetChallenge.objects.filter(user=self.user).exists())


# ── M4 / M5 : candidature et décision ───────────────────────────────────────

@override_settings(**FAST)
class ApplicationEmailTests(TestCase):
    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by, name='Kora Fintech')
        self.owner = make_user(email='owner@example.com', first_name='Moussa')
        self.member = make_user(email='member@example.com', first_name='Awa')
        make_profil(self.by, user=self.owner, company=self.company, is_company_owner=True)
        recruiter = make_profil(self.by, user=self.member, company=self.company)
        self.offer = make_offer(self.by, company=self.company, recruiter=recruiter, title='Dev mobile', status='open')
        self.candidate = make_user(email='candidat@example.com', first_name='Ada', last_name='Lovelace')
        make_profil(self.by, user=self.candidate)

    def apply(self):
        with self.captureOnCommitCallbacks(execute=True):
            return MarketService.apply(self.candidate, self.offer.id, 'Bonjour, je suis motivée.')

    def test_candidature_accuse_au_candidat_et_alerte_a_chaque_membre(self):
        self.apply()
        by_recipient = {tuple(m.to): m for m in mail.outbox}
        self.assertEqual(set(by_recipient), {('candidat@example.com',), ('owner@example.com',), ('member@example.com',)})
        self.assertEqual(by_recipient[('candidat@example.com',)].subject, 'Candidature envoyée : Dev mobile')
        received = by_recipient[('owner@example.com',)]
        self.assertEqual(received.subject, 'Nouvelle candidature : Dev mobile')
        self.assertIn('Ada Lovelace', received.body)
        self.assertIn('je suis motivée', received.body)
        self.assertIn(f'/marketplace/my-offers/{self.offer.id}', html_of(received))
        for message in mail.outbox:
            self.assertEqual(len(message.to), 1)  # aucune adresse d'un autre destinataire
            self.assertEqual(message.cc, [])
            self.assertEqual(message.bcc, [])

    def test_candidature_refusee_par_le_serveur_n_envoie_rien(self):
        self.apply()
        mail.outbox = []
        from rest_framework.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            self.apply()  # doublon
        self.assertEqual(mail.outbox, [])

    def decide(self, decision):
        candidature = self.offer.candidatures.get()
        with self.captureOnCommitCallbacks(execute=True):
            MarketService.decide(self.member, candidature.id, decision)

    def test_acceptation_et_refus(self):
        self.apply()
        mail.outbox = []
        self.decide('rejected')
        self.assertEqual([m.subject for m in mail.outbox], ['Votre candidature : Dev mobile'])
        self.assertEqual(mail.outbox[0].to, ['candidat@example.com'])
        self.decide('rejected')  # même décision renvoyée : pas de second e-mail
        self.assertEqual(len(mail.outbox), 1)
        self.decide('accepted')
        self.assertEqual(mail.outbox[-1].subject, 'Votre candidature a été acceptée : Dev mobile')

    def test_presélection_n_envoie_rien(self):
        self.apply()
        mail.outbox = []
        self.decide('shortlisted')
        self.assertEqual(mail.outbox, [])


# ── M6 : réseau et équipe ───────────────────────────────────────────────────

@override_settings(**FAST)
class NetworkAndTeamEmailTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.by = make_user()
        self.ada = make_user(email='ada@example.com', first_name='Ada', last_name='L')
        self.grace = make_user(email='grace@example.com', first_name='Grace', last_name='H')
        self.ada_profil = make_profil(self.by, user=self.ada)
        self.grace_profil = make_profil(self.by, user=self.grace)

    def like(self, user, target):
        with self.captureOnCommitCallbacks(execute=True):
            return NetworkService.swipe(user, target.id, 'like', 'network')

    def test_like_reciproque_previent_les_deux_membres(self):
        self.like(self.ada, self.grace_profil)
        self.assertEqual(mail.outbox, [])  # pas encore réciproque
        result = self.like(self.grace, self.ada_profil)
        self.assertTrue(result['matched'])
        self.assertEqual({m.to[0] for m in mail.outbox}, {'ada@example.com', 'grace@example.com'})
        to_ada = next(m for m in mail.outbox if m.to == ['ada@example.com'])
        self.assertIn('Grace H', to_ada.subject)
        self.assertIn(f'/marketplace/profiles/{self.grace_profil.id}', html_of(to_ada))

    def test_relation_refaite_dans_l_heure_sans_doublon(self):
        self.like(self.ada, self.grace_profil)
        self.like(self.grace, self.ada_profil)
        with self.captureOnCommitCallbacks(execute=True):
            NetworkService.undo_last_swipe(self.grace, 'network')
        self.like(self.grace, self.ada_profil)
        self.assertEqual(len(mail.outbox), 2)

    def test_invitation_d_entreprise_sur_le_gabarit_commun(self):
        company = make_company(self.by, name='Kora Fintech')
        make_profil(self.by, user=self.ada, company=company, is_company_owner=True)
        with self.captureOnCommitCallbacks(execute=True):
            data = InvitationService.create(self.ada, 'invite@example.com')
        message = mail.outbox[-1]
        self.assertEqual(message.to, ['invite@example.com'])
        self.assertEqual(message.subject, 'Invitation à rejoindre Kora Fintech sur DevStreet')
        self.assertIn(data['link'], html_of(message))

    def test_echec_d_envoi_de_l_invitation_garde_le_lien(self):
        company = make_company(self.by)
        make_profil(self.by, user=self.ada, company=company, is_company_owner=True)
        with patch.object(EmailService, 'send', side_effect=ConnectionError('SMTP injoignable')):
            with self.captureOnCommitCallbacks(execute=True):
                data = InvitationService.create(self.ada, 'invite@example.com')
        self.assertTrue(data['link'])
