"""Villes par pays : fusion des grandes villes et de l'API publique, cache, repli en saisie libre."""
from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from app.core.services import geo_service

User = get_user_model()

PAYLOAD = {
    'error': False,
    'data': [
        {'iso2': 'BF', 'country': 'Burkina Faso', 'cities': ['Bam', 'Banfora', 'Zorgho']},
        {'iso2': 'JP', 'country': 'Japan', 'cities': ['Tokyo', 'osaka', 'Kyoto']},
    ],
}


def fake_response(payload=PAYLOAD):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class GeoServiceTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    @patch('app.core.services.geo_service.httpx.get', return_value=fake_response())
    def test_grandes_villes_en_tete_puis_api_sans_doublon(self, _get):
        result = geo_service.cities_for('bf')
        self.assertEqual(result['country'], 'BF')
        self.assertTrue(result['available'])
        self.assertEqual(result['cities'][:2], ['Ouagadougou', 'Bobo-Dioulasso'])
        self.assertEqual(result['cities'].count('Banfora'), 1)  # présente dans les deux listes
        self.assertIn('Zorgho', result['cities'])

    @patch('app.core.services.geo_service.httpx.get', return_value=fake_response())
    def test_pays_sans_grandes_villes_trie_par_ordre_alphabetique(self, _get):
        self.assertEqual(geo_service.cities_for('JP')['cities'], ['Kyoto', 'osaka', 'Tokyo'])

    @patch('app.core.services.geo_service.httpx.get', return_value=fake_response())
    def test_la_liste_est_mise_en_cache(self, get):
        geo_service.cities_for('BF')
        geo_service.cities_for('JP')
        self.assertEqual(get.call_count, 1)

    @patch('app.core.services.geo_service.httpx.get', side_effect=httpx.ConnectError('panne'))
    def test_service_en_panne(self, get):
        # Pays prioritaire : les grandes villes suffisent
        self.assertIn('Ouagadougou', geo_service.cities_for('BF')['cities'])
        # Autre pays : saisie libre
        self.assertEqual(geo_service.cities_for('JP'), {'country': 'JP', 'cities': [], 'available': False})
        # L'échec est mémorisé : pas de nouvel appel à chaque requête
        self.assertEqual(get.call_count, 1)

    def test_code_invalide(self):
        self.assertFalse(geo_service.cities_for('FRA')['available'])
        self.assertFalse(geo_service.cities_for('1')['available'])


class GeoApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    def test_reserve_aux_membres_connectes(self):
        response = APIClient().get('/api/v1/geo/countries/BF/cities')
        self.assertIn(response.status_code, (401, 403))

    @patch('app.core.services.geo_service.httpx.get', return_value=fake_response())
    def test_villes_d_un_pays(self, _get):
        user = User.objects.create_user(email='geo@example.com', username='geo', password='x', first_name='G', last_name='E')
        client = APIClient()
        client.force_authenticate(user)
        response = client.get('/api/v1/geo/countries/BF/cities')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['cities'][0], 'Ouagadougou')
