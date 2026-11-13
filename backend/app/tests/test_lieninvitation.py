"""
Tests pour les lien_invitation.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from app.communaute.models import LienInvitation
from app.communaute.services.lieninvitation_service import LienInvitationService


class LienInvitationModelTests(TestCase):
    """
    Tests pour le modèle LienInvitation.
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

        self.lien_invitation = LienInvitation.objects.create(
            code_hash="Test code_hash",
            previsualisation_autorisee=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_lien_invitation_creation(self):
        """Test de création d'un lien_invitation."""
        self.assertIsNotNone(self.lien_invitation.id)

    def test_lien_invitation_str_representation(self):
        """Test de la représentation string du lien_invitation."""
        self.assertIsInstance(str(self.lien_invitation), str)


class LienInvitationServiceTests(TestCase):
    """
    Tests pour le service LienInvitation.
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

        self.lieninvitation_service = LienInvitationService()

    def test_get_all_lien_invitation(self):
        """Test de récupération de tous les lien_invitation."""
        LienInvitation.objects.create(
            code_hash="Test code_hash 1",
            previsualisation_autorisee=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )
        LienInvitation.objects.create(
            code_hash="Test code_hash 2",
            previsualisation_autorisee=False,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        lien_invitation = self.lieninvitation_service.get_all()
        self.assertEqual(lien_invitation.count(), 2)

    def test_create_lien_invitation(self):
        """Test de création d'un lien_invitation."""
        data = {
            "code_hash": "Nouveau code_hash",
            "previsualisation_autorisee": True,
            "created_by": self.user.id,
            "updated_by": self.user.id,
        }

        lien_invitation = self.lieninvitation_service.create(data)
        self.assertEqual(getattr(lien_invitation, 'code_hash'), "Nouveau code_hash")


    def test_update_lien_invitation(self):
        """Test de mise à jour d'un lien_invitation."""
        lien_invitation = LienInvitation.objects.create(
            code_hash="Original code_hash",
            previsualisation_autorisee=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        updated_data = {
            "code_hash": "Mis à jour code_hash"
        }
        updated_lien_invitation = self.lieninvitation_service.update(lien_invitation.id, updated_data)
        self.assertEqual(getattr(updated_lien_invitation, 'code_hash'), "Mis à jour code_hash")


    def test_delete_lien_invitation(self):
        """Test de suppression d'un lien_invitation."""
        lien_invitation = LienInvitation.objects.create(
            code_hash="À supprimer code_hash",
            previsualisation_autorisee=False,
            created_by=self.user.id,
            updated_by=self.user.id
        )

        success = self.lieninvitation_service.delete(lien_invitation.id)
        self.assertTrue(success)
        self.assertFalse(LienInvitation.objects.filter(id=lien_invitation.id).exists())


class LienInvitationAPITests(APITestCase):
    """
    Tests pour l'API LienInvitation.
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

        self.lien_invitation = LienInvitation.objects.create(
            code_hash="Test API code_hash",
            previsualisation_autorisee=True,
            created_by=self.user.id,
            updated_by=self.user.id
        )

    def test_lien_invitation_list(self):
        """Test de listage des lien_invitation."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/liens-invitation')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_lien_invitation_retrieve(self):
        """Test de récupération d'un lien_invitation."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(f'/api/v1/liens-invitation/{self.lien_invitation.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lien_invitation_create(self):
        """Test de création d'un lien_invitation."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "code_hash": "Test code_hash via API",
            "previsualisation_autorisee": True,
        }

        response = self.client.post(f'/api/v1/liens-invitation', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lien_invitation_partial_update(self):
        """Test de mise à jour partielle d'un lien_invitation."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            "code_hash": "lien_invitation mis à jour"
        }

        response = self.client.patch(f'/api/v1/liens-invitation/{self.lien_invitation.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lien_invitation_delete(self):
        """Test de suppression d'un lien_invitation."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(f'/api/v1/liens-invitation/{self.lien_invitation.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LienInvitation.objects.filter(id=self.lien_invitation.id).exists())

