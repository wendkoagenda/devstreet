"""
Tests pour les fusion.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.metier.models import Fusion
from app.metier.services.fusion_service import FusionService


class FusionModelTests(TestCase):
    """
    Tests pour le modèle Fusion.
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

        self.fusion = Fusion.objects.create(
            titre="Test titre",
            statut="draft",
            description="Test description",
            prix=99.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_fusion_creation(self):
        """Test de création d'un fusion."""
        self.assertIsNotNone(self.fusion.id)

    def test_fusion_str_representation(self):
        """Test de la représentation string du fusion."""
        self.assertIsInstance(str(self.fusion), str)


class FusionServiceTests(TestCase):
    """
    Tests pour le service Fusion.
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

        self.fusion_service = FusionService()

    def test_get_all_fusion(self):
        """Test de récupération de tous les fusion."""
        Fusion.objects.create(
            titre="Test titre 1",
            statut="draft",
            description="Test description 1",
            prix=99.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        Fusion.objects.create(
            titre="Test titre 2",
            statut="draft",
            description="Test description 2",
            prix=199.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        fusion = self.fusion_service.get_all()
        self.assertEqual(fusion.count(), 2)

    def test_create_fusion(self):
        """Test de création d'un fusion."""
        data = {
            "titre": "Nouveau titre",
            "statut": "draft",
            "description": "Nouveau description",
            "prix": 299.99,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        fusion = self.fusion_service.create(data)
        self.assertEqual(getattr(fusion, 'titre'), "Nouveau titre")


    def test_update_fusion(self):
        """Test de mise à jour d'un fusion."""
        fusion = Fusion.objects.create(
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
        updated_fusion = self.fusion_service.update(fusion.id, updated_data)
        self.assertEqual(getattr(updated_fusion, 'titre'), "Mis à jour titre")


    def test_delete_fusion(self):
        """Test de suppression d'un fusion."""
        fusion = Fusion.objects.create(
            titre="À supprimer titre",
            statut="draft",
            description="À supprimer description",
            prix=499.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.fusion_service.delete(fusion.id)
        self.assertTrue(success)
        self.assertFalse(Fusion.objects.filter(id=fusion.id).exists())


class FusionAPITests(APITestCase):
    """
    Tests pour l'API Fusion.
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

        self.fusion = Fusion.objects.create(
            titre="Test API titre",
            statut="draft",
            description="Test API description",
            prix=599.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_fusion_list(self):
        """Test de listage des fusion."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/fusions')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_fusion_retrieve(self):
        """Test de récupération d'un fusion."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/fusions/{self.fusion.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fusion_create(self):
        """Test de création d'un fusion."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "titre": "Test titre via API",
            "statut": "draft",
            "description": "Description créée via API",
            "prix": "99.99",
        }

        response = self.client.post(f'/api/v1/fusions', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fusion_partial_update(self):
        """Test de mise à jour partielle d'un fusion."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "titre": "fusion mis à jour"
        }

        response = self.client.patch(f'/api/v1/fusions/{self.fusion.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fusion_delete(self):
        """Test de suppression d'un fusion."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/fusions/{self.fusion.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Fusion.objects.filter(id=self.fusion.id).exists())

    def test_fusion_file_upload_document(self):
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
            f'/api/v1/fusions',
            data,
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('document', response.data)
        self.assertTrue(str(response.data['document']).startswith('fusion_documents/'))

