"""
Tests pour Swipe (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_profil, make_swipe
from app.marketplace.models import Swipe
from app.marketplace.services.swipe_service import SwipeService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _SwipeConfig:
    model = Swipe
    service_class = SwipeService
    resource_plural = "swipes"
    patch = {'direction': 'pass'}

    make = staticmethod(make_swipe)

    @staticmethod
    def payload(by):
        return {'author_id': make_profil(by).id, 'target_id': make_profil(by).id, 'direction': 'like', 'context': 'network'}


class SwipeModelTests(_SwipeConfig, ModelTestsMixin, TestCase):
    pass


class SwipeServiceTests(_SwipeConfig, ServiceTestsMixin, TestCase):
    pass


class SwipeAPITests(_SwipeConfig, ApiTestsMixin, APITestCase):
    pass
