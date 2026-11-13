"""
Tests pour les publication.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import Publication
from app.communaute.services.publication_service import PublicationService


class PublicationModelTests(TestCase):
    """
    Tests pour le modèle Publication.
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

        self.publication = Publication.objects.create(
            type="DISCUSSION",
            titre="Test titre",
            description="Test description",
            plateforme_app="WEB",
            contraintes="Test contraintes",
            justification_finale="Test justification_finale",
            mode_vote="UNIQUE",
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_publication_creation(self):
        """Test de création d'un publication."""
        self.assertIsNotNone(self.publication.id)

    def test_publication_str_representation(self):
        """Test de la représentation string du publication."""
        self.assertIsInstance(str(self.publication), str)


class PublicationServiceTests(TestCase):
    """
    Tests pour le service Publication.
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

        self.publication_service = PublicationService()

    def test_get_all_publication(self):
        """Test de récupération de tous les publication."""
        Publication.objects.create(
            type="DISCUSSION",
            titre="Test titre 1",
            description="Test description 1",
            plateforme_app="WEB",
            contraintes="Test contraintes 1",
            justification_finale="Test justification_finale 1",
            mode_vote="UNIQUE",
            created_by=self.user.id,
            updated_by=self.user.id
        )
        Publication.objects.create(
            type="DISCUSSION",
            titre="Test titre 2",
            description="Test description 2",
            plateforme_app="WEB",
            contraintes="Test contraintes 2",
            justification_finale="Test justification_finale 2",
            mode_vote="UNIQUE",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        publication = self.publication_service.get_all()
        self.assertEqual(publication.count(), 2)

    def test_create_publication(self):
        """Test de création d'un publication."""
        data = {
            "type": "DISCUSSION",
            "titre": "Nouveau titre",
            "description": "Nouveau description",
            "plateforme_app": "WEB",
            "contraintes": "Nouveau contraintes",
            "justification_finale": "Nouveau justification_finale",
            "mode_vote": "UNIQUE",
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        publication = self.publication_service.create(data)
        self.assertEqual(getattr(publication, 'type'), "Nouveau type")


    def test_update_publication(self):
        """Test de mise à jour d'un publication."""
        publication = Publication.objects.create(
            type="DISCUSSION",
            titre="Original titre",
            description="Original description",
            plateforme_app="WEB",
            contraintes="Original contraintes",
            justification_finale="Original justification_finale",
            mode_vote="UNIQUE",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "type": "Mis à jour type"
        }
        updated_publication = self.publication_service.update(publication.id, updated_data)
        self.assertEqual(getattr(updated_publication, 'type'), "Mis à jour type")


    def test_delete_publication(self):
        """Test de suppression d'un publication."""
        publication = Publication.objects.create(
            type="DISCUSSION",
            titre="À supprimer titre",
            description="À supprimer description",
            plateforme_app="WEB",
            contraintes="À supprimer contraintes",
            justification_finale="À supprimer justification_finale",
            mode_vote="UNIQUE",
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.publication_service.delete(publication.id)
        self.assertTrue(success)
        self.assertFalse(Publication.objects.filter(id=publication.id).exists())


class PublicationAPITests(APITestCase):
    """
    Tests pour l'API Publication.
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

        self.publication = Publication.objects.create(
            type="DISCUSSION",
            titre="Test API titre",
            description="Test API description",
            plateforme_app="WEB",
            contraintes="Test API contraintes",
            justification_finale="Test API justification_finale",
            mode_vote="UNIQUE",
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_publication_list(self):
        """Test de listage des publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/publications')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIsInstance(response.data['results'], list)
        # Scroll infini : pas de count (CursorPagination)
        self.assertNotIn('count', response.data)

    def test_publication_retrieve(self):
        """Test de récupération d'un publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/publications/{self.publication.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_publication_create(self):
        """Test de création d'un publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "type": "DISCUSSION",
            "titre": "Test titre via API",
            "description": "Description créée via API",
            "plateforme_app": "WEB",
            "contraintes": "Description créée via API",
            "justification_finale": "Description créée via API",
            "mode_vote": "UNIQUE",
        }

        response = self.client.post(f'/api/v1/publications', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_publication_partial_update(self):
        """Test de mise à jour partielle d'un publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "type": "publication mis à jour"
        }

        response = self.client.patch(f'/api/v1/publications/{self.publication.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_publication_delete(self):
        """Test de suppression d'un publication."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/publications/{self.publication.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Publication.objects.filter(id=self.publication.id).exists())

