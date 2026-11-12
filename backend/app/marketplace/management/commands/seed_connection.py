"""Seed de démonstration pour Connection (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_connection
from app.marketplace.models import Connection
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Connection'
    model = Connection
    resource_plural = 'connections'

    def build(self, admin, index):
        return make_connection(admin)
