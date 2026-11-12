"""
Tests pour les dragon.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.metier.models import Dragon
from app.metier.services.dragon_service import DragonService


class DragonModelTests(TestCase):
    """
    Tests pour le modèle Dragon.
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

        self.dragon = Dragon.objects.create(
            titre="Test titre",
            statut="draft",
            description="Test description",
            prix=99.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_dragon_creation(self):
        """Test de création d'un dragon."""
        self.assertIsNotNone(self.dragon.id)

    def test_dragon_str_representation(self):
        """Test de la représentation string du dragon."""
        self.assertIsInstance(str(self.dragon), str)


class DragonServiceTests(TestCase):
    """
    Tests pour le service Dragon.
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

        self.dragon_service = DragonService()

    def test_get_all_dragon(self):
        """Test de récupération de tous les dragon."""
        Dragon.objects.create(
            titre="Test titre 1",
            statut="draft",
            description="Test description 1",
            prix=99.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        Dragon.objects.create(
            titre="Test titre 2",
            statut="draft",
            description="Test description 2",
            prix=199.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        dragon = self.dragon_service.get_all()
        self.assertEqual(dragon.count(), 2)

    def test_create_dragon(self):
        """Test de création d'un dragon."""
        data = {
            "titre": "Nouveau titre",
            "statut": "draft",
            "description": "Nouveau description",
            "prix": 299.99,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        dragon = self.dragon_service.create(data)
        self.assertEqual(getattr(dragon, 'titre'), "Nouveau titre")


    def test_update_dragon(self):
        """Test de mise à jour d'un dragon."""
        dragon = Dragon.objects.create(
            titre="Original titre",
            statut="draft",
            description="Original description",
            prix=399.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "titre": "Mis à jour titre"
        }
        updated_dragon = self.dragon_service.update(dragon.id, updated_data)
        self.assertEqual(getattr(updated_dragon, 'titre'), "Mis à jour titre")


    def test_delete_dragon(self):
        """Test de suppression d'un dragon."""
        dragon = Dragon.objects.create(
            titre="À supprimer titre",
            statut="draft",
            description="À supprimer description",
            prix=499.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.dragon_service.delete(dragon.id)
        self.assertTrue(success)
        self.assertFalse(Dragon.objects.filter(id=dragon.id).exists())


class DragonAPITests(APITestCase):
    """
    Tests pour l'API Dragon.
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

        self.dragon = Dragon.objects.create(
            titre="Test API titre",
            statut="draft",
            description="Test API description",
            prix=599.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_dragon_list(self):
        """Test de listage des dragon."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/dragons')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_dragon_retrieve(self):
        """Test de récupération d'un dragon."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/dragons/{self.dragon.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dragon_create(self):
        """Test de création d'un dragon."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "titre": "Test titre via API",
            "statut": "draft",
            "description": "Description créée via API",
            "prix": "99.99",
        }

        response = self.client.post(f'/api/v1/dragons', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_dragon_partial_update(self):
        """Test de mise à jour partielle d'un dragon."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "titre": "dragon mis à jour"
        }

        response = self.client.patch(f'/api/v1/dragons/{self.dragon.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dragon_delete(self):
        """Test de suppression d'un dragon."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/dragons/{self.dragon.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Dragon.objects.filter(id=self.dragon.id).exists())

    def test_dragon_file_upload_document(self):
        """Test de création avec upload fichier (document)."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        uploaded = SimpleUploadedFile(
            "test-upload.pdf",
            b"%PDF-1.4 test content",
            content_type="application/pdf",
        )
        relative_path = "dragon_documents/test-upload.pdf"
        data = {
            "titre": "Test titre upload",
            "statut": "draft",
            "description": "Description upload",
            "prix": "99.99",
            "document": uploaded,
            "document_path": relative_path,
        }

        response = self.client.post(
            f'/api/v1/dragons',
            data,
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('document', response.data)
        self.assertTrue(str(response.data['document']).startswith('dragon_documents/'))

