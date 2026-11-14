"""Tests de la durée d'une offre (heures, jours, mois, années) et du niveau « expert »."""
from datetime import date

from django.test import SimpleTestCase

from app.marketplace.market_serializers import OfferWriteSerializer
from app.marketplace.models import Offer
from app.marketplace.services.scoring import LEVEL_MIN_YEARS, mission_period

DEBUT = date(2026, 1, 1)


class MissionPeriodTests(SimpleTestCase):
    def test_mois_par_defaut(self):
        self.assertEqual(mission_period(DEBUT, 3, "mission"), (DEBUT, date(2026, 3, 31)))

    def test_annees(self):
        self.assertEqual(mission_period(DEBUT, 2, "cdd", "year"), (DEBUT, date(2027, 12, 31)))

    def test_jours(self):
        self.assertEqual(mission_period(DEBUT, 10, "mission", "day"), (DEBUT, date(2026, 1, 10)))

    def test_heures_converties_en_jours_de_8_heures(self):
        self.assertEqual(mission_period(DEBUT, 8, "mission", "hour"), (DEBUT, DEBUT))
        self.assertEqual(mission_period(DEBUT, 9, "mission", "hour"), (DEBUT, date(2026, 1, 2)))
        self.assertEqual(mission_period(DEBUT, 40, "mission", "hour"), (DEBUT, date(2026, 1, 5)))

    def test_sans_duree(self):
        self.assertEqual(mission_period(DEBUT, None, "cdi"), (DEBUT, date(2026, 12, 31)))
        self.assertEqual(mission_period(DEBUT, None, "mission", "day"), (DEBUT, date(2026, 1, 31)))


class OfferChoicesTests(SimpleTestCase):
    def test_niveaux_et_unites_disponibles(self):
        levels = [value for value, _label in Offer._meta.get_field("experience_level").choices]
        self.assertEqual(levels, ["junior", "mid", "senior", "expert"])
        units = [value for value, _label in Offer._meta.get_field("contract_duration_unit").choices]
        self.assertEqual(units, ["hour", "day", "month", "year"])
        self.assertIn("expert", LEVEL_MIN_YEARS)

    def test_duree_maximale_selon_l_unite(self):
        base = {
            "title": "Dev", "description": "x", "type": "mission", "experience_level": "expert", "country": "BF",
        }
        ok = OfferWriteSerializer(data={**base, "contract_duration": 500, "contract_duration_unit": "hour"})
        self.assertTrue(ok.is_valid(), ok.errors)
        trop = OfferWriteSerializer(data={**base, "contract_duration": 30, "contract_duration_unit": "year"})
        self.assertFalse(trop.is_valid())
        self.assertIn("contract_duration", trop.errors)
