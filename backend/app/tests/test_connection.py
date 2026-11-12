"""
Tests pour Connection (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_connection, make_profil
from app.marketplace.models import Connection
from app.marketplace.services.connection_service import ConnectionService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _ConnectionConfig:
    model = Connection
    service_class = ConnectionService
    resource_plural = "connections"
    patch = {'status': 'blocked'}

    make = staticmethod(make_connection)

    @staticmethod
    def payload(by):
        return {'profil_a_id': make_profil(by).id, 'profil_b_id': make_profil(by).id, 'matched_at': '2026-01-15T10:00:00Z'}


class ConnectionModelTests(_ConnectionConfig, ModelTestsMixin, TestCase):
    pass


class ConnectionServiceTests(_ConnectionConfig, ServiceTestsMixin, TestCase):
    pass


class ConnectionAPITests(_ConnectionConfig, ApiTestsMixin, APITestCase):
    pass
