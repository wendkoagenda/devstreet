"""Tests de la route de santé /api/health."""
from unittest.mock import patch

from django.core.cache import cache
from django.db import OperationalError
from rest_framework import status
from rest_framework.test import APITestCase


class HealthTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_repond_200_sans_authentification(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_repond_503_sans_detail_si_la_base_est_injoignable(self):
        with patch('app.core.views.health_views.connection') as connexion:
            connexion.cursor.side_effect = OperationalError('mot de passe incorrect pour postgres')
            response = self.client.get('/api/health')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.json(), {'status': 'error'})
        self.assertNotIn('postgres', response.content.decode())

    def test_refuse_les_methodes_autres_que_get(self):
        response = self.client.post('/api/health')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
