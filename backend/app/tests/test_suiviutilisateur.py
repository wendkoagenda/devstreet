"""
Tests pour les suivi_utilisateur.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import SuiviUtilisateur
from app.communaute.services.suiviutilisateur_service import SuiviUtilisateurService


class SuiviUtilisateurModelTests(TestCase):
    """
    Tests pour le modèle SuiviUtilisateur.
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

        self.suivi_utilisateur = SuiviUtilisateur.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_suivi_utilisateur_creation(self):
        """Test de création d'un suivi_utilisateur."""
        self.assertIsNotNone(self.suivi_utilisateur.id)

    def test_suivi_utilisateur_str_representation(self):
        """Test de la représentation string du suivi_utilisateur."""
        self.assertIsInstance(str(self.suivi_utilisateur), str)


class SuiviUtilisateurServiceTests(TestCase):
    """
    Tests pour le service SuiviUtilisateur.
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

        self.suiviutilisateur_service = SuiviUtilisateurService()

    def test_get_all_suivi_utilisateur(self):
        """Test de récupération de tous les suivi_utilisateur."""
        SuiviUtilisateur.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )
        SuiviUtilisateur.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        suivi_utilisateur = self.suiviutilisateur_service.get_all()
        self.assertEqual(suivi_utilisateur.count(), 2)

    def test_create_suivi_utilisateur(self):
        """Test de création d'un suivi_utilisateur."""
        data = {
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        suivi_utilisateur = self.suiviutilisateur_service.create(data)


    def test_update_suivi_utilisateur(self):
        """Test de mise à jour d'un suivi_utilisateur."""
        suivi_utilisateur = SuiviUtilisateur.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
        }
        updated_suivi_utilisateur = self.suiviutilisateur_service.update(suivi_utilisateur.id, updated_data)


    def test_delete_suivi_utilisateur(self):
        """Test de suppression d'un suivi_utilisateur."""
        suivi_utilisateur = SuiviUtilisateur.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.suiviutilisateur_service.delete(suivi_utilisateur.id)
        self.assertTrue(success)
        self.assertFalse(SuiviUtilisateur.objects.filter(id=suivi_utilisateur.id).exists())


class SuiviUtilisateurAPITests(APITestCase):
    """
    Tests pour l'API SuiviUtilisateur.
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

        self.suivi_utilisateur = SuiviUtilisateur.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_suivi_utilisateur_list(self):
        """Test de listage des suivi_utilisateur."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/suivis-utilisateur')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_suivi_utilisateur_retrieve(self):
        """Test de récupération d'un suivi_utilisateur."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/suivis-utilisateur/{self.suivi_utilisateur.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suivi_utilisateur_create(self):
        """Test de création d'un suivi_utilisateur."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.post(f'/api/v1/suivis-utilisateur', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_suivi_utilisateur_partial_update(self):
        """Test de mise à jour partielle d'un suivi_utilisateur."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.patch(f'/api/v1/suivis-utilisateur/{self.suivi_utilisateur.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suivi_utilisateur_delete(self):
        """Test de suppression d'un suivi_utilisateur."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/suivis-utilisateur/{self.suivi_utilisateur.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SuiviUtilisateur.objects.filter(id=self.suivi_utilisateur.id).exists())

