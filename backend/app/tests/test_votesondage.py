"""
Tests pour les vote_sondage.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import VoteSondage
from app.communaute.services.votesondage_service import VoteSondageService


class VoteSondageModelTests(TestCase):
    """
    Tests pour le modèle VoteSondage.
    """

    def setUp(self):
        """Configuration initiale pour les tests."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            self.user = User.objects.get(email='admin@example.com')
        except User.DoesNotExist:
            self.user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )

        self.vote_sondage = VoteSondage.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_vote_sondage_creation(self):
        """Test de création d'un vote_sondage."""
        self.assertIsNotNone(self.vote_sondage.id)

    def test_vote_sondage_str_representation(self):
        """Test de la représentation string du vote_sondage."""
        self.assertIsInstance(str(self.vote_sondage), str)


class VoteSondageServiceTests(TestCase):
    """
    Tests pour le service VoteSondage.
    """

    def setUp(self):
        """Configuration initiale pour les tests."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            self.user = User.objects.get(email='admin@example.com')
        except User.DoesNotExist:
            self.user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )

        self.votesondage_service = VoteSondageService()

    def test_get_all_vote_sondage(self):
        """Test de récupération de tous les vote_sondage."""
        VoteSondage.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )
        VoteSondage.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        vote_sondage = self.votesondage_service.get_all()
        self.assertEqual(vote_sondage.count(), 2)

    def test_create_vote_sondage(self):
        """Test de création d'un vote_sondage."""
        data = {
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        vote_sondage = self.votesondage_service.create(data)


    def test_update_vote_sondage(self):
        """Test de mise à jour d'un vote_sondage."""
        vote_sondage = VoteSondage.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
        }
        updated_vote_sondage = self.votesondage_service.update(vote_sondage.id, updated_data)


    def test_delete_vote_sondage(self):
        """Test de suppression d'un vote_sondage."""
        vote_sondage = VoteSondage.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.votesondage_service.delete(vote_sondage.id)
        self.assertTrue(success)
        self.assertFalse(VoteSondage.objects.filter(id=vote_sondage.id).exists())


class VoteSondageAPITests(APITestCase):
    """
    Tests pour l'API VoteSondage.
    """

    def setUp(self):
        """Configuration initiale pour les tests."""
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import RefreshToken
        User = get_user_model()

        try:
            self.user = User.objects.get(email='admin@example.com')
        except User.DoesNotExist:
            self.user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.vote_sondage = VoteSondage.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_vote_sondage_list(self):
        """Test de listage des vote_sondage."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/votes-sondage')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_vote_sondage_retrieve(self):
        """Test de récupération d'un vote_sondage."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/votes-sondage/{self.vote_sondage.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vote_sondage_create(self):
        """Test de création d'un vote_sondage."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.post(f'/api/v1/votes-sondage', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_vote_sondage_partial_update(self):
        """Test de mise à jour partielle d'un vote_sondage."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.patch(f'/api/v1/votes-sondage/{self.vote_sondage.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vote_sondage_delete(self):
        """Test de suppression d'un vote_sondage."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/votes-sondage/{self.vote_sondage.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(VoteSondage.objects.filter(id=self.vote_sondage.id).exists())

