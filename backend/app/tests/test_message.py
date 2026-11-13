"""
Tests pour les message.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import Message
from app.communaute.services.message_service import MessageService


class MessageModelTests(TestCase):
    """
    Tests pour le modèle Message.
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

        self.message = Message.objects.create(
            texte="Test texte",
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_message_creation(self):
        """Test de création d'un message."""
        self.assertIsNotNone(self.message.id)

    def test_message_str_representation(self):
        """Test de la représentation string du message."""
        self.assertIsInstance(str(self.message), str)


class MessageServiceTests(TestCase):
    """
    Tests pour le service Message.
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

        self.message_service = MessageService()

    def test_get_all_message(self):
        """Test de récupération de tous les message."""
        Message.objects.create(
            texte="Test texte 1",
            created_by=self.user.id,
            updated_by=self.user.id
        )
        Message.objects.create(
            texte="Test texte 2",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        message = self.message_service.get_all()
        self.assertEqual(message.count(), 2)

    def test_create_message(self):
        """Test de création d'un message."""
        data = {
            "texte": "Nouveau texte",
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        message = self.message_service.create(data)
        self.assertEqual(getattr(message, 'texte'), "Nouveau texte")


    def test_update_message(self):
        """Test de mise à jour d'un message."""
        message = Message.objects.create(
            texte="Original texte",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "texte": "Mis à jour texte"
        }
        updated_message = self.message_service.update(message.id, updated_data)
        self.assertEqual(getattr(updated_message, 'texte'), "Mis à jour texte")


    def test_delete_message(self):
        """Test de suppression d'un message."""
        message = Message.objects.create(
            texte="À supprimer texte",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.message_service.delete(message.id)
        self.assertTrue(success)
        self.assertFalse(Message.objects.filter(id=message.id).exists())


class MessageAPITests(APITestCase):
    """
    Tests pour l'API Message.
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

        self.message = Message.objects.create(
            texte="Test API texte",
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_message_list(self):
        """Test de listage des message."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/messages')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_message_retrieve(self):
        """Test de récupération d'un message."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/messages/{self.message.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_create(self):
        """Test de création d'un message."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "texte": "Description créée via API",
        }

        response = self.client.post(f'/api/v1/messages', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_message_partial_update(self):
        """Test de mise à jour partielle d'un message."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "texte": "message mis à jour"
        }

        response = self.client.patch(f'/api/v1/messages/{self.message.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_delete(self):
        """Test de suppression d'un message."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/messages/{self.message.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Message.objects.filter(id=self.message.id).exists())

