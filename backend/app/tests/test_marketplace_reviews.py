"""UC-12 : dépôt d'avis après une candidature acceptée."""
from rest_framework.test import APITestCase

from app.marketplace.factories import (
    make_candidature,
    make_company,
    make_offer,
    make_profil,
    make_user,
)
from app.marketplace.models import Review
from app.tests.test_marketplace_market import login


class ReviewMeApiTests(APITestCase):
    URL = "/api/v1/marketplace/me/reviews"
    PENDING = "/api/v1/marketplace/me/reviews/pending"

    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by)
        self.recruiter_user = make_user(first_name="Fatou", last_name="R")
        self.recruiter = make_profil(
            self.by, user=self.recruiter_user, company=self.company, is_company_owner=True
        )
        self.dev_user = make_user(first_name="Awa", last_name="D")
        self.dev = make_profil(self.by, user=self.dev_user)
        self.offer = make_offer(
            self.by, company=self.company, recruiter=self.recruiter, status="closed"
        )
        self.candidature = make_candidature(
            self.by, offer=self.offer, profil=self.dev, status="accepted"
        )

    def test_pending_for_candidate_and_recruiter(self):
        login(self.client, self.dev_user)
        pending = self.client.get(self.PENDING)
        self.assertEqual(pending.status_code, 200)
        self.assertEqual(len(pending.data), 1)
        self.assertEqual(pending.data[0]["target"]["id"], self.recruiter.id)

        login(self.client, self.recruiter_user)
        pending = self.client.get(self.PENDING)
        self.assertEqual(len(pending.data), 1)
        self.assertEqual(pending.data[0]["target"]["id"], self.dev.id)

    def test_candidate_can_review_recruiter(self):
        login(self.client, self.dev_user)
        response = self.client.post(
            self.URL,
            {
                "candidature_id": self.candidature.id,
                "rating": 5,
                "comment": "Très bonne collaboration",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["target"]["id"], self.recruiter.id)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(len(self.client.get(self.PENDING).data), 0)

    def test_cannot_review_twice(self):
        login(self.client, self.dev_user)
        body = {"candidature_id": self.candidature.id, "rating": 4}
        self.assertEqual(self.client.post(self.URL, body, format="json").status_code, 201)
        self.assertEqual(self.client.post(self.URL, body, format="json").status_code, 400)

    def test_cannot_review_foreign_candidature(self):
        stranger = make_user()
        make_profil(self.by, user=stranger)
        login(self.client, stranger)
        response = self.client.post(
            self.URL,
            {"candidature_id": self.candidature.id, "rating": 3},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_sent_candidature_not_reviewable(self):
        other = make_candidature(self.by, offer=self.offer, profil=make_profil(self.by), status="sent")
        login(self.client, self.recruiter_user)
        response = self.client.post(
            self.URL,
            {"candidature_id": other.id, "rating": 5},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
