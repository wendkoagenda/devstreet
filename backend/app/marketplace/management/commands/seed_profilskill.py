"""Seed de démonstration pour ProfilSkill (données liées incluses, via app.marketplace.factories)."""
from app.marketplace.factories import make_profil_skill
from app.marketplace.models import ProfilSkill
from ._seed_base import MarketplaceSeedCommand


class Command(MarketplaceSeedCommand):
    help = 'Créer des données de démonstration pour ProfilSkill'
    model = ProfilSkill
    resource_plural = 'profil-skills'

    def build(self, admin, index):
        return make_profil_skill(admin, level=index + 1)
