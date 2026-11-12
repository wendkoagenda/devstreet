"""
Tests pour les notification_resume.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import NotificationResume
from app.communaute.services.notificationresume_service import NotificationResumeService


class NotificationResumeModelTests(TestCase):
    """
    Tests pour le modèle NotificationResume.
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

        self.notification_resume = NotificationResume.objects.create(
            nombre_nouveautes=100,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_notification_resume_creation(self):
        """Test de création d'un notification_resume."""
        self.assertIsNotNone(self.notification_resume.id)

    def test_notification_resume_str_representation(self):
        """Test de la représentation string du notification_resume."""
        self.assertIsInstance(str(self.notification_resume), str)


class NotificationResumeServiceTests(TestCase):
    """
    Tests pour le service NotificationResume.
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

        self.notificationresume_service = NotificationResumeService()

    def test_get_all_notification_resume(self):
        """Test de récupération de tous les notification_resume."""
        NotificationResume.objects.create(
            nombre_nouveautes=100,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        NotificationResume.objects.create(
            nombre_nouveautes=200,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        notification_resume = self.notificationresume_service.get_all()
        self.assertEqual(notification_resume.count(), 2)

    def test_create_notification_resume(self):
        """Test de création d'un notification_resume."""
        data = {
            "nombre_nouveautes": 300,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        notification_resume = self.notificationresume_service.create(data)


    def test_update_notification_resume(self):
        """Test de mise à jour d'un notification_resume."""
        notification_resume = NotificationResume.objects.create(
            nombre_nouveautes=400,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
        }
        updated_notification_resume = self.notificationresume_service.update(notification_resume.id, updated_data)


    def test_delete_notification_resume(self):
        """Test de suppression d'un notification_resume."""
        notification_resume = NotificationResume.objects.create(
            nombre_nouveautes=500,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.notificationresume_service.delete(notification_resume.id)
        self.assertTrue(success)
        self.assertFalse(NotificationResume.objects.filter(id=notification_resume.id).exists())


class NotificationResumeAPITests(APITestCase):
    """
    Tests pour l'API NotificationResume.
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

        self.notification_resume = NotificationResume.objects.create(
            nombre_nouveautes=600,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_notification_resume_list(self):
        """Test de listage des notification_resume."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/notifications-resume')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_notification_resume_retrieve(self):
        """Test de récupération d'un notification_resume."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/notifications-resume/{self.notification_resume.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_resume_create(self):
        """Test de création d'un notification_resume."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "nombre_nouveautes": 100,
        }

        response = self.client.post(f'/api/v1/notifications-resume', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_notification_resume_partial_update(self):
        """Test de mise à jour partielle d'un notification_resume."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.patch(f'/api/v1/notifications-resume/{self.notification_resume.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_resume_delete(self):
        """Test de suppression d'un notification_resume."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/notifications-resume/{self.notification_resume.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(NotificationResume.objects.filter(id=self.notification_resume.id).exists())

