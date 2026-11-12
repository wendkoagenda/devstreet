"""Seed de démonstration de la marketplace : couverture des tables, idempotence, reset et cohérence avec l'API."""
import json
import tempfile
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from app.marketplace.management.commands import _demo_data as demo
from app.marketplace.models import (
    Availability,
    Candidature,
    Company,
    Connection,
    Experience,
    Offer,
    Prestation,
    Profil,
    ProfilHistory,
    ProfilSkill,
    Review,
    Swipe,
)

User = get_user_model()


class MarketplaceDemoSeedTests(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        # hachage rapide : les comptes de démonstration sont recréés à chaque exécution
        override = override_settings(
            DEBUG=True,
            BASE_DIR=self.directory.name,
            PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
        )
        override.enable()
        self.addCleanup(override.disable)

    def seed(self, *args):
        call_command("seed_marketplace_demo", *args, stdout=StringIO())

    def counts(self):
        return {
            model.__name__: model.objects.count()
            for model in (Company, Profil, ProfilSkill, Experience, Prestation, ProfilHistory, Availability, Offer,
                          Candidature, Review, Swipe, Connection)
        }

    def login(self, key):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + str(RefreshToken.for_user(User.objects.get(email=demo_email(key))).access_token))
        return client

    def test_refuses_outside_debug(self):
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                self.seed()

    def test_fills_every_table(self):
        self.seed()
        counts = self.counts()
        for name, total in counts.items():
            self.assertGreater(total, 0, name)
        self.assertEqual(counts["Company"], 4)
        self.assertEqual(counts["Profil"], len(demo.RECRUITERS) + len(demo.DEVS))
        self.assertEqual(counts["Offer"], len(demo.OFFERS))
        self.assertEqual(counts["Candidature"], len(demo.CANDIDATURES))

    def test_is_idempotent(self):
        self.seed()
        first = self.counts()
        self.seed()
        self.assertEqual(self.counts(), first)

    def test_reset_rebuilds_the_same_data(self):
        self.seed()
        first = self.counts()
        self.seed("--reset")
        self.assertEqual(self.counts(), first)

    def test_reset_keeps_real_data(self):
        real = User.objects.create_user(username="vrai", email="vrai@example.com", password="x-vrai-12345")
        self.seed()
        self.seed("--reset")
        self.assertTrue(User.objects.filter(id=real.id).exists())
        self.assertEqual(User.objects.filter(email__endswith=f"@{demo.DOMAIN}").count(), len(demo.RECRUITERS) + len(demo.DEVS))

    def test_password_is_generated_outside_the_repository(self):
        self.seed()
        path = Path(self.directory.name) / ".local" / "demo.credentials.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["password"]), 24)
        self.assertTrue(User.objects.get(email=demo_email("awa")).check_password(data["password"]))
        self.assertIn(demo_email("fatou"), data["marketplace_accounts"])
        self.seed()  # le mot de passe est conservé d'une exécution à l'autre
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["password"], data["password"])

    def test_accepted_candidatures_book_the_calendar(self):
        self.seed()
        accepted = Candidature.objects.filter(status="accepted")
        self.assertEqual(accepted.count(), 3)
        for candidature in accepted:
            busy = Availability.objects.get(profil=candidature.profil, source="mission", status="busy")
            self.assertIn(candidature.offer.title, busy.note)
        self.assertTrue(all(c.decided_at for c in Candidature.objects.exclude(status="sent")))

    def test_manual_periods_do_not_overlap(self):
        self.seed()
        for profil in Profil.objects.all():
            periods = list(Availability.objects.filter(profil=profil).order_by("start_date"))
            for before, after in zip(periods, periods[1:]):
                self.assertLess(before.end_date, after.start_date, profil.slug)

    def test_connections_come_from_mutual_network_likes(self):
        self.seed()
        self.assertEqual(Connection.objects.filter(status="matched").count(), 4)
        self.assertEqual(Connection.objects.filter(status="blocked").count(), 1)
        for connection in Connection.objects.all():
            self.assertLess(connection.profil_a_id, connection.profil_b_id)

    def test_offer_statuses_and_closed_review_link(self):
        self.seed()
        self.assertEqual(set(Offer.objects.values_list("status", flat=True)), {"open", "draft", "closed"})
        linked = Review.objects.filter(candidature__isnull=False)
        self.assertEqual(linked.count(), 2)
        self.assertTrue(Review.objects.filter(is_public=False).exists())

    def test_every_company_has_a_recruiter_owner(self):
        self.seed()
        for company in Company.objects.all():
            self.assertTrue(Profil.objects.filter(company=company, is_company_owner=True).exists(), company.name)

    def test_demo_data_works_through_the_user_api(self):
        self.seed()
        # candidate : offres classées avec score, la sienne marquée « postulée »
        awa = self.login("awa")
        offers = awa.get("/api/v1/marketplace/offers").data
        scores = [row["score"] for row in offers]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(len(row["breakdown"]) == 6 for row in offers))
        self.assertEqual({row["status"] for row in offers}, {"open"})
        applied = [row for row in offers if row.get("my_candidature")]
        self.assertEqual({row["my_candidature"]["status"] for row in applied}, {"accepted", "sent"})
        self.assertEqual(len(awa.get("/api/v1/marketplace/me/candidatures").data), 2)
        self.assertTrue(awa.get("/api/v1/marketplace/me/cv").content.startswith(b"%PDF"))
        # recruteur : vivier, candidatures reçues et paquet de cartes
        fatou = self.login("fatou")
        self.assertEqual(len(fatou.get("/api/v1/marketplace/me/pool").data), 4)
        offer = Offer.objects.get(slug="faso-pay-front-react-cdi")
        received = fatou.get(f"/api/v1/marketplace/me/offers/{offer.id}/candidatures").data
        self.assertEqual({row["status"] for row in received}, {"shortlisted", "sent", "rejected"})
        self.assertGreater(len(fatou.get("/api/v1/marketplace/me/deck?context=recruit").data), 0)
        # réseau : Ibrahim a deux connexions et un paquet à découvrir
        ibrahim = self.login("ibrahim")
        self.assertEqual(len(ibrahim.get("/api/v1/marketplace/me/connections").data), 2)
        self.assertEqual(len(self.login("moussa").get("/api/v1/marketplace/me/connections").data), 1)
        self.assertEqual(ibrahim.get("/api/v1/marketplace/me/availabilities").status_code, 200)


def demo_email(key):
    return f"{key}@{demo.DOMAIN}"
