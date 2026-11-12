"""
Tests pour Company (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_company
from app.marketplace.models import Company
from app.marketplace.services.company_service import CompanyService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _CompanyConfig:
    model = Company
    service_class = CompanyService
    resource_plural = "companies"
    patch = {'name': 'Entreprise mise à jour'}

    make = staticmethod(make_company)

    @staticmethod
    def payload(by):
        return {'name': 'Nouvelle entreprise', 'slug': f'nouvelle-{uuid4().hex[:8]}', 'sector': 'fintech', 'country': 'BF'}


class CompanyModelTests(_CompanyConfig, ModelTestsMixin, TestCase):
    pass


class CompanyServiceTests(_CompanyConfig, ServiceTestsMixin, TestCase):
    pass


class CompanyAPITests(_CompanyConfig, ApiTestsMixin, APITestCase):
    pass
