"""
Tests pour Experience (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_experience, make_profil
from app.marketplace.models import Experience
from app.marketplace.services.experience_service import ExperienceService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _ExperienceConfig:
    model = Experience
    service_class = ExperienceService
    resource_plural = "experiences"
    patch = {'title': 'Poste mis à jour'}

    make = staticmethod(make_experience)

    @staticmethod
    def payload(by):
        return {'profil_id': make_profil(by).id, 'title': 'Dev', 'company_name': 'Acme', 'start_date': '2024-01-01'}


class ExperienceModelTests(_ExperienceConfig, ModelTestsMixin, TestCase):
    pass


class ExperienceServiceTests(_ExperienceConfig, ServiceTestsMixin, TestCase):
    pass


class ExperienceAPITests(_ExperienceConfig, ApiTestsMixin, APITestCase):
    pass
