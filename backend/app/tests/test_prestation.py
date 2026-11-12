"""
Tests pour Prestation (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_prestation, make_profil
from app.marketplace.models import Prestation
from app.marketplace.services.prestation_service import PrestationService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _PrestationConfig:
    model = Prestation
    service_class = PrestationService
    resource_plural = "prestations"
    patch = {'title': 'Prestation mise à jour'}

    make = staticmethod(make_prestation)

    @staticmethod
    def payload(by):
        return {'profil_id': make_profil(by).id, 'title': 'Prestation', 'slug': f'prestation-{uuid4().hex[:8]}', 'description': 'Contenu', 'category': 'web', 'price': '100000.00', 'delivery_days': 7}


class PrestationModelTests(_PrestationConfig, ModelTestsMixin, TestCase):
    pass


class PrestationServiceTests(_PrestationConfig, ServiceTestsMixin, TestCase):
    pass


class PrestationAPITests(_PrestationConfig, ApiTestsMixin, APITestCase):
    pass
