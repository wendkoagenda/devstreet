"""
Tests pour les espace.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import Espace
from app.communaute.services.espace_service import EspaceService


class EspaceModelTests(TestCase):
    """
    Tests pour le modèle Espace.
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

        self.espace = Espace.objects.create(
            type="COMMUNAUTE",
            nom="Test nom",
            description="Test description",
            acces="PUBLIC",
            membres_peuvent_publier=True,
            commentaires_ouverts=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_espace_creation(self):
        """Test de création d'un espace."""
        self.assertIsNotNone(self.espace.id)

    def test_espace_str_representation(self):
        """Test de la représentation string du espace."""
        self.assertIsInstance(str(self.espace), str)


class EspaceServiceTests(TestCase):
    """
    Tests pour le service Espace.
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

        self.espace_service = EspaceService()

    def test_get_all_espace(self):
        """Test de récupération de tous les espace."""
        Espace.objects.create(
            type="COMMUNAUTE",
            nom="Test nom 1",
            description="Test description 1",
            acces="PUBLIC",
            membres_peuvent_publier=True,
            commentaires_ouverts=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        Espace.objects.create(
            type="COMMUNAUTE",
            nom="Test nom 2",
            description="Test description 2",
            acces="PUBLIC",
            membres_peuvent_publier=False,
            commentaires_ouverts=False,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        espace = self.espace_service.get_all()
        self.assertEqual(espace.count(), 2)

    def test_create_espace(self):
        """Test de création d'un espace."""
        data = {
            "type": "COMMUNAUTE",
            "nom": "Nouveau nom",
            "description": "Nouveau description",
            "acces": "PUBLIC",
            "membres_peuvent_publier": True,
            "commentaires_ouverts": True,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        espace = self.espace_service.create(data)
        self.assertEqual(getattr(espace, 'type'), "Nouveau type")


    def test_update_espace(self):
        """Test de mise à jour d'un espace."""
        espace = Espace.objects.create(
            type="COMMUNAUTE",
            nom="Original nom",
            description="Original description",
            acces="PUBLIC",
            membres_peuvent_publier=True,
            commentaires_ouverts=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "type": "Mis à jour type"
        }
        updated_espace = self.espace_service.update(espace.id, updated_data)
        self.assertEqual(getattr(updated_espace, 'type'), "Mis à jour type")


    def test_delete_espace(self):
        """Test de suppression d'un espace."""
        espace = Espace.objects.create(
            type="COMMUNAUTE",
            nom="À supprimer nom",
            description="À supprimer description",
            acces="PUBLIC",
            membres_peuvent_publier=False,
            commentaires_ouverts=False,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.espace_service.delete(espace.id)
        self.assertTrue(success)
        self.assertFalse(Espace.objects.filter(id=espace.id).exists())


class EspaceAPITests(APITestCase):
    """
    Tests pour l'API Espace.
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

        self.espace = Espace.objects.create(
            type="COMMUNAUTE",
            nom="Test API nom",
            description="Test API description",
            acces="PUBLIC",
            membres_peuvent_publier=True,
            commentaires_ouverts=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_espace_list(self):
        """Test de listage des espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/espaces')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_espace_retrieve(self):
        """Test de récupération d'un espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/espaces/{self.espace.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_espace_create(self):
        """Test de création d'un espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "type": "COMMUNAUTE",
            "nom": "Test nom via API",
            "description": "Description créée via API",
            "acces": "PUBLIC",
            "membres_peuvent_publier": True,
            "commentaires_ouverts": True,
        }

        response = self.client.post(f'/api/v1/espaces', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_espace_partial_update(self):
        """Test de mise à jour partielle d'un espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "type": "espace mis à jour"
        }

        response = self.client.patch(f'/api/v1/espaces/{self.espace.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_espace_delete(self):
        """Test de suppression d'un espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/espaces/{self.espace.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Espace.objects.filter(id=self.espace.id).exists())

