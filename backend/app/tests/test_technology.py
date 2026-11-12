from app.projects.models import Technology
from app.tests.projects_base import ProjectsAPITestCase


class TechnologyRoutesTests(ProjectsAPITestCase):
    def test_catalogue_public_and_creation_protected_by_iam(self):
        created = self.client.post(
            "/api/v1/technologies", {"label": "Django", "slug": "django"}, format="json"
        )
        self.assertEqual(created.status_code, 201, created.data)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/v1/technologies").data["count"], 1)
        self.assertEqual(
            self.client.get(f'/api/v1/technologies/{created.data["id"]}').status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                "/api/v1/technologies",
                {"label": "Python", "slug": "python"},
                format="json",
            ).status_code,
            401,
        )

    def test_project_technologies_are_selected_from_catalogue(self):
        technology = Technology.objects.create(
            label="Django",
            slug="django",
            created_by=self.aicha.pk,
            updated_by=self.aicha.pk,
        )
        response = self.client.post(
            "/api/v1/projects",
            {**self.body(), "technologies": [technology.pk]},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["technologies"], [technology.pk])
        self.assertEqual(
            self.client.get("/api/v1/projects?technology=django").data["count"], 1
        )
        self.assertEqual(
            self.client.get("/api/v1/projects?technology=react").data["count"], 0
        )

    def test_invalid_technology_id_and_duplicate_slug_rejected(self):
        Technology.objects.create(
            label="Python",
            slug="python",
            created_by=self.aicha.pk,
            updated_by=self.aicha.pk,
        )
        self.assertEqual(
            self.client.post(
                "/api/v1/technologies",
                {"label": "Python", "slug": "python"},
                format="json",
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(
                "/api/v1/projects",
                {**self.body(), "technologies": [99999]},
                format="json",
            ).status_code,
            400,
        )
