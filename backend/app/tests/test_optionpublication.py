"""
Tests pour les option_publication.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import OptionPublication
from app.communaute.services.optionpublication_service import OptionPublicationService


class OptionPublicationModelTests(TestCase):
    """
    Tests pour le modèle OptionPublication.
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

        self.option_publication = OptionPublication.objects.create(
            libelle="Test libelle",
            description="Test description",
            position=100,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_option_publication_creation(self):
        """Test de création d'un option_publication."""
        self.assertIsNotNone(self.option_publication.id)

    def test_option_publication_str_representation(self):
        """Test de la représentation string du option_publication."""
        self.assertIsInstance(str(self.option_publication), str)


class OptionPublicationServiceTests(TestCase):
    """
    Tests pour le service OptionPublication.
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

        self.optionpublication_service = OptionPublicationService()

    def test_get_all_option_publication(self):
        """Test de récupération de tous les option_publication."""
        OptionPublication.objects.create(
            libelle="Test libelle 1",
            description="Test description 1",
            position=100,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        OptionPublication.objects.create(
            libelle="Test libelle 2",
            description="Test description 2",
            position=200,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        option_publication = self.optionpublication_service.get_all()
        self.assertEqual(option_publication.count(), 2)

    def test_create_option_publication(self):
        """Test de création d'un option_publication."""
        data = {
            "libelle": "Nouveau libelle",
            "description": "Nouveau description",
            "position": 300,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        option_publication = self.optionpublication_service.create(data)
        self.assertEqual(getattr(option_publication, 'libelle'), "Nouveau libelle")


    def test_update_option_publication(self):
        """Test de mise à jour d'un option_publication."""
        option_publication = OptionPublication.objects.create(
            libelle="Original libelle",
            description="Original description",
            position=400,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "libelle": "Mis à jour libelle"
        }
        updated_option_publication = self.optionpublication_service.update(option_publication.id, updated_data)
        self.assertEqual(getattr(updated_option_publication, 'libelle'), "Mis à jour libelle")


    def test_delete_option_publication(self):
        """Test de suppression d'un option_publication."""
        option_publication = OptionPublication.objects.create(
            libelle="À supprimer libelle",
            description="À supprimer description",
            position=500,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.optionpublication_service.delete(option_publication.id)
        self.assertTrue(success)
        self.assertFalse(OptionPublication.objects.filter(id=option_publication.id).exists())


class OptionPublicationAPITests(APITestCase):
    """
    Tests pour l'API OptionPublication.
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

        self.option_publication = OptionPublication.objects.create(
            libelle="Test API libelle",
            description="Test API description",
            position=600,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_option_publication_list(self):
        """Test de listage des option_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/options-publication')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_option_publication_retrieve(self):
        """Test de récupération d'un option_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/options-publication/{self.option_publication.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_option_publication_create(self):
        """Test de création d'un option_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "libelle": "Test libelle via API",
            "description": "Description créée via API",
            "position": 100,
        }

        response = self.client.post(f'/api/v1/options-publication', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_option_publication_partial_update(self):
        """Test de mise à jour partielle d'un option_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "libelle": "option_publication mis à jour"
        }

        response = self.client.patch(f'/api/v1/options-publication/{self.option_publication.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_option_publication_delete(self):
        """Test de suppression d'un option_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/options-publication/{self.option_publication.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(OptionPublication.objects.filter(id=self.option_publication.id).exists())

