"""Écrans utilisateur « marché » : score par règles, offres, candidatures, décisions, compétences."""
from datetime import date
from decimal import Decimal

from django.core import mail
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from app.marketplace.factories import (
    make_availability,
    make_candidature,
    make_company,
    make_offer,
    make_profil,
    make_profil_skill,
    make_review,
    make_skill,
    make_user,
)
from app.marketplace.models import Availability, Candidature, Offer, ProfilSkill
from app.marketplace.services.scoring import WEIGHTS, add_months, build_contexts, compute_score


def login(client, user):
    client.credentials(HTTP_AUTHORIZATION="Bearer " + str(RefreshToken.for_user(user).access_token))


class ScoringTests(TestCase):
    def setUp(self):
        self.by = make_user()
        self.skill = make_skill(self.by)
        self.company = make_company(self.by)
        self.recruiter = make_profil(self.by, company=self.company)
        self.offer = make_offer(
            self.by,
            company=self.company,
            recruiter=self.recruiter,
            experience_level="mid",
            city="Ouagadougou",
            work_mode="on_site",
            budget_max=Decimal("440000"),
            budget_period="month",
            start_date=date(2026, 12, 1),
            contract_duration=3,
        )
        self.offer.required_skills.add(self.skill)

    def score(self, profil):
        ctx = build_contexts([profil])[profil.id]
        return compute_score(self.offer, profil, ctx)

    def test_weights_sum_to_100(self):
        self.assertEqual(sum(WEIGHTS.values()), 100)

    def test_ideal_profil_scores_high(self):
        profil = make_profil(
            self.by, years_of_experience=4, city="Ouagadougou", daily_rate=Decimal("15000"), is_open_to_work=True
        )
        make_profil_skill(self.by, profil=profil, skill=self.skill, level=5)
        make_availability(self.by, profil=profil, start_date=date(2026, 11, 1), end_date=date(2027, 3, 1))
        make_review(self.by, target=profil, rating=5)
        result = self.score(profil)
        self.assertGreaterEqual(result["score"], 95)
        self.assertEqual(result["matched_skill_ids"], [self.skill.id])
        self.assertEqual([item["key"] for item in result["breakdown"]][:2], ["skills", "experience"])

    def test_missing_required_skill_scores_zero_on_skills(self):
        result = self.score(make_profil(self.by))
        skills = next(item for item in result["breakdown"] if item["key"] == "skills")
        self.assertEqual(skills["score"], 0)

    def test_busy_period_scores_zero_on_availability(self):
        profil = make_profil(self.by)
        make_availability(self.by, profil=profil, start_date=date(2026, 12, 10), end_date=date(2026, 12, 20), status="busy")
        availability = next(item for item in self.score(profil)["breakdown"] if item["key"] == "availability")
        self.assertEqual(availability["score"], 0)

    def test_junior_scores_lower_on_experience_for_mid_offer(self):
        profil = make_profil(self.by, years_of_experience=1)
        experience = next(item for item in self.score(profil)["breakdown"] if item["key"] == "experience")
        self.assertLess(experience["score"], WEIGHTS["experience"])

    def test_other_country_on_site_scores_zero_on_location(self):
        profil = make_profil(self.by, country="FR", city="Paris")
        location = next(item for item in self.score(profil)["breakdown"] if item["key"] == "location")
        self.assertEqual(location["score"], 0)

    def test_add_months_clamps_to_end_of_month(self):
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(add_months(date(2026, 11, 15), 3), date(2027, 2, 15))


class MarketBase(APITestCase):
    def setUp(self):
        self.by = make_user()
        self.recruiter_user = make_user(first_name="Fatou", last_name="Sow")
        self.company = make_company(self.by, name="Resto Express")
        self.recruiter = make_profil(self.by, user=self.recruiter_user, company=self.company, is_company_owner=True)
        self.candidate_user = make_user(first_name="Awa", last_name="Kone", email="awa@example.com")
        self.candidate = make_profil(self.by, user=self.candidate_user, years_of_experience=4)
        self.react = make_skill(self.by, name="React Native X", slug="react-native-x")
        self.offer = make_offer(
            self.by, company=self.company, recruiter=self.recruiter, status="open", title="Dev mobile",
            start_date=date(2026, 12, 1), contract_duration=3,
        )
        self.offer.required_skills.add(self.react)
        make_profil_skill(self.by, profil=self.candidate, skill=self.react, level=4)

    def as_user(self, user):
        login(self.client, user)


class OffersApiTests(MarketBase):
    def test_list_open_offers_scored_for_candidate(self):
        make_offer(self.by, status="draft", title="Brouillon")
        low = make_offer(self.by, status="open", title="Autre", country="FR")
        low.required_skills.add(make_skill(self.by))
        self.as_user(self.candidate_user)
        response = self.client.get("/api/v1/marketplace/offers")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [row["title"] for row in response.data]
        self.assertNotIn("Brouillon", titles)
        self.assertEqual(titles[0], "Dev mobile")
        self.assertGreater(response.data[0]["score"], response.data[-1]["score"])
        self.assertEqual(len(response.data[0]["breakdown"]), 6)

    def test_recruiter_does_not_see_own_company_offers(self):
        self.as_user(self.recruiter_user)
        self.assertNotIn("Dev mobile", [row["title"] for row in self.client.get("/api/v1/marketplace/offers").data])

    def test_list_without_profil_has_no_score(self):
        self.as_user(make_user())
        response = self.client.get("/api/v1/marketplace/offers")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("score", response.data[0])

    def test_search_and_filters(self):
        self.as_user(self.candidate_user)
        self.assertEqual(len(self.client.get("/api/v1/marketplace/offers?search=mobile").data), 1)
        self.assertEqual(len(self.client.get("/api/v1/marketplace/offers?search=introuvable").data), 0)
        self.assertEqual(len(self.client.get("/api/v1/marketplace/offers?type=cdi").data), 0)

    def test_detail_counts_views_and_hides_drafts(self):
        draft = make_offer(self.by, status="draft")
        self.as_user(self.candidate_user)
        response = self.client.get(f"/api/v1/marketplace/offers/{self.offer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["views_count"], 1)
        self.assertIn("description", response.data)
        self.assertEqual(self.client.get(f"/api/v1/marketplace/offers/{draft.id}").status_code, 404)

    def test_company_sees_its_own_draft(self):
        draft = make_offer(self.by, company=self.company, recruiter=self.recruiter, status="draft")
        self.as_user(self.recruiter_user)
        self.assertEqual(self.client.get(f"/api/v1/marketplace/offers/{draft.id}").status_code, 200)

    def test_anonymous_is_refused(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/v1/marketplace/offers").status_code, 401)


class ApplyTests(MarketBase):
    def apply(self, user, offer=None, message="Bonjour"):
        self.as_user(user)
        return self.client.post(f"/api/v1/marketplace/offers/{(offer or self.offer).id}/apply", {"message": message}, format="json")

    def test_apply_creates_candidature(self):
        response = self.apply(self.candidate_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        candidature = Candidature.objects.get(offer=self.offer, profil=self.candidate)
        self.assertEqual((candidature.status, candidature.message), ("sent", "Bonjour"))

    def test_apply_twice_is_refused(self):
        self.apply(self.candidate_user)
        self.assertEqual(self.apply(self.candidate_user).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Candidature.objects.count(), 1)

    def test_apply_to_own_company_is_refused(self):
        self.assertEqual(self.apply(self.recruiter_user).status_code, status.HTTP_400_BAD_REQUEST)

    def test_apply_to_closed_offer_is_404(self):
        closed = make_offer(self.by, status="closed")
        self.assertEqual(self.apply(self.candidate_user, closed).status_code, status.HTTP_404_NOT_FOUND)

    def test_apply_without_profil_is_403(self):
        self.assertEqual(self.apply(make_user()).status_code, status.HTTP_403_FORBIDDEN)

    def test_my_candidatures(self):
        self.apply(self.candidate_user)
        response = self.client.get("/api/v1/marketplace/me/candidatures")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["offer"]["title"], "Dev mobile")
        self.client.credentials()
        self.as_user(self.recruiter_user)
        self.assertEqual(self.client.get("/api/v1/marketplace/me/candidatures").data, [])


class RecruiterOffersTests(MarketBase):
    PAYLOAD = {
        "title": "Développeur Flutter",
        "description": "Application de livraison",
        "type": "mission",
        "experience_level": "mid",
        "country": "tg",
        "city": "Lomé",
        "work_mode": "hybrid",
        "contract_duration": 3,
        "budget_max": "500000",
        "start_date": "2026-12-01",
    }

    def test_recruiter_creates_and_publishes_offer(self):
        self.as_user(self.recruiter_user)
        body = {**self.PAYLOAD, "required_skill_ids": [self.react.id], "publish": True}
        response = self.client.post("/api/v1/marketplace/me/offers", body, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        offer = Offer.objects.get(id=response.data["id"])
        self.assertEqual((offer.status, offer.country, offer.company_id), ("open", "TG", self.company.id))
        self.assertIsNotNone(offer.published_at)
        self.assertEqual(list(offer.required_skills.all()), [self.react])
        self.assertEqual(offer.recruiter_id, self.recruiter.id)

    def test_offer_is_draft_by_default(self):
        self.as_user(self.recruiter_user)
        response = self.client.post("/api/v1/marketplace/me/offers", self.PAYLOAD, format="json")
        self.assertEqual(response.data["status"], "draft")

    def test_non_recruiter_is_refused(self):
        self.as_user(self.candidate_user)
        self.assertEqual(self.client.post("/api/v1/marketplace/me/offers", self.PAYLOAD, format="json").status_code, 403)
        self.assertEqual(self.client.get("/api/v1/marketplace/me/offers").status_code, 403)

    def test_invalid_payload_is_refused(self):
        self.as_user(self.recruiter_user)
        bad = {**self.PAYLOAD, "budget_min": "900", "budget_max": "100", "required_skill_ids": [999999]}
        response = self.client.post("/api/v1/marketplace/me/offers", bad, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("budget_max", response.data)

    def test_status_and_company_cannot_be_forged(self):
        self.as_user(self.recruiter_user)
        other = make_company(self.by)
        body = {**self.PAYLOAD, "status": "closed", "company_id": other.id, "company": other.id}
        offer = Offer.objects.get(id=self.client.post("/api/v1/marketplace/me/offers", body, format="json").data["id"])
        self.assertEqual((offer.status, offer.company_id), ("draft", self.company.id))

    def test_update_and_close_own_offer(self):
        self.as_user(self.recruiter_user)
        response = self.client.patch(
            f"/api/v1/marketplace/me/offers/{self.offer.id}", {"title": "Nouveau titre", "status": "closed"}, format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.offer.refresh_from_db()
        self.assertEqual((self.offer.title, self.offer.status), ("Nouveau titre", "closed"))

    def test_cannot_touch_another_company_offer(self):
        foreign = make_offer(self.by, status="open")
        self.as_user(self.recruiter_user)
        self.assertEqual(self.client.patch(f"/api/v1/marketplace/me/offers/{foreign.id}", {"title": "x"}, format="json").status_code, 404)
        self.assertEqual(self.client.get(f"/api/v1/marketplace/me/offers/{foreign.id}/candidatures").status_code, 404)

    def test_my_offers_lists_counts(self):
        make_candidature(self.by, offer=self.offer, profil=self.candidate)
        self.as_user(self.recruiter_user)
        rows = self.client.get("/api/v1/marketplace/me/offers").data
        self.assertEqual((rows[0]["candidatures_count"], rows[0]["candidatures_new"]), (1, 1))

    def test_candidatures_are_ranked_with_contact(self):
        weak = make_profil(self.by, user=make_user(first_name="Salif", last_name="B"), years_of_experience=0)
        make_candidature(self.by, offer=self.offer, profil=weak)
        make_candidature(self.by, offer=self.offer, profil=self.candidate)
        self.as_user(self.recruiter_user)
        rows = self.client.get(f"/api/v1/marketplace/me/offers/{self.offer.id}/candidatures").data
        self.assertEqual(rows[0]["profil"]["name"], "Awa Kone")
        self.assertEqual(rows[0]["profil"]["email"], "awa@example.com")
        self.assertGreater(rows[0]["score"], rows[1]["score"])

    def test_recommended_profils(self):
        hidden = make_profil(self.by, is_open_to_work=False)
        make_profil_skill(self.by, profil=hidden, skill=self.react, level=5)
        self.as_user(self.recruiter_user)
        rows = self.client.get(f"/api/v1/marketplace/me/offers/{self.offer.id}/recommended-profils").data
        ids = [row["id"] for row in rows]
        self.assertEqual(ids[0], self.candidate.id)
        self.assertNotIn(hidden.id, ids)
        self.assertNotIn(self.recruiter.id, ids)
        self.assertNotIn("email", rows[0])


class DecisionTests(MarketBase):
    def setUp(self):
        super().setUp()
        self.candidature = make_candidature(self.by, offer=self.offer, profil=self.candidate)

    def decide(self, user, status_value, candidature=None):
        self.as_user(user)
        return self.client.post(
            f"/api/v1/marketplace/candidatures/{(candidature or self.candidature).id}/decision", {"status": status_value}, format="json"
        )

    def test_accept_books_mission_and_sends_email(self):
        response = self.decide(self.recruiter_user, "accepted")
        self.assertEqual(response.status_code, 200, response.data)
        self.candidature.refresh_from_db()
        self.assertEqual(self.candidature.status, "accepted")
        self.assertIsNotNone(self.candidature.decided_at)
        busy = Availability.objects.get(profil=self.candidate, source="mission")
        self.assertEqual((busy.status, busy.start_date, busy.end_date), ("busy", date(2026, 12, 1), date(2027, 2, 28)))
        self.assertIn("Dev mobile", busy.note)
        self.assertEqual(mail.outbox[-1].to, ["awa@example.com"])

    def test_shortlist_and_reject_do_not_touch_calendar(self):
        self.assertEqual(self.decide(self.recruiter_user, "shortlisted").status_code, 200)
        self.assertEqual(self.decide(self.recruiter_user, "rejected").status_code, 200)
        self.assertFalse(Availability.objects.filter(source="mission").exists())

    def test_accepted_is_final(self):
        self.decide(self.recruiter_user, "accepted")
        self.assertEqual(self.decide(self.recruiter_user, "rejected").status_code, 400)

    def test_other_company_cannot_decide(self):
        other_user = make_user()
        make_profil(self.by, user=other_user, company=make_company(self.by), is_company_owner=True)
        self.assertEqual(self.decide(other_user, "accepted").status_code, 404)
        self.candidature.refresh_from_db()
        self.assertEqual(self.candidature.status, "sent")

    def test_candidate_cannot_decide_own_application(self):
        self.assertEqual(self.decide(self.candidate_user, "accepted").status_code, 403)

    def test_invalid_status_is_refused(self):
        self.assertEqual(self.decide(self.recruiter_user, "sent").status_code, 400)

    def test_offer_without_start_date_books_from_today(self):
        offer = make_offer(self.by, company=self.company, recruiter=self.recruiter, status="open", start_date=None)
        candidature = make_candidature(self.by, offer=offer, profil=self.candidate)
        self.assertEqual(self.decide(self.recruiter_user, "accepted", candidature).status_code, 200)
        self.assertTrue(Availability.objects.filter(profil=self.candidate, source="mission").exists())


class SkillsApiTests(MarketBase):
    def test_base_skills_are_seeded_by_migration(self):
        self.as_user(self.candidate_user)
        names = [row["name"] for row in self.client.get("/api/v1/marketplace/skills").data]
        self.assertIn("Python", names)
        self.assertEqual([row["name"] for row in self.client.get("/api/v1/marketplace/skills?search=django").data], ["Django"])

    def test_replace_my_skills(self):
        other = make_skill(self.by)
        self.as_user(self.candidate_user)
        body = {"skills": [{"skill_id": other.id, "level": 3, "years": 2}]}
        response = self.client.put("/api/v1/marketplace/me/skills", body, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual([(row["skill_id"], row["level"]) for row in response.data], [(other.id, 3)])
        self.assertEqual(ProfilSkill.objects.filter(profil=self.candidate).count(), 1)

    def test_unknown_skill_and_bad_level_are_refused(self):
        self.as_user(self.candidate_user)
        self.assertEqual(self.client.put("/api/v1/marketplace/me/skills", {"skills": [{"skill_id": 999999, "level": 3}]}, format="json").status_code, 400)
        self.assertEqual(self.client.put("/api/v1/marketplace/me/skills", {"skills": [{"skill_id": self.react.id, "level": 9}]}, format="json").status_code, 400)

    def test_skills_require_profil(self):
        self.as_user(make_user())
        self.assertEqual(self.client.get("/api/v1/marketplace/me/skills").status_code, 403)
