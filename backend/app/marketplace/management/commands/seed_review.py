"""Seed de démonstration pour Review (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_review
from app.marketplace.models import Review
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Review'
    model = Review
    resource_plural = 'reviews'

    def build(self, admin, index):
        return make_review(admin, rating=3 + index % 3)
