"""
Tests pour Review (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_profil, make_review
from app.marketplace.models import Review
from app.marketplace.services.review_service import ReviewService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _ReviewConfig:
    model = Review
    service_class = ReviewService
    resource_plural = "reviews"
    patch = {'comment': 'Commentaire mis à jour'}

    make = staticmethod(make_review)

    @staticmethod
    def payload(by):
        return {'target_id': make_profil(by).id, 'author_id': make_profil(by).id, 'rating': 4, 'comment': 'Bien'}


class ReviewModelTests(_ReviewConfig, ModelTestsMixin, TestCase):
    pass


class ReviewServiceTests(_ReviewConfig, ServiceTestsMixin, TestCase):
    pass


class ReviewAPITests(_ReviewConfig, ApiTestsMixin, APITestCase):
    pass
