"""
Tests pour les like_publication.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import LikePublication
from app.communaute.services.likepublication_service import LikePublicationService


class LikePublicationModelTests(TestCase):
    """
    Tests pour le modèle LikePublication.
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

        self.like_publication = LikePublication.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_like_publication_creation(self):
        """Test de création d'un like_publication."""
        self.assertIsNotNone(self.like_publication.id)

    def test_like_publication_str_representation(self):
        """Test de la représentation string du like_publication."""
        self.assertIsInstance(str(self.like_publication), str)


class LikePublicationServiceTests(TestCase):
    """
    Tests pour le service LikePublication.
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

        self.likepublication_service = LikePublicationService()

    def test_get_all_like_publication(self):
        """Test de récupération de tous les like_publication."""
        LikePublication.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )
        LikePublication.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        like_publication = self.likepublication_service.get_all()
        self.assertEqual(like_publication.count(), 2)

    def test_create_like_publication(self):
        """Test de création d'un like_publication."""
        data = {
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        like_publication = self.likepublication_service.create(data)


    def test_update_like_publication(self):
        """Test de mise à jour d'un like_publication."""
        like_publication = LikePublication.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
        }
        updated_like_publication = self.likepublication_service.update(like_publication.id, updated_data)


    def test_delete_like_publication(self):
        """Test de suppression d'un like_publication."""
        like_publication = LikePublication.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.likepublication_service.delete(like_publication.id)
        self.assertTrue(success)
        self.assertFalse(LikePublication.objects.filter(id=like_publication.id).exists())


class LikePublicationAPITests(APITestCase):
    """
    Tests pour l'API LikePublication.
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

        self.like_publication = LikePublication.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_like_publication_list(self):
        """Test de listage des like_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/likes-publication')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_like_publication_retrieve(self):
        """Test de récupération d'un like_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/likes-publication/{self.like_publication.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_publication_create(self):
        """Test de création d'un like_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.post(f'/api/v1/likes-publication', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_publication_partial_update(self):
        """Test de mise à jour partielle d'un like_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.patch(f'/api/v1/likes-publication/{self.like_publication.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_publication_delete(self):
        """Test de suppression d'un like_publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/likes-publication/{self.like_publication.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LikePublication.objects.filter(id=self.like_publication.id).exists())

