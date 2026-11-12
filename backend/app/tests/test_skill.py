"""
Tests pour Skill (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_skill
from app.marketplace.models import Skill
from app.marketplace.services.skill_service import SkillService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _SkillConfig:
    model = Skill
    service_class = SkillService
    resource_plural = "skills"
    patch = {'name': 'Compétence mise à jour'}

    make = staticmethod(make_skill)

    @staticmethod
    def payload(by):
        return {'name': f'Skill {uuid4().hex[:8]}', 'slug': f'skill-{uuid4().hex[:8]}', 'type': 'hard'}


class SkillModelTests(_SkillConfig, ModelTestsMixin, TestCase):
    pass


class SkillServiceTests(_SkillConfig, ServiceTestsMixin, TestCase):
    pass


class SkillAPITests(_SkillConfig, ApiTestsMixin, APITestCase):
    pass
