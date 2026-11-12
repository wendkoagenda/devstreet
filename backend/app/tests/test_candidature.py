"""
Tests pour Candidature (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_candidature, make_offer, make_profil
from app.marketplace.models import Candidature
from app.marketplace.services.candidature_service import CandidatureService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _CandidatureConfig:
    model = Candidature
    service_class = CandidatureService
    resource_plural = "candidatures"
    patch = {'status': 'shortlisted'}

    make = staticmethod(make_candidature)

    @staticmethod
    def payload(by):
        return {'offer_id': make_offer(by).id, 'profil_id': make_profil(by).id, 'message': 'Motivation'}


class CandidatureModelTests(_CandidatureConfig, ModelTestsMixin, TestCase):
    pass


class CandidatureServiceTests(_CandidatureConfig, ServiceTestsMixin, TestCase):
    pass


class CandidatureAPITests(_CandidatureConfig, ApiTestsMixin, APITestCase):
    pass
