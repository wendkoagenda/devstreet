"""Seed de démonstration pour Swipe (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_swipe
from app.marketplace.models import Swipe
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Swipe'
    model = Swipe
    resource_plural = 'swipes'

    def build(self, admin, index):
        return make_swipe(admin)
