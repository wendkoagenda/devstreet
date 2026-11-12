"""Seed de démonstration pour Experience (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_experience
from app.marketplace.models import Experience
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Experience'
    model = Experience
    resource_plural = 'experiences'

    def build(self, admin, index):
        return make_experience(admin)
