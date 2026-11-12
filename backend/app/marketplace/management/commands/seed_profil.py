"""Seed de démonstration pour Profil (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_profil
from app.marketplace.models import Profil
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Profil'
    model = Profil
    resource_plural = 'profils'

    def build(self, admin, index):
        return make_profil(admin)
