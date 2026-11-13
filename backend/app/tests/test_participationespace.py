"""
Tests pour les participation_espace.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import ParticipationEspace
from app.communaute.services.participationespace_service import ParticipationEspaceService


class ParticipationEspaceModelTests(TestCase):
    """
    Tests pour le modèle ParticipationEspace.
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

        self.participation_espace = ParticipationEspace.objects.create(
            role="SUPER_ADMIN",
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_participation_espace_creation(self):
        """Test de création d'un participation_espace."""
        self.assertIsNotNone(self.participation_espace.id)

    def test_participation_espace_str_representation(self):
        """Test de la représentation string du participation_espace."""
        self.assertIsInstance(str(self.participation_espace), str)


class ParticipationEspaceServiceTests(TestCase):
    """
    Tests pour le service ParticipationEspace.
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

        self.participationespace_service = ParticipationEspaceService()

    def test_get_all_participation_espace(self):
        """Test de récupération de tous les participation_espace."""
        ParticipationEspace.objects.create(
            role="SUPER_ADMIN",
            created_by=self.user.id,
            updated_by=self.user.id
        )
        ParticipationEspace.objects.create(
            role="SUPER_ADMIN",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        participation_espace = self.participationespace_service.get_all()
        self.assertEqual(participation_espace.count(), 2)

    def test_create_participation_espace(self):
        """Test de création d'un participation_espace."""
        data = {
            "role": "SUPER_ADMIN",
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        participation_espace = self.participationespace_service.create(data)
        self.assertEqual(getattr(participation_espace, 'role'), "Nouveau role")


    def test_update_participation_espace(self):
        """Test de mise à jour d'un participation_espace."""
        participation_espace = ParticipationEspace.objects.create(
            role="SUPER_ADMIN",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "role": "Mis à jour role"
        }
        updated_participation_espace = self.participationespace_service.update(participation_espace.id, updated_data)
        self.assertEqual(getattr(updated_participation_espace, 'role'), "Mis à jour role")


    def test_delete_participation_espace(self):
        """Test de suppression d'un participation_espace."""
        participation_espace = ParticipationEspace.objects.create(
            role="SUPER_ADMIN",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.participationespace_service.delete(participation_espace.id)
        self.assertTrue(success)
        self.assertFalse(ParticipationEspace.objects.filter(id=participation_espace.id).exists())


class ParticipationEspaceAPITests(APITestCase):
    """
    Tests pour l'API ParticipationEspace.
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

        self.participation_espace = ParticipationEspace.objects.create(
            role="SUPER_ADMIN",
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_participation_espace_list(self):
        """Test de listage des participation_espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/participations-espace')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_participation_espace_retrieve(self):
        """Test de récupération d'un participation_espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/participations-espace/{self.participation_espace.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_participation_espace_create(self):
        """Test de création d'un participation_espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "role": "SUPER_ADMIN",
        }

        response = self.client.post(f'/api/v1/participations-espace', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_participation_espace_partial_update(self):
        """Test de mise à jour partielle d'un participation_espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "role": "participation_espace mis à jour"
        }

        response = self.client.patch(f'/api/v1/participations-espace/{self.participation_espace.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_participation_espace_delete(self):
        """Test de suppression d'un participation_espace."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/participations-espace/{self.participation_espace.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ParticipationEspace.objects.filter(id=self.participation_espace.id).exists())

