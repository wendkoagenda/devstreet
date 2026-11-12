"""
Tests pour Profil (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_profil, make_user
from app.marketplace.models import Profil
from app.marketplace.services.profil_service import ProfilService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _ProfilConfig:
    model = Profil
    service_class = ProfilService
    resource_plural = "profils"
    patch = {'headline': 'Accroche mise à jour'}

    make = staticmethod(make_profil)

    @staticmethod
    def payload(by):
        return {'user_id': make_user().id, 'slug': f'profil-{uuid4().hex[:8]}', 'country': 'BF'}


class ProfilModelTests(_ProfilConfig, ModelTestsMixin, TestCase):
    pass


class ProfilServiceTests(_ProfilConfig, ServiceTestsMixin, TestCase):
    pass


class ProfilAPITests(_ProfilConfig, ApiTestsMixin, APITestCase):
    pass


class ProfilUserIdTests(APITestCase):
    """Le profil expose l'identifiant de son compte (user_id), jamais l'utilisateur complet."""

    def test_user_id_exposed_without_user_details(self):
        from app.tests.marketplace_base import get_admin
        from rest_framework_simplejwt.tokens import RefreshToken

        admin = get_admin()
        profil = make_profil(admin)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + str(RefreshToken.for_user(admin).access_token))
        response = self.client.get(f"/api/v1/profils/{profil.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user_id"], profil.user_id)
        self.assertNotIn("user", response.data)
        self.assertNotIn("password", str(response.data))
