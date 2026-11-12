"""Seed de démonstration pour Offer (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_offer
from app.marketplace.models import Offer
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Offer'
    model = Offer
    resource_plural = 'offers'

    def build(self, admin, index):
        return make_offer(admin)
