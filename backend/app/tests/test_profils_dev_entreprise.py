"""Tests des profils dev / entreprise : contraintes, rattachement, profil public du membre et invitations."""
from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from app.marketplace.factories import (
    make_candidature,
    make_company,
    make_connection,
    make_offer,
    make_profil,
    make_review,
    make_swipe,
    make_user,
)
from app.marketplace.models import InvitationEntreprise, Profil
from app.marketplace.services.invitation_service import InvitationService
from app.tests.test_marketplace_market import login


class ProfilTypeConstraintsTests(TestCase):
    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by)

    def test_un_profil_de_chaque_type_au_plus(self):
        user = make_user()
        make_profil(self.by, user=user)
        make_profil(self.by, user=user, type="entreprise", company=self.company)
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_profil(self.by, user=user)
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_profil(self.by, user=user, type="entreprise", company=self.company)

    def test_profil_entreprise_exige_une_entreprise(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Profil.objects.create(
                user=make_user(), type="entreprise", slug="sans-entreprise", country="BF",
                created_by=self.by.id, updated_by=self.by.id,
            )

    def test_profil_dev_refuse_une_entreprise(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Profil.objects.create(
                user=make_user(), type="dev", company=self.company, slug="dev-avec-entreprise", country="BF",
                created_by=self.by.id, updated_by=self.by.id,
            )


class ProfilTypeRulesTests(TestCase):
    def setUp(self):
        self.by = make_user()
        self.dev = make_profil(self.by)
        self.autre_dev = make_profil(self.by)
        self.entreprise = make_profil(self.by, type="entreprise")

    def test_avis_refuse_vers_un_profil_entreprise(self):
        with self.assertRaises(DjangoValidationError):
            make_review(self.by, target=self.entreprise, author=self.dev)

    def test_connexion_autorisee_entre_dev_et_entreprise(self):
        make_connection(self.by, profil_a=self.dev, profil_b=self.entreprise)
        autre_entreprise = make_profil(self.by, type="entreprise")
        make_connection(self.by, profil_a=self.entreprise, profil_b=autre_entreprise)

    def test_candidature_refusee_depuis_un_profil_entreprise(self):
        offer = make_offer(self.by, status="open")
        with self.assertRaises(DjangoValidationError):
            make_candidature(self.by, profil=self.entreprise, offer=offer)

    def test_offre_refusee_avec_un_recruteur_dev(self):
        with self.assertRaises(DjangoValidationError):
            make_offer(self.by, recruiter=self.dev)

    def test_swipe_recrutement_va_de_entreprise_vers_dev(self):
        make_swipe(self.by, author=self.entreprise, target=self.dev, context="recruit")
        with self.assertRaises(DjangoValidationError):
            make_swipe(self.by, author=self.dev, target=self.autre_dev, context="recruit")
        with self.assertRaises(DjangoValidationError):
            make_swipe(self.by, author=self.entreprise, target=self.entreprise, context="recruit")

    def test_swipe_reseau_est_ouvert_aux_deux_types_de_profil(self):
        make_swipe(self.by, author=self.dev, target=self.autre_dev, context="network")
        make_swipe(self.by, author=self.entreprise, target=self.dev, context="network")
        make_swipe(self.by, author=self.dev, target=self.entreprise, context="network")


class MemberProfilesApiTests(APITestCase):
    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by, name="Faso Pay", contact_email="rh@fasopay.example", phone="+22670000000")
        self.owner = make_user(first_name="Fatou", last_name="Sow", username="fatou")
        make_profil(self.by, user=self.owner, headline="Dev Django")
        self.entreprise = make_profil(self.by, user=self.owner, company=self.company, is_company_owner=True)
        self.open_offer = make_offer(self.by, company=self.company, recruiter=self.entreprise, status="open", title="Dev React")
        self.draft_offer = make_offer(self.by, company=self.company, recruiter=self.entreprise, status="draft", title="Brouillon")
        self.outsider = make_user(first_name="Awa", last_name="K", username="awa")

    def get(self, viewer, username):
        login(self.client, viewer)
        return self.client.get(f"/api/v1/membres/u/{username}")

    def test_profil_public_expose_les_deux_profils(self):
        data = self.get(self.outsider, "fatou").data
        self.assertEqual(data["profil_dev"]["headline"], "Dev Django")
        self.assertEqual(data["profil_entreprise"]["company"]["name"], "Faso Pay")

    def test_membre_sans_profil_na_ni_dev_ni_entreprise(self):
        data = self.get(self.owner, "awa").data
        self.assertIsNone(data["profil_dev"])
        self.assertIsNone(data["profil_entreprise"])

    def test_etancheite_des_profils(self):
        data = self.get(self.outsider, "fatou").data
        # Pas d'offres côté dev, pas de compétences ni de candidatures côté entreprise
        self.assertNotIn("offers", data["profil_dev"])
        self.assertNotIn("skills", data["profil_entreprise"])
        self.assertNotIn("candidatures", data["profil_entreprise"])

    def test_un_visiteur_ne_voit_que_les_offres_ouvertes(self):
        titles = [row["title"] for row in self.get(self.outsider, "fatou").data["profil_entreprise"]["offers"]]
        self.assertEqual(titles, ["Dev React"])
        own_titles = [row["title"] for row in self.get(self.owner, "fatou").data["profil_entreprise"]["offers"]]
        self.assertCountEqual(own_titles, ["Dev React", "Brouillon"])

    def test_les_offres_affichees_sont_celles_de_lentreprise_comme_mes_offres(self):
        from app.marketplace.services.market_service import MarketService

        colleague = make_user(username="collegue2")
        colleague_profil = make_profil(self.by, user=colleague, company=self.company)
        make_offer(self.by, company=self.company, recruiter=colleague_profil, status="open", title="Offre du collègue")
        shown = {row["title"] for row in self.get(self.owner, "fatou").data["profil_entreprise"]["offers"]}
        mine = {row["title"] for row in MarketService.my_offers(self.owner)}
        self.assertEqual(shown, mine)
        self.assertIn("Offre du collègue", shown)

    def test_coordonnees_reservees_aux_membres_de_lentreprise(self):
        outsider_company = self.get(self.outsider, "fatou").data["profil_entreprise"]["company"]
        self.assertNotIn("contact_email", outsider_company)
        self.assertNotIn("phone", outsider_company)
        colleague = make_user(username="colleague")
        make_profil(self.by, user=colleague, company=self.company)
        member_company = self.get(colleague, "fatou").data["profil_entreprise"]["company"]
        self.assertEqual(member_company["contact_email"], "rh@fasopay.example")

    def test_recherche_insensible_a_la_casse(self):
        self.assertEqual(self.get(self.outsider, "FATOU").data["username"], "fatou")


class InvitationTests(APITestCase):
    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by, name="Faso Pay")
        self.owner = make_user(first_name="Fatou", last_name="Sow")
        make_profil(self.by, user=self.owner, company=self.company, is_company_owner=True)
        self.guest = make_user(first_name="Seydou", last_name="C", email="seydou@example.com")

    def _token_from(self, link: str) -> str:
        return link.rsplit("/", 1)[-1]

    def create(self, **payload):
        login(self.client, self.owner)
        return self.client.post("/api/v1/marketplace/me/invitations", payload, format="json")

    def test_le_proprietaire_cree_une_invitation_et_voit_le_lien_une_fois(self):
        response = self.create()
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn("/entreprise/invitation/", response.data["link"])
        listing = self.client.get("/api/v1/marketplace/me/invitations").data
        self.assertEqual(len(listing), 1)
        self.assertNotIn("link", listing[0])
        self.assertEqual(listing[0]["state"], "valid")

    def test_un_non_proprietaire_ne_peut_pas_inviter(self):
        colleague = make_user()
        make_profil(self.by, user=colleague, company=self.company)
        login(self.client, colleague)
        self.assertEqual(self.client.post("/api/v1/marketplace/me/invitations", {}, format="json").status_code, 403)

    def test_accepter_cree_un_profil_entreprise_non_proprietaire(self):
        token = self._token_from(self.create().data["link"])
        login(self.client, self.guest)
        response = self.client.post(f"/api/v1/marketplace/invitations/{token}/accept")
        self.assertEqual(response.status_code, 201, response.data)
        profil = Profil.objects.get(user=self.guest, type="entreprise")
        self.assertEqual(profil.company_id, self.company.id)
        self.assertFalse(profil.is_company_owner)

    def test_usage_unique(self):
        token = self._token_from(self.create().data["link"])
        login(self.client, self.guest)
        self.client.post(f"/api/v1/marketplace/invitations/{token}/accept")
        other = make_user()
        login(self.client, other)
        response = self.client.post(f"/api/v1/marketplace/invitations/{token}/accept")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["state"], "accepted")
        self.assertFalse(Profil.objects.filter(user=other).exists())

    def test_invitation_revoquee_ou_expiree_affiche_le_motif(self):
        created = self.create().data
        token = self._token_from(created["link"])
        login(self.client, self.owner)
        self.assertEqual(self.client.delete(f"/api/v1/marketplace/me/invitations/{created['id']}").status_code, 200)
        login(self.client, self.guest)
        self.assertEqual(self.client.get(f"/api/v1/marketplace/invitations/{token}").data["state"], "revoked")

        expired = self.create().data
        InvitationEntreprise.objects.filter(id=expired["id"]).update(expires_at=timezone.now() - timedelta(minutes=1))
        login(self.client, self.guest)
        detail = self.client.get(f"/api/v1/marketplace/invitations/{self._token_from(expired['link'])}").data
        self.assertEqual(detail["state"], "expired")

    def test_un_membre_deja_rattache_ne_peut_pas_rejoindre_une_seconde_entreprise(self):
        make_profil(self.by, user=self.guest, type="entreprise", company=make_company(self.by))
        token = self._token_from(self.create().data["link"])
        login(self.client, self.guest)
        self.assertEqual(self.client.post(f"/api/v1/marketplace/invitations/{token}/accept").status_code, 400)

    def test_invitation_par_e_mail_reservee_a_cette_adresse(self):
        token = self._token_from(self.create(email="seydou@example.com").data["link"])
        login(self.client, make_user(email="intrus@example.com"))
        self.assertEqual(self.client.post(f"/api/v1/marketplace/invitations/{token}/accept").status_code, 400)
        login(self.client, self.guest)
        self.assertEqual(self.client.post(f"/api/v1/marketplace/invitations/{token}/accept").status_code, 201)

    def test_seul_le_hash_du_jeton_est_conserve(self):
        data = InvitationService.create(self.owner)
        token = self._token_from(data["link"])
        self.assertFalse(InvitationEntreprise.objects.filter(token_hash=token).exists())
        self.assertEqual(InvitationEntreprise.objects.count(), 1)


class NetworkWithEntrepriseTests(APITestCase):
    """Le réseau est général : un profil entreprise et un profil dev peuvent se connecter."""

    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by, name="Faso Pay")
        self.recruiter_user = make_user(first_name="Fatou", last_name="Sow", username="fatou")
        # Membre qui n'a qu'un profil entreprise
        self.entreprise = make_profil(self.by, user=self.recruiter_user, company=self.company, is_company_owner=True)
        self.dev_user = make_user(first_name="Yao", last_name="D", username="yao")
        self.dev = make_profil(self.by, user=self.dev_user)

    def swipe(self, target, acting=None):
        payload = {"target_id": target.id, "direction": "like", "context": "network"}
        if acting:
            payload["acting"] = acting
        return self.client.post("/api/v1/marketplace/me/swipes", payload, format="json")

    def test_un_membre_entreprise_seul_peut_ouvrir_le_reseau(self):
        login(self.client, self.recruiter_user)
        response = self.client.get("/api/v1/marketplace/me/deck?context=network")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual([card["id"] for card in response.data], [self.dev.id])

    def test_le_paquet_propose_aussi_des_profils_entreprise_avec_leur_societe(self):
        login(self.client, self.dev_user)
        cards = self.client.get("/api/v1/marketplace/me/deck?context=network").data
        card = next(item for item in cards if item["id"] == self.entreprise.id)
        self.assertEqual(card["type"], "entreprise")
        self.assertEqual(card["company"]["name"], "Faso Pay")
        self.assertEqual(card["username"], "fatou")

    def test_like_reciproque_cree_la_connexion_dev_entreprise(self):
        login(self.client, self.dev_user)
        self.assertFalse(self.swipe(self.entreprise).data["matched"])
        login(self.client, self.recruiter_user)
        self.assertTrue(self.swipe(self.dev).data["matched"])
        connections = self.client.get("/api/v1/marketplace/me/connections").data
        self.assertEqual([item["id"] for item in connections], [self.dev.id])
        login(self.client, self.dev_user)
        connections = self.client.get("/api/v1/marketplace/me/connections").data
        self.assertEqual([item["id"] for item in connections], [self.entreprise.id])

    def test_jamais_ses_propres_profils_dans_le_paquet(self):
        make_profil(self.by, user=self.recruiter_user)  # le recruteur a aussi un profil dev
        login(self.client, self.recruiter_user)
        ids = [card["id"] for card in self.client.get("/api/v1/marketplace/me/deck?context=network&acting=entreprise").data]
        self.assertNotIn(self.entreprise.id, ids)
        self.assertNotIn(Profil.objects.get(user=self.recruiter_user, type="dev").id, ids)

    def test_agir_en_tant_que_choisit_le_profil(self):
        dev_du_recruteur = make_profil(self.by, user=self.recruiter_user)
        login(self.client, self.recruiter_user)
        self.assertEqual(self.swipe(self.dev, acting="entreprise").status_code, 201)
        from app.marketplace.models import Swipe

        self.assertEqual(Swipe.objects.get(target=self.dev).author_id, self.entreprise.id)
        self.assertEqual(self.client.post(
            "/api/v1/marketplace/me/swipes",
            {"target_id": self.entreprise.id, "direction": "like", "context": "network", "acting": "dev"},
            format="json",
        ).status_code, 404)  # pas de swipe vers un de ses propres profils
        self.assertTrue(dev_du_recruteur.id)

    def test_demandes_envoyees_et_recues_avec_le_profil_a_utiliser_pour_repondre(self):
        # Le dev propose à l'entreprise ; l'entreprise a aussi reçu une demande d'un autre dev
        login(self.client, self.dev_user)
        self.swipe(self.entreprise)
        autre_dev = make_profil(self.by)
        make_swipe(self.by, author=autre_dev, target=self.entreprise, direction="like", context="network")

        sent = self.client.get("/api/v1/marketplace/me/network-requests").data["sent"]
        self.assertEqual([row["id"] for row in sent], [self.entreprise.id])
        self.assertEqual(sent[0]["acting"], "dev")

        login(self.client, self.recruiter_user)
        received = self.client.get("/api/v1/marketplace/me/network-requests").data["received"]
        self.assertCountEqual([row["id"] for row in received], [self.dev.id, autre_dev.id])
        self.assertTrue(all(row["acting"] == "entreprise" for row in received))

        # Répondre à une demande reçue la fait disparaître, et crée la connexion si c'est un like
        self.assertTrue(self.swipe(self.dev, acting="entreprise").data["matched"])
        data = self.client.get("/api/v1/marketplace/me/network-requests").data
        self.assertEqual([row["id"] for row in data["received"]], [autre_dev.id])
        self.assertEqual(data["sent"], [])
