"""
Tests pour les gado.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.garoapp.models import Gado
from app.garoapp.services.gado_service import GadoService


class GadoModelTests(TestCase):
    """
    Tests pour le modèle Gado.
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

        self.gado = Gado.objects.create(
            titre="Test titre",
            statut="draft",
            description="Test description",
            prix=99.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_gado_creation(self):
        """Test de création d'un gado."""
        self.assertIsNotNone(self.gado.id)

    def test_gado_str_representation(self):
        """Test de la représentation string du gado."""
        self.assertIsInstance(str(self.gado), str)


class GadoServiceTests(TestCase):
    """
    Tests pour le service Gado.
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

        self.gado_service = GadoService()

    def test_get_all_gado(self):
        """Test de récupération de tous les gado."""
        Gado.objects.create(
            titre="Test titre 1",
            statut="draft",
            description="Test description 1",
            prix=99.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        Gado.objects.create(
            titre="Test titre 2",
            statut="draft",
            description="Test description 2",
            prix=199.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        gado = self.gado_service.get_all()
        self.assertEqual(gado.count(), 2)

    def test_create_gado(self):
        """Test de création d'un gado."""
        data = {
            "titre": "Nouveau titre",
            "statut": "draft",
            "description": "Nouveau description",
            "prix": 299.99,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        gado = self.gado_service.create(data)
        self.assertEqual(getattr(gado, 'titre'), "Nouveau titre")


    def test_update_gado(self):
        """Test de mise à jour d'un gado."""
        gado = Gado.objects.create(
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
        updated_gado = self.gado_service.update(gado.id, updated_data)
        self.assertEqual(getattr(updated_gado, 'titre'), "Mis à jour titre")


    def test_delete_gado(self):
        """Test de suppression d'un gado."""
        gado = Gado.objects.create(
            titre="À supprimer titre",
            statut="draft",
            description="À supprimer description",
            prix=499.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.gado_service.delete(gado.id)
        self.assertTrue(success)
        self.assertFalse(Gado.objects.filter(id=gado.id).exists())


class GadoAPITests(APITestCase):
    """
    Tests pour l'API Gado.
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

        self.gado = Gado.objects.create(
            titre="Test API titre",
            statut="draft",
            description="Test API description",
            prix=599.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_gado_list(self):
        """Test de listage des gado."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/gados')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_gado_retrieve(self):
        """Test de récupération d'un gado."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/gados/{self.gado.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gado_create(self):
        """Test de création d'un gado."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "titre": "Test titre via API",
            "statut": "draft",
            "description": "Description créée via API",
            "prix": "99.99",
        }

        response = self.client.post(f'/api/v1/gados', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_gado_partial_update(self):
        """Test de mise à jour partielle d'un gado."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "titre": "gado mis à jour"
        }

        response = self.client.patch(f'/api/v1/gados/{self.gado.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gado_delete(self):
        """Test de suppression d'un gado."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/gados/{self.gado.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Gado.objects.filter(id=self.gado.id).exists())

    def test_gado_file_upload_document(self):
        """Test de création avec upload fichier (document)."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        uploaded = SimpleUploadedFile(
            "test-upload.pdf",
            b"%PDF-1.4 test content",
            content_type="application/pdf",
        )
        relative_path = "fusion_documents/test-upload.pdf"
        data = {
            "titre": "Test titre upload",
            "statut": "draft",
            "description": "Description upload",
            "prix": "99.99",
            "document": uploaded,
            "document_path": relative_path,
        }

        response = self.client.post(
            f'/api/v1/gados',
            data,
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('document', response.data)
        self.assertTrue(str(response.data['document']).startswith('fusion_documents/'))

