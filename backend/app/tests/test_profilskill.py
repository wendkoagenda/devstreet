"""
Tests pour ProfilSkill (modèle, service et API), avec objets liés créés par app.marketplace.factories.
"""
from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import make_profil, make_profil_skill, make_skill
from app.marketplace.models import ProfilSkill
from app.marketplace.services.profilskill_service import ProfilSkillService
from app.tests.marketplace_base import ApiTestsMixin, ModelTestsMixin, ServiceTestsMixin


class _ProfilSkillConfig:
    model = ProfilSkill
    service_class = ProfilSkillService
    resource_plural = "profil-skills"
    patch = {'years': 5}

    make = staticmethod(make_profil_skill)

    @staticmethod
    def payload(by):
        return {'profil_id': make_profil(by).id, 'skill_id': make_skill(by).id, 'level': 4, 'years': 3}


class ProfilSkillModelTests(_ProfilSkillConfig, ModelTestsMixin, TestCase):
    pass


class ProfilSkillServiceTests(_ProfilSkillConfig, ServiceTestsMixin, TestCase):
    pass


class ProfilSkillAPITests(_ProfilSkillConfig, ApiTestsMixin, APITestCase):
    pass
