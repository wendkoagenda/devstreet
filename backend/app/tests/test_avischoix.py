"""
Tests pour les avis_choix.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import AvisChoix
from app.communaute.services.avischoix_service import AvisChoixService


class AvisChoixModelTests(TestCase):
    """
    Tests pour le modèle AvisChoix.
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

        self.avis_choix = AvisChoix.objects.create(
            explication="Test explication",
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_avis_choix_creation(self):
        """Test de création d'un avis_choix."""
        self.assertIsNotNone(self.avis_choix.id)

    def test_avis_choix_str_representation(self):
        """Test de la représentation string du avis_choix."""
        self.assertIsInstance(str(self.avis_choix), str)


class AvisChoixServiceTests(TestCase):
    """
    Tests pour le service AvisChoix.
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

        self.avischoix_service = AvisChoixService()

    def test_get_all_avis_choix(self):
        """Test de récupération de tous les avis_choix."""
        AvisChoix.objects.create(
            explication="Test explication 1",
            created_by=self.user.id,
            updated_by=self.user.id
        )
        AvisChoix.objects.create(
            explication="Test explication 2",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        avis_choix = self.avischoix_service.get_all()
        self.assertEqual(avis_choix.count(), 2)

    def test_create_avis_choix(self):
        """Test de création d'un avis_choix."""
        data = {
            "explication": "Nouveau explication",
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        avis_choix = self.avischoix_service.create(data)
        self.assertEqual(getattr(avis_choix, 'explication'), "Nouveau explication")


    def test_update_avis_choix(self):
        """Test de mise à jour d'un avis_choix."""
        avis_choix = AvisChoix.objects.create(
            explication="Original explication",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "explication": "Mis à jour explication"
        }
        updated_avis_choix = self.avischoix_service.update(avis_choix.id, updated_data)
        self.assertEqual(getattr(updated_avis_choix, 'explication'), "Mis à jour explication")


    def test_delete_avis_choix(self):
        """Test de suppression d'un avis_choix."""
        avis_choix = AvisChoix.objects.create(
            explication="À supprimer explication",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.avischoix_service.delete(avis_choix.id)
        self.assertTrue(success)
        self.assertFalse(AvisChoix.objects.filter(id=avis_choix.id).exists())


class AvisChoixAPITests(APITestCase):
    """
    Tests pour l'API AvisChoix.
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

        self.avis_choix = AvisChoix.objects.create(
            explication="Test API explication",
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_avis_choix_list(self):
        """Test de listage des avis_choix."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/avis-choix')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_avis_choix_retrieve(self):
        """Test de récupération d'un avis_choix."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/avis-choix/{self.avis_choix.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_avis_choix_create(self):
        """Test de création d'un avis_choix."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "explication": "Description créée via API",
        }

        response = self.client.post(f'/api/v1/avis-choix', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_avis_choix_partial_update(self):
        """Test de mise à jour partielle d'un avis_choix."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "explication": "avis_choix mis à jour"
        }

        response = self.client.patch(f'/api/v1/avis-choix/{self.avis_choix.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_avis_choix_delete(self):
        """Test de suppression d'un avis_choix."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/avis-choix/{self.avis_choix.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AvisChoix.objects.filter(id=self.avis_choix.id).exists())

