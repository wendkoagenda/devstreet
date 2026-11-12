"""Tableau de bord marketplace : indicateurs du candidat et du recruteur."""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from app.marketplace.factories import (
    make_availability,
    make_candidature,
    make_company,
    make_connection,
    make_experience,
    make_offer,
    make_profil,
    make_profil_skill,
    make_review,
    make_skill,
    make_swipe,
    make_user,
)
from app.marketplace.models import Candidature
from app.marketplace.services.dashboard_service import DashboardService
from app.tests.test_marketplace_market import login


class DashboardBase(APITestCase):
    def setUp(self):
        self.by = make_user()
        self.today = timezone.localdate()
        self.company = make_company(self.by, name="Faso Pay")
        self.recruiter_user = make_user(first_name="Fatou", last_name="Sow")
        self.recruiter = make_profil(self.by, user=self.recruiter_user, company=self.company, is_company_owner=True)
        self.dev_user = make_user(first_name="Awa", last_name="Koné")
        self.dev = make_profil(self.by, user=self.dev_user, headline="Dev React")

    def get(self, user):
        login(self.client, user)
        return self.client.get("/api/v1/marketplace/me/dashboard")


class CandidateDashboardTests(DashboardBase):
    def test_requires_profil_and_auth(self):
        self.assertEqual(self.get(make_user()).status_code, 403)
        self.client.credentials()
        self.assertEqual(self.client.get("/api/v1/marketplace/me/dashboard").status_code, 401)

    def test_new_profile_has_zeroes_and_no_recruiter_block(self):
        data = self.get(self.dev_user).data
        self.assertEqual(data["profil"]["name"], "Awa Koné")
        self.assertIsNone(data["recruiter"])
        self.assertEqual(data["candidate"]["counts"], {"sent": 0, "shortlisted": 0, "accepted": 0, "rejected": 0, "total": 0})
        self.assertEqual(data["connections_count"], 0)
        self.assertIsNone(data["reputation"]["rating_avg"])
        self.assertIsNone(data["availability"]["current"])

    def test_completeness_counts_filled_items(self):
        empty = self.get(self.dev_user).data["completeness"]
        keys = {item["key"] for item in empty["missing"]}
        self.assertTrue({"bio", "skills", "experiences", "links", "daily_rate"} <= keys)
        self.assertNotIn("headline", keys)
        self.dev.bio = "Présentation"
        self.dev.github_url = "https://github.com/awa"
        self.dev.daily_rate = 20000
        self.dev.languages = [{"language": "Français"}]
        self.dev.save()
        for _ in range(3):
            make_profil_skill(self.by, profil=self.dev, skill=make_skill(self.by), level=3)
        make_experience(self.by, profil=self.dev)
        full = self.get(self.dev_user).data["completeness"]
        self.assertEqual((full["percent"], full["missing"]), (100, []))

    def test_candidature_counts_recent_and_missions(self):
        offer = make_offer(self.by, company=self.company, recruiter=self.recruiter, status="open", title="Dev mobile")
        make_candidature(self.by, offer=offer, profil=self.dev, status="accepted")
        for status in ("sent", "rejected"):
            make_candidature(self.by, offer=make_offer(self.by, status="open"), profil=self.dev, status=status)
        make_availability(
            self.by, profil=self.dev, source="mission", status="busy", note="Mission : Dev mobile",
            start_date=self.today + timedelta(days=10), end_date=self.today + timedelta(days=100),
        )
        data = self.get(self.dev_user).data["candidate"]
        self.assertEqual((data["counts"]["total"], data["counts"]["accepted"], data["counts"]["sent"]), (3, 1, 1))
        self.assertEqual(len(data["recent"]), 3)
        self.assertIn("offer", data["recent"][0])
        self.assertEqual([row["note"] for row in data["upcoming_missions"]], ["Mission : Dev mobile"])

    def test_recommended_offers_are_scored_and_limited(self):
        for _ in range(5):
            make_offer(self.by, status="open")
        data = self.get(self.dev_user).data["candidate"]["recommended_offers"]
        self.assertEqual(len(data), 3)
        self.assertTrue(all("score" in row for row in data))

    def test_availability_prefers_the_most_constraining_period(self):
        make_availability(self.by, profil=self.dev, status="available", start_date=self.today - timedelta(days=5), end_date=self.today + timedelta(days=30))
        make_availability(self.by, profil=self.dev, status="busy", source="mission", start_date=self.today, end_date=self.today + timedelta(days=10))
        make_availability(self.by, profil=self.dev, status="partial", start_date=self.today + timedelta(days=40), end_date=self.today + timedelta(days=60))
        data = self.get(self.dev_user).data["availability"]
        self.assertEqual(data["current"]["status"], "busy")
        self.assertEqual(data["current"]["source"], "mission")
        self.assertEqual(data["next_available_start"], (self.today + timedelta(days=40)).isoformat())

    def test_reputation_ignores_private_reviews_and_connections_count_matched(self):
        make_review(self.by, target=self.dev, rating=5, is_public=True)
        make_review(self.by, target=self.dev, rating=4, is_public=True)
        make_review(self.by, target=self.dev, rating=1, is_public=False)
        other = make_profil(self.by)
        make_connection(self.by, profil_a=self.dev, profil_b=other, status="matched")
        make_connection(self.by, profil_a=make_profil(self.by), profil_b=self.dev, status="blocked")
        data = self.get(self.dev_user).data
        self.assertEqual((data["reputation"]["rating_avg"], data["reputation"]["reviews_count"]), (4.5, 2))
        self.assertEqual(data["connections_count"], 1)

    def test_only_own_data_is_exposed(self):
        make_candidature(self.by, profil=make_profil(self.by), offer=make_offer(self.by, status="open"))
        self.assertEqual(self.get(self.dev_user).data["candidate"]["counts"]["total"], 0)


class RecruiterDashboardTests(DashboardBase):
    def setUp(self):
        super().setUp()
        self.open_offer = make_offer(self.by, company=self.company, recruiter=self.recruiter, status="open", title="Front React", views_count=40)
        self.draft = make_offer(self.by, company=self.company, recruiter=self.recruiter, status="draft", views_count=0)
        self.closed = make_offer(self.by, company=self.company, recruiter=self.recruiter, status="closed", views_count=15)
        self.foreign = make_offer(self.by, status="open", views_count=999)
        skill = make_skill(self.by)
        self.open_offer.required_skills.add(skill)
        make_profil_skill(self.by, profil=self.dev, skill=skill, level=4)
        make_candidature(self.by, offer=self.open_offer, profil=self.dev, status="sent")
        make_candidature(self.by, offer=self.open_offer, profil=make_profil(self.by), status="shortlisted")
        make_candidature(self.by, offer=self.closed, profil=make_profil(self.by), status="accepted")
        make_candidature(self.by, offer=self.foreign, profil=make_profil(self.by), status="sent")

    def block(self):
        return self.get(self.recruiter_user).data["recruiter"]

    def test_offer_and_candidature_figures_cover_only_my_company(self):
        data = self.block()
        self.assertEqual(data["company"]["name"], "Faso Pay")
        self.assertEqual(data["offers"], {"open": 1, "draft": 1, "closed": 1, "total": 3})
        self.assertEqual(data["views_total"], 55)
        self.assertEqual(data["candidatures"], {"sent": 1, "shortlisted": 1, "accepted": 1, "rejected": 0, "total": 3})

    def test_top_offers_and_recent_candidatures(self):
        data = self.block()
        self.assertEqual(data["top_offers"][0]["title"], "Front React")
        self.assertEqual((data["top_offers"][0]["candidatures_count"], data["top_offers"][0]["candidatures_new"]), (2, 1))
        recent = data["recent_candidatures"]
        self.assertEqual(len(recent), 3)
        self.assertIn("score", recent[0])
        self.assertIn("name", recent[0]["profil"])
        self.assertNotIn("email", recent[0]["profil"])

    def test_pool_size_counts_distinct_liked_talents_of_the_company(self):
        colleague = make_profil(self.by, company=self.company)
        talent = make_profil(self.by)
        make_swipe(self.by, author=self.recruiter, target=talent, direction="like", context="recruit")
        make_swipe(self.by, author=colleague, target=talent, direction="like", context="recruit")
        make_swipe(self.by, author=self.recruiter, target=make_profil(self.by), direction="pass", context="recruit")
        make_swipe(self.by, author=make_profil(self.by), target=talent, direction="like", context="recruit")
        self.assertEqual(self.block()["pool_size"], 1)

    def test_weekly_series_covers_eight_weeks_oldest_first(self):
        old = Candidature.objects.filter(offer=self.closed).first()
        Candidature.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(weeks=3))
        Candidature.objects.filter(offer=self.foreign).update(created_at=timezone.now() - timedelta(weeks=1))
        weekly = self.block()["weekly"]
        self.assertEqual(len(weekly), 8)
        self.assertEqual([row["week_start"] for row in weekly], sorted(row["week_start"] for row in weekly))
        # 3 candidatures reçues par mon entreprise ; celle d'une autre entreprise n'est pas comptée
        self.assertEqual(sum(row["count"] for row in weekly), 3)
        self.assertEqual(weekly[-1]["count"], 2)
        self.assertEqual(weekly[-4]["count"], 1)

    def test_recruiter_also_gets_the_candidate_block(self):
        data = self.get(self.recruiter_user).data
        self.assertEqual(data["candidate"]["counts"]["total"], 0)
        self.assertIn("completeness", data)


class CompletenessUnitTests(TestCase):
    def test_empty_profile_misses_everything(self):
        profil = make_profil(make_user(), headline="", city="", bio="")
        data = DashboardService._completeness(profil)
        self.assertEqual(data["percent"], 0)
        self.assertEqual(len(data["missing"]), 8)
