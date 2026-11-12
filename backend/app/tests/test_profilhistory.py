"""
Tests pour ProfilHistory (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_profil, make_profil_history
from app.marketplace.models import ProfilHistory
from app.marketplace.services.profilhistory_service import ProfilHistoryService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _ProfilHistoryConfig:
    model = ProfilHistory
    service_class = ProfilHistoryService
    resource_plural = "profil-histories"
    patch = {'new_value': 'valeur mise à jour'}

    make = staticmethod(make_profil_history)

    @staticmethod
    def payload(by):
        return {'profil_id': make_profil(by).id, 'field': 'bio', 'old_value': 'a', 'new_value': 'b'}


class ProfilHistoryModelTests(_ProfilHistoryConfig, ModelTestsMixin, TestCase):
    pass


class ProfilHistoryServiceTests(_ProfilHistoryConfig, ServiceTestsMixin, TestCase):
    pass


class ProfilHistoryAPITests(_ProfilHistoryConfig, ApiTestsMixin, APITestCase):
    pass
