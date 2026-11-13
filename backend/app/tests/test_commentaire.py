"""
Tests pour les commentaire.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import Commentaire
from app.communaute.services.commentaire_service import CommentaireService


class CommentaireModelTests(TestCase):
    """
    Tests pour le modèle Commentaire.
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

        self.commentaire = Commentaire.objects.create(
            nature="COMMENTAIRE",
            texte="Test texte",
            est_anonyme=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_commentaire_creation(self):
        """Test de création d'un commentaire."""
        self.assertIsNotNone(self.commentaire.id)

    def test_commentaire_str_representation(self):
        """Test de la représentation string du commentaire."""
        self.assertIsInstance(str(self.commentaire), str)


class CommentaireServiceTests(TestCase):
    """
    Tests pour le service Commentaire.
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

        self.commentaire_service = CommentaireService()

    def test_get_all_commentaire(self):
        """Test de récupération de tous les commentaire."""
        Commentaire.objects.create(
            nature="COMMENTAIRE",
            texte="Test texte 1",
            est_anonyme=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        Commentaire.objects.create(
            nature="COMMENTAIRE",
            texte="Test texte 2",
            est_anonyme=False,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        commentaire = self.commentaire_service.get_all()
        self.assertEqual(commentaire.count(), 2)

    def test_create_commentaire(self):
        """Test de création d'un commentaire."""
        data = {
            "nature": "COMMENTAIRE",
            "texte": "Nouveau texte",
            "est_anonyme": True,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        commentaire = self.commentaire_service.create(data)
        self.assertEqual(getattr(commentaire, 'nature'), "Nouveau nature")


    def test_update_commentaire(self):
        """Test de mise à jour d'un commentaire."""
        commentaire = Commentaire.objects.create(
            nature="COMMENTAIRE",
            texte="Original texte",
            est_anonyme=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "nature": "Mis à jour nature"
        }
        updated_commentaire = self.commentaire_service.update(commentaire.id, updated_data)
        self.assertEqual(getattr(updated_commentaire, 'nature'), "Mis à jour nature")


    def test_delete_commentaire(self):
        """Test de suppression d'un commentaire."""
        commentaire = Commentaire.objects.create(
            nature="COMMENTAIRE",
            texte="À supprimer texte",
            est_anonyme=False,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.commentaire_service.delete(commentaire.id)
        self.assertTrue(success)
        self.assertFalse(Commentaire.objects.filter(id=commentaire.id).exists())


class CommentaireAPITests(APITestCase):
    """
    Tests pour l'API Commentaire.
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

        self.commentaire = Commentaire.objects.create(
            nature="COMMENTAIRE",
            texte="Test API texte",
            est_anonyme=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_commentaire_list(self):
        """Test de listage des commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/commentaires')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_commentaire_retrieve(self):
        """Test de récupération d'un commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/commentaires/{self.commentaire.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_commentaire_create(self):
        """Test de création d'un commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "nature": "COMMENTAIRE",
            "texte": "Description créée via API",
            "est_anonyme": True,
        }

        response = self.client.post(f'/api/v1/commentaires', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_commentaire_partial_update(self):
        """Test de mise à jour partielle d'un commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "nature": "commentaire mis à jour"
        }

        response = self.client.patch(f'/api/v1/commentaires/{self.commentaire.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_commentaire_delete(self):
        """Test de suppression d'un commentaire."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/commentaires/{self.commentaire.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Commentaire.objects.filter(id=self.commentaire.id).exists())

