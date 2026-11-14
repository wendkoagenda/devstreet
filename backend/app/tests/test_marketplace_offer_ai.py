"""UC-09 : génération d'offre marketplace par IA (brouillon + suggestions)."""
import json
from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from app.ai.errors import ExternalUnavailable
from app.ai.providers.base import CompletionResult
from app.marketplace.factories import (
    make_company,
    make_profil,
    make_profil_skill,
    make_skill,
    make_user,
)
from app.marketplace.services.offer_ai_service import _normalize_draft


def login(client, user):
    client.credentials(HTTP_AUTHORIZATION="Bearer " + str(RefreshToken.for_user(user).access_token))


class OfferAiGenerateApiTests(APITestCase):
    URL = "/api/v1/marketplace/me/offers/generate"

    def setUp(self):
        cache.clear()
        self.by = make_user()
        self.company = make_company(self.by, country="SN", city="Dakar")
        self.recruiter = make_profil(self.by, user=self.by, company=self.company, is_company_owner=True)
        self.react = make_skill(self.by)
        self.ts = make_skill(self.by)
        self.sample_draft = {
            "title": "Développeur React Native",
            "description": "Nous recherchons un développeur mobile pour une app de livraison.",
            "type": "mission",
            "experience_level": "mid",
            "work_mode": "hybrid",
            "contract_duration": 3,
            "budget_min": 400000,
            "budget_max": 600000,
            "currency": "XOF",
            "budget_period": "month",
            "skills": [self.react.name, self.ts.name],
        }
        login(self.client, self.by)

    @patch("app.marketplace.services.offer_ai_service.LlmRouter.complete")
    def test_generate_returns_draft_and_suggestions(self, complete):
        complete.return_value = CompletionResult(
            content=json.dumps(self.sample_draft),
            provider="grok",
            model="test-model",
        )
        talent = make_profil(self.by, is_open_to_work=True, years_of_experience=4)
        make_profil_skill(self.by, profil=talent, skill=self.react, level=4)

        response = self.client.post(
            self.URL,
            {"brief": "Besoin d'une app mobile de livraison pour restaurant."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        draft = response.data["draft"]
        self.assertEqual(draft["title"], self.sample_draft["title"])
        self.assertEqual(draft["country"], "SN")
        self.assertEqual(draft["city"], "Dakar")
        self.assertIn(self.react.id, draft["required_skill_ids"])
        self.assertIn(self.ts.id, draft["required_skill_ids"])
        self.assertEqual(response.data["provider"], "grok")
        self.assertIsInstance(response.data["suggested_profils"], list)

    def test_brief_too_short_returns_400(self):
        response = self.client.post(self.URL, {"brief": "trop court"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_recruiter_forbidden(self):
        talent = make_user()
        make_profil(self.by, user=talent)
        login(self.client, talent)
        response = self.client.post(
            self.URL,
            {"brief": "Besoin d'un développeur Django expérimenté."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("app.marketplace.services.offer_ai_service.LlmRouter.complete")
    def test_external_unavailable_returns_503(self, complete):
        complete.side_effect = ExternalUnavailable("down")
        response = self.client.post(
            self.URL,
            {"brief": "Besoin d'un développeur Django expérimenté."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
    @patch("app.marketplace.services.offer_ai_service.LlmRouter.complete")
    def test_daily_quota(self, complete):
        complete.return_value = CompletionResult(
            content=json.dumps(self.sample_draft),
            provider="grok",
            model="m",
        )
        with patch("app.marketplace.services.offer_ai_service.DAILY_QUOTA", 1):
            first = self.client.post(
                self.URL,
                {"brief": "Besoin d'un développeur Django expérimenté."},
                format="json",
            )
            self.assertEqual(first.status_code, status.HTTP_200_OK)
            second = self.client.post(
                self.URL,
                {"brief": "Autre besoin pour une API Django."},
                format="json",
            )
            self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class OfferAiNormalizeTests(APITestCase):
    def setUp(self):
        self.by = make_user()
        self.skill = make_skill(self.by)

    def test_normalize_matches_skills_and_clamps_fields(self):
        draft = _normalize_draft(
            {
                "title": "Backend Django",
                "description": "Mission API.",
                "type": "weird",
                "experience_level": "nope",
                "work_mode": "??",
                "contract_duration": 99,
                "budget_period": "year",
                "skills": [self.skill.name, "InconnuXYZ"],
            },
            country="BF",
            city="Ouagadougou",
        )
        self.assertEqual(draft["type"], "mission")
        self.assertEqual(draft["experience_level"], "mid")
        self.assertEqual(draft["work_mode"], "hybrid")
        self.assertEqual(draft["contract_duration"], 36)
        self.assertEqual(draft["budget_period"], "month")
        self.assertEqual(draft["required_skill_ids"], [self.skill.id])
        self.assertEqual(draft["country"], "BF")
