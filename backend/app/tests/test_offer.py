"""
Tests pour Offer (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_company, make_offer, make_profil
from app.marketplace.models import Offer
from app.marketplace.services.offer_service import OfferService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _OfferConfig:
    model = Offer
    service_class = OfferService
    resource_plural = "offers"
    patch = {'title': 'Offre mise à jour'}

    make = staticmethod(make_offer)

    @staticmethod
    def payload(by):
        return {'company_id': make_company(by).id, 'recruiter_id': make_profil(by, type='entreprise').id, 'title': 'Nouvelle offre', 'slug': f'offre-{uuid4().hex[:8]}', 'description': 'Description', 'type': 'mission', 'experience_level': 'mid', 'country': 'BF'}


class OfferModelTests(_OfferConfig, ModelTestsMixin, TestCase):
    pass


class OfferServiceTests(_OfferConfig, ServiceTestsMixin, TestCase):
    pass


class OfferAPITests(_OfferConfig, ApiTestsMixin, APITestCase):
    pass


class OfferRequiredSkillsAPITests(APITestCase):
    """Écriture de la relation M2M required_skills via l'API (sélecteur de compétences du frontend)."""

    def setUp(self):
        from app.marketplace.factories import make_skill
        from app.tests.marketplace_base import get_admin
        from rest_framework_simplejwt.tokens import RefreshToken

        self.user = get_admin()
        self.skills = [make_skill(self.user), make_skill(self.user)]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + str(RefreshToken.for_user(self.user).access_token))

    def test_create_with_required_skills(self):
        data = _OfferConfig.payload(self.user)
        data["required_skills"] = [skill.id for skill in self.skills]
        response = self.client.post("/api/v1/offers", data, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        offer = Offer.objects.get(id=response.data["id"])
        self.assertEqual(set(offer.required_skills.values_list("id", flat=True)), {skill.id for skill in self.skills})
        self.assertEqual(len(response.data["required_skills"]), 2)

    def test_update_replaces_required_skills(self):
        offer = make_offer(self.user)
        offer.required_skills.set(self.skills)
        response = self.client.put(
            f"/api/v1/offers/{offer.id}", {"required_skills": [self.skills[0].id]}, format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(list(offer.required_skills.values_list("id", flat=True)), [self.skills[0].id])
