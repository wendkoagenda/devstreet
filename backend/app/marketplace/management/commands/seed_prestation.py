"""Seed de démonstration pour Prestation (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_prestation
from app.marketplace.models import Prestation
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Prestation'
    model = Prestation
    resource_plural = 'prestations'

    def build(self, admin, index):
        return make_prestation(admin)
