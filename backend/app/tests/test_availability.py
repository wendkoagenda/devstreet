"""
Tests pour Availability (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_availability, make_profil
from app.marketplace.models import Availability
from app.marketplace.services.availability_service import AvailabilityService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _AvailabilityConfig:
    model = Availability
    service_class = AvailabilityService
    resource_plural = "availabilities"
    patch = {'note': 'Note mise à jour'}

    make = staticmethod(make_availability)

    @staticmethod
    def payload(by):
        return {'profil_id': make_profil(by).id, 'start_date': '2026-02-01', 'end_date': '2026-02-28', 'status': 'busy'}


class AvailabilityModelTests(_AvailabilityConfig, ModelTestsMixin, TestCase):
    pass


class AvailabilityServiceTests(_AvailabilityConfig, ServiceTestsMixin, TestCase):
    pass


class AvailabilityAPITests(_AvailabilityConfig, ApiTestsMixin, APITestCase):
    pass
