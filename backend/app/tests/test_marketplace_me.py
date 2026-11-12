"""« Mon espace marketplace » : profil et entreprise de l'utilisateur connecté, sans permission RBAC."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from app.marketplace.models import Company, Profil

PROFIL = {"headline": "Dev web junior, Django et React", "country": "bf", "city": "Ouagadougou", "bio": "Premier stage."}
COMPANY = {"name": "Resto Express", "sector": "other", "country": "TG", "city": "Lomé"}


def make_user(email="awa@example.com", first_name="Awa", last_name="Kone"):
    return get_user_model().objects.create_user(
        username=email, email=email, password="pass12345", first_name=first_name, last_name=last_name
    )


class MeBase(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.login(self.user)

    def login(self, user):
        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)


class MeApiTests(MeBase):
    def test_anonymous_is_refused(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/v1/marketplace/me").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_space_is_empty_before_profil(self):
        response = self.client.get("/api/v1/marketplace/me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"profil": None, "company": None})

    def test_user_without_rbac_permission_creates_profil(self):
        self.assertFalse(self.user.has_permission("profils.create"))
        response = self.client.post("/api/v1/marketplace/me/profil", PROFIL, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        profil = Profil.objects.get(user=self.user)
        self.assertEqual(profil.country, "BF")
        self.assertEqual(profil.slug, "awa-kone")
        self.assertEqual((profil.created_by, profil.updated_by), (self.user.id, self.user.id))
        self.assertEqual(response.data["profil"]["id"], profil.id)
        self.assertIsNone(response.data["company"])

    def test_slug_is_unique(self):
        other = make_user("awa2@example.com")
        self.login(other)
        self.client.post("/api/v1/marketplace/me/profil", PROFIL, format="json")
        self.login(self.user)
        self.client.post("/api/v1/marketplace/me/profil", PROFIL, format="json")
        self.assertEqual(
            sorted(Profil.objects.values_list("slug", flat=True)), ["awa-kone", "awa-kone-2"]
        )

    def test_second_profil_is_refused(self):
        self.client.post("/api/v1/marketplace/me/profil", PROFIL, format="json")
        response = self.client.post("/api/v1/marketplace/me/profil", PROFIL, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Profil.objects.filter(user=self.user).count(), 1)

    def test_invalid_country_is_refused(self):
        response = self.client.post("/api/v1/marketplace/me/profil", {**PROFIL, "country": "Burkina"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_set_protected_fields(self):
        """Compte, slug et entreprise ne se choisissent pas depuis le corps de la requête."""
        other = make_user("autre@example.com")
        body = {**PROFIL, "user": other.id, "slug": "pirate", "is_company_owner": True}
        self.client.post("/api/v1/marketplace/me/profil", body, format="json")
        profil = Profil.objects.get(user=self.user)
        self.assertEqual(profil.slug, "awa-kone")
        self.assertFalse(profil.is_company_owner)
        self.assertFalse(Profil.objects.filter(user=other).exists())

    def test_patch_profil(self):
        self.client.post("/api/v1/marketplace/me/profil", PROFIL, format="json")
        response = self.client.patch("/api/v1/marketplace/me/profil", {"headline": "Dev senior"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(Profil.objects.get(user=self.user).headline, "Dev senior")

    def test_patch_without_profil_is_404(self):
        response = self.client.patch("/api/v1/marketplace/me/profil", {"headline": "x"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_only_sees_own_space(self):
        self.client.post("/api/v1/marketplace/me/profil", PROFIL, format="json")
        self.login(make_user("autre@example.com"))
        self.assertIsNone(self.client.get("/api/v1/marketplace/me").data["profil"])


class MeCompanyTests(MeBase):
    def setUp(self):
        super().setUp()
        self.client.post("/api/v1/marketplace/me/profil", PROFIL, format="json")

    def test_company_requires_profil(self):
        self.login(make_user("sans-profil@example.com"))
        response = self.client.post("/api/v1/marketplace/me/company", COMPANY, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_company_attaches_owner_profil(self):
        response = self.client.post("/api/v1/marketplace/me/company", COMPANY, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        profil = Profil.objects.get(user=self.user)
        self.assertEqual(profil.company.name, "Resto Express")
        self.assertTrue(profil.is_company_owner)
        self.assertEqual(profil.company.slug, "resto-express")
        self.assertFalse(profil.company.is_verified)
        self.assertEqual(response.data["company"]["name"], "Resto Express")

    def test_second_company_is_refused(self):
        self.client.post("/api/v1/marketplace/me/company", COMPANY, format="json")
        response = self.client.post("/api/v1/marketplace/me/company", COMPANY, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Company.objects.count(), 1)

    def test_cannot_verify_own_company(self):
        self.client.post("/api/v1/marketplace/me/company", {**COMPANY, "is_verified": True}, format="json")
        self.assertFalse(Company.objects.get().is_verified)

    def test_owner_updates_company(self):
        self.client.post("/api/v1/marketplace/me/company", COMPANY, format="json")
        response = self.client.patch("/api/v1/marketplace/me/company", {"city": "Kara"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(Company.objects.get().city, "Kara")

    def test_non_owner_cannot_update_company(self):
        self.client.post("/api/v1/marketplace/me/company", COMPANY, format="json")
        company = Company.objects.get()
        colleague = make_user("collegue@example.com")
        Profil.objects.create(
            user=colleague, slug="collegue", country="TG", company=company, created_by=colleague.id, updated_by=colleague.id
        )
        self.login(colleague)
        response = self.client.patch("/api/v1/marketplace/me/company", {"city": "Kara"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Company.objects.get().city, "Lomé")

    def test_patch_without_company_is_404(self):
        response = self.client.patch("/api/v1/marketplace/me/company", {"city": "Kara"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
