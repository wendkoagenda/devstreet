"""
Tests pour les confirmation_aide.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import ConfirmationAide
from app.communaute.services.confirmationaide_service import ConfirmationAideService


class ConfirmationAideModelTests(TestCase):
    """
    Tests pour le modèle ConfirmationAide.
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

        self.confirmation_aide = ConfirmationAide.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_confirmation_aide_creation(self):
        """Test de création d'un confirmation_aide."""
        self.assertIsNotNone(self.confirmation_aide.id)

    def test_confirmation_aide_str_representation(self):
        """Test de la représentation string du confirmation_aide."""
        self.assertIsInstance(str(self.confirmation_aide), str)


class ConfirmationAideServiceTests(TestCase):
    """
    Tests pour le service ConfirmationAide.
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

        self.confirmationaide_service = ConfirmationAideService()

    def test_get_all_confirmation_aide(self):
        """Test de récupération de tous les confirmation_aide."""
        ConfirmationAide.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )
        ConfirmationAide.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        confirmation_aide = self.confirmationaide_service.get_all()
        self.assertEqual(confirmation_aide.count(), 2)

    def test_create_confirmation_aide(self):
        """Test de création d'un confirmation_aide."""
        data = {
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        confirmation_aide = self.confirmationaide_service.create(data)


    def test_update_confirmation_aide(self):
        """Test de mise à jour d'un confirmation_aide."""
        confirmation_aide = ConfirmationAide.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
        }
        updated_confirmation_aide = self.confirmationaide_service.update(confirmation_aide.id, updated_data)


    def test_delete_confirmation_aide(self):
        """Test de suppression d'un confirmation_aide."""
        confirmation_aide = ConfirmationAide.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.confirmationaide_service.delete(confirmation_aide.id)
        self.assertTrue(success)
        self.assertFalse(ConfirmationAide.objects.filter(id=confirmation_aide.id).exists())


class ConfirmationAideAPITests(APITestCase):
    """
    Tests pour l'API ConfirmationAide.
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

        self.confirmation_aide = ConfirmationAide.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_confirmation_aide_list(self):
        """Test de listage des confirmation_aide."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/confirmations-aide')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_confirmation_aide_retrieve(self):
        """Test de récupération d'un confirmation_aide."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/confirmations-aide/{self.confirmation_aide.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirmation_aide_create(self):
        """Test de création d'un confirmation_aide."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.post(f'/api/v1/confirmations-aide', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_confirmation_aide_partial_update(self):
        """Test de mise à jour partielle d'un confirmation_aide."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.patch(f'/api/v1/confirmations-aide/{self.confirmation_aide.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirmation_aide_delete(self):
        """Test de suppression d'un confirmation_aide."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/confirmations-aide/{self.confirmation_aide.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ConfirmationAide.objects.filter(id=self.confirmation_aide.id).exists())

