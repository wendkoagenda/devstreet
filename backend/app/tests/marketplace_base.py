"""
Mixins de tests CRUD communs aux modèles de la marketplace.

Les mixins ne sont pas des TestCase : chaque fichier test_<modele>.py les combine avec TestCase / APITestCase.
Chaque modèle fournit : model, service_class, resource_plural, make(by) (instance valide, objets liés inclus),
payload(by) (corps de création API/service avec les clés étrangères en « <champ>_id ») et patch (mise à jour partielle).
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


def get_admin():
    User = get_user_model()
    try:
        return User.objects.get(email="admin@example.com")
    except User.DoesNotExist:
        return User.objects.create_superuser(username="admin", email="admin@example.com", password="admin123")


class ModelCrudMixin:
    model = None
    service_class = None
    resource_plural = None
    patch = {}

    @staticmethod
    def make(by):
        raise NotImplementedError

    @staticmethod
    def payload(by):
        raise NotImplementedError


class ModelTestsMixin(ModelCrudMixin):
    def setUp(self):
        self.user = get_admin()
        self.instance = self.make(self.user)

    def test_creation(self):
        self.assertIsNotNone(self.instance.id)
        self.assertTrue(self.model.objects.filter(id=self.instance.id).exists())

    def test_str_representation(self):
        self.assertIsInstance(str(self.instance), str)


class ServiceTestsMixin(ModelCrudMixin):
    def setUp(self):
        self.user = get_admin()
        self.service = self.service_class()

    def test_get_all(self):
        self.make(self.user)
        self.make(self.user)
        self.assertGreaterEqual(self.service.get_all().count(), 2)

    def test_create(self):
        before = self.model.objects.count()
        created = self.service.create({**self.payload(self.user), "created_by": self.user.id, "updated_by": self.user.id})
        self.assertEqual(self.model.objects.count(), before + 1)
        self.assertIsNotNone(created.id)

    def test_update(self):
        instance = self.make(self.user)
        updated = self.service.update(instance.id, dict(self.patch))
        for field, value in self.patch.items():
            self.assertEqual(getattr(updated, field), value)

    def test_delete(self):
        instance = self.make(self.user)
        self.assertTrue(self.service.delete(instance.id))
        self.assertFalse(self.model.objects.filter(id=instance.id).exists())


class ApiTestsMixin(ModelCrudMixin):
    def setUp(self):
        self.user = get_admin()
        self.instance = self.make(self.user)
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

    @property
    def base_url(self):
        return f"/api/v1/{self.resource_plural}"

    def test_list(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["results"], list)

    def test_retrieve(self):
        response = self.client.get(f"{self.base_url}/{self.instance.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        response = self.client.post(self.base_url, self.payload(self.user), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_partial_update(self):
        response = self.client.patch(f"{self.base_url}/{self.instance.id}", dict(self.patch), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.instance.refresh_from_db()
        for field, value in self.patch.items():
            self.assertEqual(getattr(self.instance, field), value)

    def test_delete(self):
        response = self.client.delete(f"{self.base_url}/{self.instance.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.model.objects.filter(id=self.instance.id).exists())
