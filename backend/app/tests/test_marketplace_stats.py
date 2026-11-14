"""Tests des petites statistiques des pages de la marketplace (GET /marketplace/me/stats?scope=…)."""
from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from app.marketplace.factories import (
    make_availability,
    make_candidature,
    make_company,
    make_connection,
    make_offer,
    make_profil,
    make_swipe,
    make_user,
)
from app.marketplace.models import Swipe
from app.marketplace.services.scoring import build_contexts, compute_score
from app.tests.test_marketplace_market import login


class StatsBase(APITestCase):
    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by, name="Faso Pay")
        self.recruiter_user = make_user(first_name="Fatou", last_name="Sow")
        # Membre qui n'a qu'un profil entreprise
        self.entreprise = make_profil(self.by, user=self.recruiter_user, company=self.company, is_company_owner=True)
        self.dev_user = make_user(first_name="Awa", last_name="Koné")
        self.dev = make_profil(self.by, user=self.dev_user, headline="Dev React")

    def stats(self, user, scope):
        login(self.client, user)
        return self.client.get(f"/api/v1/marketplace/me/stats?scope={scope}")


class RecruiterStatsTests(StatsBase):
    def setUp(self):
        super().setUp()
        self.open_offer = make_offer(
            self.by, company=self.company, recruiter=self.entreprise, status="open", views_count=40
        )
        make_offer(self.by, company=self.company, recruiter=self.entreprise, status="draft", views_count=0)
        make_offer(self.by, company=self.company, recruiter=self.entreprise, status="closed", views_count=15)
        make_candidature(self.by, offer=self.open_offer, profil=make_profil(self.by), status="sent")
        make_candidature(self.by, offer=self.open_offer, profil=make_profil(self.by), status="shortlisted")
        # Une candidature à une autre entreprise ne compte pas
        make_candidature(self.by, offer=make_offer(self.by, status="open"), profil=make_profil(self.by), status="sent")

    def test_offers_compte_par_statut_a_traiter_et_vues(self):
        data = self.stats(self.recruiter_user, "offers").data
        self.assertEqual((data["open"], data["draft"], data["closed"], data["total"]), (1, 1, 1, 3))
        self.assertEqual(data["to_process"], 1)
        self.assertEqual(data["views_total"], 55)

    def test_les_scopes_entreprise_sont_refuses_sans_profil_entreprise(self):
        for scope in ("offers", "pool"):
            self.assertEqual(self.stats(self.dev_user, scope).status_code, 403, scope)

    def test_vivier(self):
        talent = make_profil(self.by)
        old = make_profil(self.by, is_open_to_work=False)
        make_swipe(self.by, author=self.entreprise, target=talent, direction="like", context="recruit")
        old_swipe = make_swipe(self.by, author=self.entreprise, target=old, direction="like", context="recruit")
        Swipe.objects.filter(pk=old_swipe.pk).update(created_at=timezone.now() - timedelta(days=30))
        make_swipe(self.by, author=self.entreprise, target=make_profil(self.by), direction="pass", context="recruit")

        pool = self.stats(self.recruiter_user, "pool").data
        self.assertEqual((pool["total"], pool["this_week"], pool["open_to_work"]), (2, 1, 1))


class DevStatsTests(StatsBase):
    def test_applications_par_statut_et_missions(self):
        make_candidature(self.by, profil=self.dev, status="sent")
        make_candidature(self.by, profil=self.dev, status="accepted")
        today = timezone.localdate()
        make_availability(
            self.by, profil=self.dev, source="mission", status="busy",
            start_date=today + timedelta(days=5), end_date=today + timedelta(days=20),
        )
        data = self.stats(self.dev_user, "applications").data
        self.assertEqual((data["sent"], data["accepted"], data["total"]), (1, 1, 2))
        self.assertEqual(data["upcoming_missions"], 1)

    def test_cv_expose_la_completude(self):
        data = self.stats(self.dev_user, "cv").data["completeness"]
        self.assertIn("percent", data)
        self.assertTrue(any(item["key"] == "bio" for item in data["missing"]))

    def test_disponibilite_et_profil_resume(self):
        data = self.stats(self.dev_user, "availability").data
        self.assertIsNone(data["current"])
        self.assertEqual(data["periods_count"], 0)
        make_connection(self.by, profil_a=self.dev, profil_b=make_profil(self.by))
        summary = self.stats(self.dev_user, "profile").data
        self.assertEqual(summary["connections_count"], 1)
        self.assertIn("rating_avg", summary["reputation"])

    def test_scopes_dev_refuses_sans_profil_dev(self):
        for scope in ("applications", "availability", "cv", "profile"):
            self.assertEqual(self.stats(self.recruiter_user, scope).status_code, 403, scope)


class GeneralStatsTests(StatsBase):
    def test_explorer_compte_les_offres_ouvertes_hors_son_entreprise(self):
        make_offer(self.by, company=self.company, recruiter=self.entreprise, status="open")
        make_offer(self.by, status="open")
        make_offer(self.by, status="draft")
        make_candidature(self.by, profil=self.dev, offer=make_offer(self.by, status="open"))
        dev_data = self.stats(self.dev_user, "explore").data
        self.assertEqual(dev_data["open_offers"], 3)
        self.assertEqual(dev_data["applications_sent"], 1)
        self.assertIsNotNone(dev_data["well_matched"])
        # Un membre entreprise seul : ses propres offres sont exclues, pas de score
        company_data = self.stats(self.recruiter_user, "explore").data
        self.assertEqual(company_data["open_offers"], 2)
        self.assertIsNone(company_data["well_matched"])

    def test_reseau_compte_les_connexions_des_deux_profils(self):
        make_connection(self.by, profil_a=self.dev, profil_b=self.entreprise)
        self.assertEqual(self.stats(self.dev_user, "network").data["connections"], 1)
        self.assertEqual(self.stats(self.recruiter_user, "network").data["connections"], 1)

    def test_reseau_demandes_en_attente_et_recues(self):
        autre = make_profil(self.by)
        demandeur = make_profil(self.by)
        # J'ai proposé à `autre` (pas de réponse) ; `demandeur` m'a proposé (je n'ai pas répondu)
        make_swipe(self.by, author=self.dev, target=autre, direction="like", context="network")
        make_swipe(self.by, author=demandeur, target=self.dev, direction="like", context="network")
        data = self.stats(self.dev_user, "network").data
        self.assertEqual((data["connections"], data["pending_sent"], data["pending_received"]), (0, 1, 1))
        # Je réponds à `demandeur` : la demande reçue disparaît
        make_swipe(self.by, author=self.dev, target=demandeur, direction="pass", context="network")
        self.assertEqual(self.stats(self.dev_user, "network").data["pending_received"], 0)

    def test_scope_invalide_et_membre_sans_profil(self):
        self.assertEqual(self.stats(self.dev_user, "nope").status_code, 400)
        self.assertEqual(self.stats(make_user(), "network").status_code, 403)


class FreeByDefaultTests(StatsBase):
    """Sans période occupée, on est disponible : seules les plages occupées se déclarent."""

    def _availability_score(self, profil, offer):
        ctx = build_contexts([profil])[profil.id]
        item = next(row for row in compute_score(offer, profil, ctx)["breakdown"] if row["key"] == "availability")
        return item

    def test_sans_periode_le_score_de_disponibilite_est_complet(self):
        today = timezone.localdate()
        offer = make_offer(
            self.by, status="open", start_date=today + timedelta(days=10), contract_duration=2
        )
        item = self._availability_score(self.dev, offer)
        self.assertEqual(item["score"], item["max"])

    def test_periode_occupee_sur_les_dates_de_l_offre_donne_zero(self):
        today = timezone.localdate()
        offer = make_offer(self.by, status="open", start_date=today + timedelta(days=10), contract_duration=2)
        make_availability(
            self.by, profil=self.dev, status="busy",
            start_date=today + timedelta(days=5), end_date=today + timedelta(days=40),
        )
        self.assertEqual(self._availability_score(self.dev, offer)["score"], 0)

    def test_prochaine_disponibilite_apres_les_periodes_occupees_qui_s_enchainent(self):
        today = timezone.localdate()
        make_availability(
            self.by, profil=self.dev, status="busy",
            start_date=today - timedelta(days=1), end_date=today + timedelta(days=9),
        )
        make_availability(
            self.by, profil=self.dev, status="leave",
            start_date=today + timedelta(days=10), end_date=today + timedelta(days=20),
        )
        data = self.stats(self.dev_user, "availability").data
        self.assertEqual(data["current"]["status"], "busy")
        self.assertEqual(data["next_available_start"], (today + timedelta(days=21)).isoformat())

    def test_libre_aujourd_hui_pas_de_prochaine_disponibilite_a_annoncer(self):
        today = timezone.localdate()
        make_availability(
            self.by, profil=self.dev, status="busy",
            start_date=today + timedelta(days=30), end_date=today + timedelta(days=40),
        )
        data = self.stats(self.dev_user, "availability").data
        self.assertIsNone(data["current"])
        self.assertIsNone(data["next_available_start"])
