"""
Tests pour les elitesty.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.metier.models import Elitesty
from app.metier.services.elitesty_service import ElitestyService


class ElitestyModelTests(TestCase):
    """
    Tests pour le modèle Elitesty.
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

        self.elitesty = Elitesty.objects.create(
            titre="Test titre",
            statut="draft",
            description="Test description",
            prix=99.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_elitesty_creation(self):
        """Test de création d'un elitesty."""
        self.assertIsNotNone(self.elitesty.id)

    def test_elitesty_str_representation(self):
        """Test de la représentation string du elitesty."""
        self.assertIsInstance(str(self.elitesty), str)


class ElitestyServiceTests(TestCase):
    """
    Tests pour le service Elitesty.
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

        self.elitesty_service = ElitestyService()

    def test_get_all_elitesty(self):
        """Test de récupération de tous les elitesty."""
        Elitesty.objects.create(
            titre="Test titre 1",
            statut="draft",
            description="Test description 1",
            prix=99.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        Elitesty.objects.create(
            titre="Test titre 2",
            statut="draft",
            description="Test description 2",
            prix=199.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        elitesty = self.elitesty_service.get_all()
        self.assertEqual(elitesty.count(), 2)

    def test_create_elitesty(self):
        """Test de création d'un elitesty."""
        data = {
            "titre": "Nouveau titre",
            "statut": "draft",
            "description": "Nouveau description",
            "prix": 299.99,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        elitesty = self.elitesty_service.create(data)
        self.assertEqual(getattr(elitesty, 'titre'), "Nouveau titre")


    def test_update_elitesty(self):
        """Test de mise à jour d'un elitesty."""
        elitesty = Elitesty.objects.create(
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
        updated_elitesty = self.elitesty_service.update(elitesty.id, updated_data)
        self.assertEqual(getattr(updated_elitesty, 'titre'), "Mis à jour titre")


    def test_delete_elitesty(self):
        """Test de suppression d'un elitesty."""
        elitesty = Elitesty.objects.create(
            titre="À supprimer titre",
            statut="draft",
            description="À supprimer description",
            prix=499.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.elitesty_service.delete(elitesty.id)
        self.assertTrue(success)
        self.assertFalse(Elitesty.objects.filter(id=elitesty.id).exists())


class ElitestyAPITests(APITestCase):
    """
    Tests pour l'API Elitesty.
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

        self.elitesty = Elitesty.objects.create(
            titre="Test API titre",
            statut="draft",
            description="Test API description",
            prix=599.99,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_elitesty_list(self):
        """Test de listage des elitesty."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/elitesties')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_elitesty_retrieve(self):
        """Test de récupération d'un elitesty."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/elitesties/{self.elitesty.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_elitesty_create(self):
        """Test de création d'un elitesty."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "titre": "Test titre via API",
            "statut": "draft",
            "description": "Description créée via API",
            "prix": "99.99",
        }

        response = self.client.post(f'/api/v1/elitesties', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_elitesty_partial_update(self):
        """Test de mise à jour partielle d'un elitesty."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "titre": "elitesty mis à jour"
        }

        response = self.client.patch(f'/api/v1/elitesties/{self.elitesty.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_elitesty_delete(self):
        """Test de suppression d'un elitesty."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/elitesties/{self.elitesty.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Elitesty.objects.filter(id=self.elitesty.id).exists())

    def test_elitesty_file_upload_document(self):
        """Test de création avec upload fichier (document)."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        uploaded = SimpleUploadedFile(
            "test-upload.pdf",
            b"%PDF-1.4 test content",
            content_type="application/pdf",
        )
        relative_path = "elitest_documents/test-upload.pdf"
        data = {
            "titre": "Test titre upload",
            "statut": "draft",
            "description": "Description upload",
            "prix": "99.99",
            "document": uploaded,
            "document_path": relative_path,
        }

        response = self.client.post(
            f'/api/v1/elitesties',
            data,
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('document', response.data)
        self.assertTrue(str(response.data['document']).startswith('elitest_documents/'))

