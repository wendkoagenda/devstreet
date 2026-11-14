"""UC-02 : réputation calculée depuis les contributions DevStreet."""
from rest_framework.test import APITestCase

from app.marketplace.factories import make_profil, make_review, make_user
from app.marketplace.services.reputation_service import ReputationService
from app.tests.test_marketplace_market import login


class ReputationServiceTests(APITestCase):
    def setUp(self):
        self.user = make_user(first_name="Awa", last_name="K")
        self.by = make_user()
        self.profil = make_profil(self.by, user=self.user)

    def test_empty_reputation_is_zero(self):
        data = ReputationService.for_profil(self.profil)
        self.assertEqual(data["score"], 0)
        self.assertIsNone(data["rating_avg"])
        self.assertEqual(data["reviews_count"], 0)
        self.assertEqual(data["breakdown"]["reviews"]["points"], 0)

    def test_reviews_increase_score(self):
        make_review(self.by, target=self.profil, rating=5)
        make_review(make_user(), target=self.profil, rating=4)
        data = ReputationService.for_profil(self.profil)
        self.assertEqual(data["reviews_count"], 2)
        self.assertEqual(data["rating_avg"], 4.5)
        self.assertGreater(data["score"], 0)
        self.assertGreater(data["breakdown"]["reviews"]["points"], 0)

    def test_api_endpoint(self):
        make_review(self.by, target=self.profil, rating=5)
        login(self.client, self.user)
        response = self.client.get("/api/v1/marketplace/me/reputation")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn("score", response.data)
        self.assertIn("breakdown", response.data)
        self.assertEqual(response.data["reviews_count"], 1)

    def test_dashboard_embeds_reputation_breakdown(self):
        make_review(self.by, target=self.profil, rating=5)
        login(self.client, self.user)
        response = self.client.get("/api/v1/marketplace/me/dashboard")
        self.assertEqual(response.status_code, 200, response.data)
        reputation = response.data["reputation"]
        self.assertIn("score", reputation)
        self.assertIn("breakdown", reputation)
        self.assertIn("forum", reputation["breakdown"])

    def test_requires_profil(self):
        login(self.client, make_user())
        self.assertEqual(self.client.get("/api/v1/marketplace/me/reputation").status_code, 403)
