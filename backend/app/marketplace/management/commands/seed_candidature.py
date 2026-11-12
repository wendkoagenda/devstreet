"""Seed de démonstration pour Candidature (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_candidature
from app.marketplace.models import Candidature
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Candidature'
    model = Candidature
    resource_plural = 'candidatures'

    def build(self, admin, index):
        return make_candidature(admin)
