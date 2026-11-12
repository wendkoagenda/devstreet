"""
Liste paginée des modèles métier (exemple : Elitest) : format {count, next, previous, results},
recherche, tri autorisé, taille de page plafonnée.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from app.core.models import Permission, Role
from app.metier.models import Elitest

User = get_user_model()
URL = '/api/v1/elitests'


class ElitestListPaginationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='lecteur', email='lecteur@example.com', password='Mot-de-passe-42')
        permission, _ = Permission.objects.get_or_create(code='elitests.view', defaults={'description': 'Voir'})
        role, _ = Role.objects.get_or_create(name='Lecteur elitests')
        role.permissions.add(permission)
        cls.user.roles.add(role)

        Elitest.objects.bulk_create([
            Elitest(titre=f'Produit {i:02d}', statut='draft' if i % 2 else 'published',
                    description='Café en grains' if i % 5 == 0 else 'Thé vert',
                    prix=Decimal(i), created_by=cls.user.id, updated_by=cls.user.id)
            for i in range(1, 26)
        ])

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.client.force_authenticate(self.user)

    def get(self, **params):
        return self.client.get(URL, params)

    # ------------------------------------------------------------ format et taille
    def test_list_is_paginated_with_the_standard_format(self):
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {'count', 'next', 'previous', 'results'})
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_second_page_holds_the_rest(self):
        response = self.get(page=2)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_page_size_can_be_chosen(self):
        self.assertEqual(len(self.get(page_size=10).data['results']), 10)

    def test_page_size_is_capped(self):
        Elitest.objects.bulk_create([
            Elitest(titre=f'Extra {i}', statut='draft', description='x', prix=Decimal(1),
                    created_by=self.user.id, updated_by=self.user.id) for i in range(100)
        ])
        response = self.get(page_size=1000)
        self.assertEqual(len(response.data['results']), 100)  # plafonné, pas les 125 lignes

    def test_page_out_of_range_is_a_404_not_an_empty_list(self):
        self.assertEqual(self.get(page=99).status_code, status.HTTP_404_NOT_FOUND)

    def test_pages_do_not_overlap(self):
        first = {item['id'] for item in self.get(page=1, page_size=10).data['results']}
        second = {item['id'] for item in self.get(page=2, page_size=10).data['results']}
        self.assertFalse(first & second)

    # ------------------------------------------------------------ recherche
    def test_search_matches_text_fields_case_insensitively(self):
        response = self.get(search='CAFÉ')
        self.assertEqual(response.data['count'], 5)
        self.assertTrue(all('Café' in item['description'] for item in response.data['results']))

    def test_search_matches_the_title(self):
        self.assertEqual(self.get(search='Produit 07').data['count'], 1)

    def test_search_without_match_gives_an_empty_page(self):
        response = self.get(search='introuvable')
        self.assertEqual((response.status_code, response.data['count'], response.data['results']), (200, 0, []))

    def test_count_follows_the_search(self):
        self.assertEqual(self.get(search='Thé', page_size=100).data['count'], 20)

    # ------------------------------------------------------------ tri
    def test_default_order_is_stable(self):
        ids = [item['id'] for item in self.get(page_size=100).data['results']]
        self.assertEqual(ids, sorted(ids))

    def test_ordering_ascending_and_descending(self):
        asc = [Decimal(i['prix']) for i in self.get(ordering='prix', page_size=100).data['results']]
        desc = [Decimal(i['prix']) for i in self.get(ordering='-prix', page_size=100).data['results']]
        self.assertEqual(asc, sorted(asc))
        self.assertEqual(desc, sorted(desc, reverse=True))

    def test_ordering_applies_before_pagination(self):
        top = self.get(ordering='-prix', page_size=3).data['results']
        self.assertEqual([Decimal(i['prix']) for i in top], [Decimal(25), Decimal(24), Decimal(23)])

    def test_search_and_ordering_combine(self):
        response = self.get(search='Café', ordering='-prix')
        prices = [Decimal(i['prix']) for i in response.data['results']]
        self.assertEqual(prices, [Decimal(25), Decimal(20), Decimal(15), Decimal(10), Decimal(5)])

    def test_forbidden_ordering_is_a_clear_400(self):
        for ordering in ('created_by', 'password', '-roles', 'nom_inexistant', 'titre;drop'):
            response = self.get(ordering=ordering)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, ordering)
            self.assertEqual(response.data, {'error': 'Tri invalide'})  # message générique, rien d'interne

    # ------------------------------------------------------------ accès
    def test_anonymous_cannot_list(self):
        self.assertEqual(APIClient().get(URL).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_without_permission_cannot_list(self):
        other = User.objects.create_user(username='sans', email='sans@example.com', password='Mot-de-passe-42')
        self.client.force_authenticate(other)
        self.assertEqual(self.get().status_code, status.HTTP_403_FORBIDDEN)
