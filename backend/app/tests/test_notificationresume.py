"""
Tests pour les notification_resume.
"""
from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from app.communaute.models import NotificationResume, Publication, SuiviUtilisateur
from app.communaute.services.notificationresume_service import (
    NotificationResumeService,
)

User = get_user_model()


def _admin_user():
    try:
        return User.objects.get(email='admin@example.com')
    except User.DoesNotExist:
        return User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
        )


def _resume_kwargs(user, *, day=None, count=3, index=0):
    jour = day or (date.today() - timedelta(days=1 + index))
    return {
        'destinataire': user,
        'periode_debut': jour,
        'periode_fin': jour,
        'nombre_nouveautes': count,
        'created_by': user.id,
        'updated_by': user.id,
    }


class NotificationResumeModelTests(TestCase):
    def setUp(self):
        self.user = _admin_user()
        self.notification_resume = NotificationResume.objects.create(
            **_resume_kwargs(self.user, count=100)
        )

    def test_notification_resume_creation(self):
        self.assertIsNotNone(self.notification_resume.id)

    def test_notification_resume_str_representation(self):
        self.assertIn(str(self.user.id), str(self.notification_resume))


class NotificationResumeServiceTests(TestCase):
    def setUp(self):
        self.user = _admin_user()
        self.service = NotificationResumeService()

    def test_get_all_notification_resume(self):
        NotificationResume.objects.create(**_resume_kwargs(self.user, index=0))
        NotificationResume.objects.create(**_resume_kwargs(self.user, index=1))
        self.assertEqual(self.service.get_all().count(), 2)

    def test_create_notification_resume(self):
        data = _resume_kwargs(self.user, count=300, index=2)
        data['destinataire'] = self.user
        resume = self.service.create(data)
        self.assertEqual(resume.nombre_nouveautes, 300)

    def test_update_notification_resume(self):
        resume = NotificationResume.objects.create(
            **_resume_kwargs(self.user, count=400, index=3)
        )
        updated = self.service.update(
            resume.id, {'nombre_nouveautes': 401}, partial=True
        )
        self.assertEqual(updated.nombre_nouveautes, 401)

    def test_delete_notification_resume(self):
        resume = NotificationResume.objects.create(
            **_resume_kwargs(self.user, count=500, index=4)
        )
        self.assertTrue(self.service.delete(resume.id))
        self.assertFalse(
            NotificationResume.objects.filter(id=resume.id).exists()
        )

    def test_ensure_for_day_counts_abonnements_once(self):
        followed = User.objects.create_user(
            username='suivi_resume',
            email='suivi_resume@example.com',
            password='pass1234',
        )
        SuiviUtilisateur.objects.create(
            suiveur=self.user,
            suivi=followed,
            created_by=self.user.id,
            updated_by=self.user.id,
        )
        jour = self.service.covered_day()
        pub = Publication.objects.create(
            auteur=followed,
            type='DISCUSSION',
            titre='Nouveauté suivi',
            description='Contenu',
            created_by=followed.id,
            updated_by=followed.id,
        )
        Publication.objects.filter(pk=pub.pk).update(
            created_at=timezone.make_aware(
                datetime.combine(jour, time(12, 0))
            )
        )

        resume = self.service.ensure_for_day(membre=self.user, jour=jour)
        self.assertIsNotNone(resume)
        self.assertEqual(resume.nombre_nouveautes, 1)

        again = self.service.ensure_for_day(membre=self.user, jour=jour)
        self.assertEqual(again.id, resume.id)
        self.assertEqual(
            NotificationResume.objects.filter(
                destinataire=self.user, periode_debut=jour
            ).count(),
            1,
        )

    def test_mark_read_persists(self):
        resume = NotificationResume.objects.create(
            **_resume_kwargs(self.user, count=2, index=5)
        )
        marked = self.service.mark_read(
            resume_id=resume.id, membre=self.user
        )
        self.assertIsNotNone(marked.read_at)
        self.assertIsNone(self.service.get_actuel_non_lu(membre=self.user))


class NotificationResumeAPITests(APITestCase):
    def setUp(self):
        self.user = _admin_user()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.notification_resume = NotificationResume.objects.create(
            **_resume_kwargs(self.user, count=600, index=0)
        )

    def test_notification_resume_list(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        response = self.client.get('/api/v1/notifications-resume')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_notification_resume_retrieve(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        response = self.client.get(
            f'/api/v1/notifications-resume/{self.notification_resume.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_resume_create(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        jour = date.today() - timedelta(days=10)
        data = {
            'destinataire': self.user.id,
            'periode_debut': jour.isoformat(),
            'periode_fin': jour.isoformat(),
            'nombre_nouveautes': 100,
        }
        response = self.client.post(
            '/api/v1/notifications-resume', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_notification_resume_partial_update(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        response = self.client.patch(
            f'/api/v1/notifications-resume/{self.notification_resume.id}',
            {'nombre_nouveautes': 601},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_resume_delete(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        response = self.client.delete(
            f'/api/v1/notifications-resume/{self.notification_resume.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_actuel_and_lire(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        followed = User.objects.create_user(
            username='suivi_api_resume',
            email='suivi_api_resume@example.com',
            password='pass1234',
        )
        SuiviUtilisateur.objects.create(
            suiveur=self.user,
            suivi=followed,
            created_by=self.user.id,
            updated_by=self.user.id,
        )
        service = NotificationResumeService()
        jour = service.covered_day()
        pub = Publication.objects.create(
            auteur=followed,
            type='DISCUSSION',
            titre='Pub résumé API',
            description='Contenu',
            created_by=followed.id,
            updated_by=followed.id,
        )
        Publication.objects.filter(pk=pub.pk).update(
            created_at=timezone.make_aware(datetime.combine(jour, time(12, 0)))
        )
        NotificationResume.objects.all().delete()

        actuel = self.client.get('/api/v1/notifications-resume/actuel')
        self.assertEqual(actuel.status_code, status.HTTP_200_OK)
        self.assertEqual(actuel.data['nombre_nouveautes'], 1)

        lire = self.client.post(
            f'/api/v1/notifications-resume/{actuel.data["id"]}/lire'
        )
        self.assertEqual(lire.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(lire.data['read_at'])

        again = self.client.get('/api/v1/notifications-resume/actuel')
        self.assertEqual(again.status_code, status.HTTP_204_NO_CONTENT)
