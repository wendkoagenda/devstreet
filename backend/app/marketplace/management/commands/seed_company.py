"""Seed de démonstration pour Company (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_company
from app.marketplace.models import Company
from ._seed_base import MarketplaceSeedCommand

NAMES = ['Faso Pay', 'AgriConnect', 'EduTech Sahel']
SLUGS = ['faso-pay', 'agriconnect', 'edutech-sahel']


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour Company'
    model = Company
    resource_plural = 'companies'

    def build(self, admin, index):
        return make_company(admin, name=NAMES[index - 1], slug=f'{SLUGS[index - 1]}-{index}')
