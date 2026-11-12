"""Seed de démonstration pour ProfilHistory (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_profil_history
from app.marketplace.models import ProfilHistory
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour ProfilHistory'
    model = ProfilHistory
    resource_plural = 'profil-histories'

    def build(self, admin, index):
        return make_profil_history(admin)
