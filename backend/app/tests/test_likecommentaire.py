"""
Tests pour les like_commentaire.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import LikeCommentaire
from app.communaute.services.likecommentaire_service import LikeCommentaireService


class LikeCommentaireModelTests(TestCase):
    """
    Tests pour le modèle LikeCommentaire.
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

        self.like_commentaire = LikeCommentaire.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_like_commentaire_creation(self):
        """Test de création d'un like_commentaire."""
        self.assertIsNotNone(self.like_commentaire.id)

    def test_like_commentaire_str_representation(self):
        """Test de la représentation string du like_commentaire."""
        self.assertIsInstance(str(self.like_commentaire), str)


class LikeCommentaireServiceTests(TestCase):
    """
    Tests pour le service LikeCommentaire.
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

        self.likecommentaire_service = LikeCommentaireService()

    def test_get_all_like_commentaire(self):
        """Test de récupération de tous les like_commentaire."""
        LikeCommentaire.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )
        LikeCommentaire.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        like_commentaire = self.likecommentaire_service.get_all()
        self.assertEqual(like_commentaire.count(), 2)

    def test_create_like_commentaire(self):
        """Test de création d'un like_commentaire."""
        data = {
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        like_commentaire = self.likecommentaire_service.create(data)


    def test_update_like_commentaire(self):
        """Test de mise à jour d'un like_commentaire."""
        like_commentaire = LikeCommentaire.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
        }
        updated_like_commentaire = self.likecommentaire_service.update(like_commentaire.id, updated_data)


    def test_delete_like_commentaire(self):
        """Test de suppression d'un like_commentaire."""
        like_commentaire = LikeCommentaire.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.likecommentaire_service.delete(like_commentaire.id)
        self.assertTrue(success)
        self.assertFalse(LikeCommentaire.objects.filter(id=like_commentaire.id).exists())


class LikeCommentaireAPITests(APITestCase):
    """
    Tests pour l'API LikeCommentaire.
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

        self.like_commentaire = LikeCommentaire.objects.create(
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_like_commentaire_list(self):
        """Test de listage des like_commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/likes-commentaire')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_like_commentaire_retrieve(self):
        """Test de récupération d'un like_commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/likes-commentaire/{self.like_commentaire.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_commentaire_create(self):
        """Test de création d'un like_commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.post(f'/api/v1/likes-commentaire', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_commentaire_partial_update(self):
        """Test de mise à jour partielle d'un like_commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
        }

        response = self.client.patch(f'/api/v1/likes-commentaire/{self.like_commentaire.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_commentaire_delete(self):
        """Test de suppression d'un like_commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/likes-commentaire/{self.like_commentaire.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LikeCommentaire.objects.filter(id=self.like_commentaire.id).exists())

