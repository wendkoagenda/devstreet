"""Découverte de profils : paquet de cartes, swipes, vivier, connexions, fiche publique."""
from datetime import date, timedelta

from rest_framework.test import APITestCase

from app.marketplace.factories import (
    make_availability,
    make_candidature,
    make_company,
    make_experience,
    make_offer,
    make_profil,
    make_profil_skill,
    make_review,
    make_skill,
    make_user,
)
from app.marketplace.models import Connection, Swipe
from app.tests.test_marketplace_market import login


class NetworkBase(APITestCase):
    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by)
        self.recruiter_user = make_user(first_name="Fatou", last_name="Sow")
        self.recruiter = make_profil(self.by, user=self.recruiter_user, company=self.company, is_company_owner=True)
        self.python = make_skill(self.by, name="Python X", slug="python-x")
        self.devs = []
        for index, (first, years) in enumerate((("Yao", 4), ("Mariam", 5), ("Kossi", 6))):
            user = make_user(first_name=first, last_name="D", email=f"{first.lower()}@example.com")
            profil = make_profil(self.by, user=user, years_of_experience=years, headline=f"Dev {first}")
            if index < 2:
                make_profil_skill(self.by, profil=profil, skill=self.python, level=4)
            self.devs.append(profil)
        self.yao, self.mariam, self.kossi = self.devs
        self.offer = make_offer(self.by, company=self.company, recruiter=self.recruiter, status="open")
        self.offer.required_skills.add(self.python)

    def as_user(self, user):
        login(self.client, user)

    def swipe(self, target, direction="like", context="recruit"):
        return self.client.post(
            "/api/v1/marketplace/me/swipes", {"target_id": target.id, "direction": direction, "context": context}, format="json"
        )


class DeckTests(NetworkBase):
    def test_recruit_deck_ranks_by_best_offer_score(self):
        self.as_user(self.recruiter_user)
        response = self.client.get("/api/v1/marketplace/me/deck?context=recruit")
        self.assertEqual(response.status_code, 200, response.data)
        ids = [card["id"] for card in response.data]
        self.assertNotIn(self.recruiter.id, ids)
        self.assertEqual(ids[-1], self.kossi.id)  # sans la compétence requise
        self.assertIsNotNone(response.data[0]["score"])
        self.assertNotIn("email", response.data[0])

    def test_recruit_deck_hides_swiped_and_closed_to_work(self):
        self.mariam.is_open_to_work = False
        self.mariam.save()
        self.as_user(self.recruiter_user)
        self.swipe(self.yao)
        ids = [card["id"] for card in self.client.get("/api/v1/marketplace/me/deck?context=recruit").data]
        self.assertEqual(ids, [self.kossi.id])

    def test_recruit_deck_requires_recruiter(self):
        self.as_user(self.yao.user)
        self.assertEqual(self.client.get("/api/v1/marketplace/me/deck?context=recruit").status_code, 403)

    def test_network_deck_ranks_common_skills(self):
        self.as_user(self.mariam.user)
        cards = self.client.get("/api/v1/marketplace/me/deck?context=network").data
        self.assertEqual(cards[0]["id"], self.yao.id)
        self.assertEqual(cards[0]["common_skills"], ["Python X"])
        self.assertNotIn(self.mariam.id, [card["id"] for card in cards])

    def test_invalid_context_and_no_profil(self):
        self.as_user(self.yao.user)
        self.assertEqual(self.client.get("/api/v1/marketplace/me/deck?context=x").status_code, 400)
        self.as_user(make_user())
        self.assertEqual(self.client.get("/api/v1/marketplace/me/deck?context=network").status_code, 403)

    def test_available_from_is_exposed(self):
        start = date.today() + timedelta(days=10)
        make_availability(self.by, profil=self.yao, start_date=start, end_date=start + timedelta(days=30), status="available")
        self.as_user(self.recruiter_user)
        cards = {card["id"]: card for card in self.client.get("/api/v1/marketplace/me/deck?context=recruit").data}
        self.assertEqual(cards[self.yao.id]["available_from"], start.isoformat())


class SwipeTests(NetworkBase):
    def test_like_and_pass_are_recorded(self):
        self.as_user(self.recruiter_user)
        self.assertEqual(self.swipe(self.yao).status_code, 201)
        self.assertEqual(self.swipe(self.mariam, "pass").status_code, 201)
        self.assertEqual(Swipe.objects.filter(author=self.recruiter).count(), 2)

    def test_cannot_swipe_twice_or_self(self):
        self.as_user(self.recruiter_user)
        self.swipe(self.yao)
        self.assertEqual(self.swipe(self.yao).status_code, 400)
        self.assertEqual(self.swipe(self.recruiter).status_code, 404)

    def test_mutual_network_like_creates_connection(self):
        self.as_user(self.yao.user)
        first = self.swipe(self.mariam, context="network")
        self.assertFalse(first.data["matched"])
        self.as_user(self.mariam.user)
        second = self.swipe(self.yao, context="network")
        self.assertTrue(second.data["matched"])
        connection = Connection.objects.get()
        self.assertEqual((connection.profil_a_id, connection.profil_b_id), tuple(sorted((self.yao.id, self.mariam.id))))
        self.assertEqual(connection.status, "matched")

    def test_pass_never_matches(self):
        self.as_user(self.yao.user)
        self.swipe(self.mariam, context="network")
        self.as_user(self.mariam.user)
        self.assertFalse(self.swipe(self.yao, "pass", "network").data["matched"])
        self.assertFalse(Connection.objects.exists())

    def test_recruit_like_does_not_create_connection(self):
        self.as_user(self.yao.user)
        self.swipe(self.mariam, context="network")
        self.as_user(self.recruiter_user)
        self.swipe(self.yao, context="recruit")
        self.assertFalse(Connection.objects.exists())

    def test_undo_last_swipe_removes_connection(self):
        self.as_user(self.yao.user)
        self.swipe(self.mariam, context="network")
        self.as_user(self.mariam.user)
        self.swipe(self.yao, context="network")
        response = self.client.delete("/api/v1/marketplace/me/swipes/last?context=network")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["undone"], self.yao.id)
        self.assertFalse(Connection.objects.exists())
        self.assertFalse(Swipe.objects.filter(author=self.mariam).exists())
        self.assertEqual(self.client.delete("/api/v1/marketplace/me/swipes/last?context=network").status_code, 404)


class PoolAndConnectionsTests(NetworkBase):
    def test_pool_lists_company_likes_without_duplicates(self):
        colleague_user = make_user(first_name="Awa")
        colleague = make_profil(self.by, user=colleague_user, company=self.company)
        self.as_user(self.recruiter_user)
        self.swipe(self.yao)
        self.swipe(self.kossi, "pass")
        self.as_user(colleague_user)
        self.swipe(self.yao)
        self.swipe(self.mariam)
        self.as_user(self.recruiter_user)
        rows = self.client.get("/api/v1/marketplace/me/pool").data
        self.assertEqual(sorted(row["id"] for row in rows), sorted([self.yao.id, self.mariam.id]))
        self.assertEqual(rows[0]["email"], self.mariam.user.email)
        self.assertEqual(colleague.company_id, self.company.id)

    def test_pool_is_private_to_the_company(self):
        self.as_user(self.recruiter_user)
        self.swipe(self.yao)
        other_user = make_user()
        make_profil(self.by, user=other_user, company=make_company(self.by))
        self.as_user(other_user)
        self.assertEqual(self.client.get("/api/v1/marketplace/me/pool").data, [])

    def test_connections_list_with_contact(self):
        self.as_user(self.yao.user)
        self.swipe(self.mariam, context="network")
        self.as_user(self.mariam.user)
        self.swipe(self.yao, context="network")
        rows = self.client.get("/api/v1/marketplace/me/connections").data
        self.assertEqual([row["id"] for row in rows], [self.yao.id])
        self.assertEqual(rows[0]["email"], self.yao.user.email)
        self.as_user(self.kossi.user)
        self.assertEqual(self.client.get("/api/v1/marketplace/me/connections").data, [])


class PublicProfileTests(NetworkBase):
    def test_profile_with_experiences_skills_and_reviews(self):
        make_experience(self.by, profil=self.yao, title="Développeur mobile")
        make_review(self.by, target=self.yao, rating=5, comment="Excellent", is_public=True)
        make_review(self.by, target=self.yao, rating=1, comment="Privé", is_public=False)
        self.as_user(self.recruiter_user)
        data = self.client.get(f"/api/v1/marketplace/profils/{self.yao.id}").data
        self.assertEqual(data["experiences"][0]["title"], "Développeur mobile")
        self.assertEqual(data["skills_detail"][0]["name"], "Python X")
        self.assertEqual([review["comment"] for review in data["reviews"]], ["Excellent"])
        self.assertEqual(data["rating_avg"], 5.0)
        self.assertFalse(data["is_self"])
        self.assertNotIn("email", data)

    def test_email_visible_for_candidate_of_my_company(self):
        make_candidature(self.by, offer=self.offer, profil=self.yao)
        self.as_user(self.recruiter_user)
        self.assertEqual(self.client.get(f"/api/v1/marketplace/profils/{self.yao.id}").data["email"], self.yao.user.email)

    def test_closed_profile_is_hidden_unless_related(self):
        self.kossi.is_open_to_work = False
        self.kossi.save()
        self.as_user(self.recruiter_user)
        self.assertEqual(self.client.get(f"/api/v1/marketplace/profils/{self.kossi.id}").status_code, 404)
        self.as_user(self.kossi.user)
        self.assertTrue(self.client.get(f"/api/v1/marketplace/profils/{self.kossi.id}").data["is_self"])

    def test_requires_profil(self):
        self.as_user(make_user())
        self.assertEqual(self.client.get(f"/api/v1/marketplace/profils/{self.yao.id}").status_code, 403)


class TalentsDirectoryTests(NetworkBase):
    URL = "/api/v1/marketplace/talents"

    def test_lists_open_talents_for_recruiter(self):
        self.as_user(self.recruiter_user)
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200, response.data)
        ids = {row["id"] for row in response.data}
        self.assertTrue({self.yao.id, self.mariam.id, self.kossi.id}.issubset(ids))
        self.assertNotIn(self.recruiter.id, ids)

    def test_filters_by_skill_country_and_availability(self):
        self.yao.country = "SN"
        self.yao.remote = True
        self.yao.save()
        for other in (self.mariam, self.kossi):
            other.remote = False
            other.country = "BF"
            other.save()
        start = date.today()
        make_availability(
            self.by,
            profil=self.yao,
            start_date=start,
            end_date=start + timedelta(days=20),
            status="available",
        )
        self.as_user(self.recruiter_user)
        by_skill = self.client.get(f"{self.URL}?skill={self.python.id}")
        self.assertEqual({row["id"] for row in by_skill.data}, {self.yao.id, self.mariam.id})
        by_country = self.client.get(f"{self.URL}?country=SN")
        self.assertEqual([row["id"] for row in by_country.data], [self.yao.id])
        by_remote = self.client.get(f"{self.URL}?remote=1")
        self.assertEqual([row["id"] for row in by_remote.data], [self.yao.id])
        by_available = self.client.get(f"{self.URL}?available=1")
        self.assertEqual([row["id"] for row in by_available.data], [self.yao.id])

    def test_requires_recruiter(self):
        self.as_user(self.yao.user)
        self.assertEqual(self.client.get(self.URL).status_code, 403)
