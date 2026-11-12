"""Seed de démonstration pour Availability (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_availability
from app.marketplace.models import Availability
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Availability'
    model = Availability
    resource_plural = 'availabilities'

    def build(self, admin, index):
        return make_availability(admin)
