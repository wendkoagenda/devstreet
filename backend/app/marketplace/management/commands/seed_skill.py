"""Seed de démonstration pour Skill (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.models import Skill
from ._seed_base import MarketplaceSeedCommand

NAMES = [
    {'name': 'Django', 'slug': 'django', 'type': 'hard', 'category': 'backend'},
    {'name': 'React', 'slug': 'react', 'type': 'hard', 'category': 'frontend'},
    {'name': 'Communication', 'slug': 'communication', 'type': 'soft', 'category': 'soft'},
]


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Skill'
    model = Skill
    resource_plural = 'skills'

    def build(self, admin, index):
        return Skill.objects.create(**{**NAMES[index - 1], 'created_by': admin.id, 'updated_by': admin.id})
