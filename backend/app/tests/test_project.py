from django.db import IntegrityError, transaction
from rest_framework_simplejwt.tokens import RefreshToken
from app.devstreet_hub.models import Project, Star, ProjectMember
from app.devstreet_hub.services.errors import ExternalUnavailable
from app.tests.devstreet_hub_base import DevStreetHubAPITestCase


class ProjectRoutesTests(DevStreetHubAPITestCase):
    def test_filters_remain_scoped_and_reject_invalid_ids(self):
        self.project()
        other = self.project(owner=self.moussa, status="draft")
        response = self.client.get("/api/v1/projects", {"owner": self.moussa.pk})
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(
            self.client.get("/api/v1/projects?owner=wrong").status_code, 400
        )
        task = self.task()
        self.assertEqual(
            self.client.get(
                "/api/v1/contribution-tasks", {"project_id": other.pk}
            ).data["count"],
            0,
        )
        self.assertEqual(
            self.client.get(
                "/api/v1/contribution-tasks", {"project_id": task.project_id}
            ).data["count"],
            1,
        )

    def test_create_uses_existing_user_and_does_not_create_an_iam_account(self):
        response = self.client.post("/api/v1/projects", self.body(), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        project = Project.objects.get(pk=response.data["id"])
        self.assertEqual(project.owner, self.aicha)
        self.assertEqual(project.status, "draft")
        self.assertEqual(project.repository.status, "ready")
        self.assertEqual(project.repository.name, project.slug)
        self.assertEqual(response.data["setup"]["identity"], "ok")
        self.assertEqual(response.data["setup"]["repository"], "ok")
        self.assertIn("forge_access", response.data)

    def test_create_allocates_slug_when_absent_and_handles_collision(self):
        Project.objects.create(
            owner=self.aicha,
            title="Stock",
            slug="stock",
            created_by=self.aicha.pk,
            updated_by=self.aicha.pk,
        )
        response = self.client.post(
            "/api/v1/projects",
            {"title": "Stock", "declared_license": "MIT"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["slug"], "stock-2")

    def test_create_ignores_forged_owner_and_published_status(self):
        response = self.client.post(
            "/api/v1/projects",
            {**self.body(), "owner": self.moussa.pk, "status": "published"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            (response.data["owner_id"], response.data["status"]),
            (self.aicha.pk, "draft"),
        )

    def test_iam_denies_unprivileged_authenticated_user(self):
        self.login(self.outsider)
        self.assertEqual(
            self.client.post(
                "/api/v1/projects", self.body(), format="json"
            ).status_code,
            403,
        )

    def test_anonymous_create_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(
            self.client.post(
                "/api/v1/projects", self.body(), format="json"
            ).status_code,
            401,
        )

    def test_bearer_token_uses_boilerplate_authentication(self):
        self.client.force_authenticate(None)
        token = str(RefreshToken.for_user(self.aicha).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.assertEqual(
            self.client.post(
                "/api/v1/projects", self.body(), format="json"
            ).status_code,
            201,
        )

    def test_public_catalogue_excludes_drafts_and_archives(self):
        public = self.project()
        self.project(status="draft")
        self.project(status="archived")
        self.client.force_authenticate(None)
        response = self.client.get("/api/v1/projects")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([x["id"] for x in response.data["results"]], [public.pk])

    def test_draft_inaccessible_by_id_and_repository_url(self):
        project = self.project(status="draft")
        self.login(self.moussa)
        for path in (
            f"/api/v1/projects/{project.pk}",
            f"/api/v1/projects/{project.pk}/repository",
        ):
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_owner_can_edit_but_other_developer_cannot(self):
        project = self.project()
        self.login(self.moussa)
        self.assertEqual(
            self.client.patch(
                f"/api/v1/projects/{project.pk}", {"title": "Vol"}, format="json"
            ).status_code,
            403,
        )
        self.login(self.aicha)
        self.assertEqual(
            self.client.patch(
                f"/api/v1/projects/{project.pk}", {"title": "Stock v2"}, format="json"
            ).status_code,
            200,
        )
        project.refresh_from_db()
        self.assertEqual(project.title, "Stock v2")

    def test_blank_title_duplicate_slug_and_copyleft_rejected(self):
        self.project()
        for data in (
            self.body(title=" "),
            self.body(slug="stock-0"),
            {**self.body(), "declared_license": "GPL-3.0"},
        ):
            self.assertEqual(
                self.client.post("/api/v1/projects", data, format="json").status_code,
                400,
            )

    def test_publish_requires_ready_repository(self):
        self.forge.provision_repository.side_effect = ExternalUnavailable()
        response = self.client.post("/api/v1/projects", self.body(), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["setup"]["repository"], "failed")
        self.assertEqual(
            self.client.post(
                f'/api/v1/projects/{response.data["id"]}/publish'
            ).status_code,
            409,
        )

    def test_publish_and_archive_synchronize_visibility(self):
        project = self.project(status="draft")
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{project.pk}/publish").status_code, 200
        )
        self.forge.set_public.assert_called_with(project.repository, True)
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{project.pk}/archive").status_code, 200
        )
        self.forge.set_public.assert_called_with(project.repository, False)
        self.assertEqual(
            self.client.patch(
                f"/api/v1/projects/{project.pk}", {"title": "Nouvelle"}, format="json"
            ).status_code,
            409,
        )

    def test_failed_publication_keeps_draft(self):
        project = self.project(status="draft")
        self.forge.set_public.side_effect = ExternalUnavailable()
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{project.pk}/publish").status_code, 503
        )
        project.refresh_from_db()
        self.assertEqual(project.status, "draft")

    def test_star_put_and_delete_are_idempotent(self):
        project = self.project()
        self.login(self.moussa)
        path = f"/api/v1/projects/{project.pk}/star"
        for _ in range(2):
            self.assertEqual(self.client.put(path).data["star_count"], 1)
        self.assertEqual(Star.objects.count(), 1)
        for _ in range(2):
            self.assertEqual(self.client.delete(path).data["star_count"], 0)

    def test_database_prevents_duplicate_star(self):
        project = self.project()
        Star.objects.create(project=project, user=self.aicha)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Star.objects.create(project=project, user=self.aicha)

    def test_member_owner_and_iam_checks(self):
        project = self.project()
        path = f"/api/v1/projects/{project.pk}/members"
        result = self.client.post(
            path, {"user_id": self.moussa.pk, "role": "maintainer"}, format="json"
        )
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(
            self.client.get(path).data["results"][0]["user_id"], self.moussa.pk
        )
        self.forge.add_collaborator.assert_called()
        add_args = self.forge.add_collaborator.call_args[0]
        self.assertEqual(add_args[0], project.repository)
        self.assertEqual(add_args[2], "write")
        self.login(self.moussa)
        self.assertEqual(
            self.client.patch(
                f"/api/v1/projects/{project.pk}", {"title": "Stock v2"}, format="json"
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{project.pk}/publish").status_code, 403
        )
        self.login(self.aicha)
        self.assertEqual(
            self.client.delete(path + f"/{self.moussa.pk}").status_code, 204
        )
        self.assertFalse(ProjectMember.objects.exists())
        self.forge.remove_collaborator.assert_called()

    def test_member_contributor_syncs_read_permission(self):
        project = self.project()
        result = self.client.post(
            f"/api/v1/projects/{project.pk}/members",
            {"user_id": self.moussa.pk, "role": "contributor"},
            format="json",
        )
        self.assertEqual(result.status_code, 200, result.data)
        add_args = self.forge.add_collaborator.call_args[0]
        self.assertEqual(add_args[2], "read")

    def test_owner_cannot_be_removed_as_member(self):
        project = self.project()
        self.assertEqual(
            self.client.delete(
                f"/api/v1/projects/{project.pk}/members/{self.aicha.pk}"
            ).status_code,
            409,
        )

    def test_iam_permission_revocation_is_effective_without_new_token(self):
        self.role.permissions.remove(self.role.permissions.get(code="projects.create"))
        self.assertEqual(
            self.client.post(
                "/api/v1/projects", self.body(), format="json"
            ).status_code,
            403,
        )

    def test_repository_provision_is_retryable_and_idempotent(self):
        self.forge.create_user.side_effect = ExternalUnavailable()
        created = self.client.post("/api/v1/projects", self.body(), format="json")
        self.assertEqual(created.status_code, 201, created.data)
        project_id = created.data["id"]
        self.assertEqual(created.data["setup"]["identity"], "failed")
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{project_id}/provision").status_code,
            409,
        )

        # Restaure la création d'identité pour la reprise.
        users = self._forge_users_by_login
        users_by_id = self._forge_users_by_id
        next_id = {"value": self._next_gitea_id}

        def create_user(*, login, email, provisioning_key, password=None):
            from app.devstreet_hub.services.forge_identity_tokens import (
                description_with_marker,
                has_correlation,
            )
            from app.devstreet_hub.services.errors import Conflict

            existing = users.get(login)
            if existing:
                if has_correlation(existing, provisioning_key):
                    return existing, ""
                raise Conflict("Compte Git déjà présent sans preuve.")
            password = password or "one-time-secret"
            user = {
                "id": next_id["value"],
                "login": login,
                "email": email,
                "description": description_with_marker(provisioning_key),
            }
            next_id["value"] += 1
            users[login] = user
            users_by_id[user["id"]] = user
            return user, password

        self.forge.create_user.side_effect = create_user
        first = self.client.post("/api/v1/forge-access")
        self.assertEqual(first.status_code, 200, first.data)
        self.assertIn("initial_password", first.data)
        self.assertNotIn(
            "initial_password", self.client.post("/api/v1/forge-access").data
        )
        self.forge.provision_repository.side_effect = ExternalUnavailable()
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{project_id}/provision").status_code,
            503,
        )

        def provision_repository(repository, identity):
            return {
                "id": 201,
                "default_branch": "main",
                "private": True,
                "owner": {"id": identity.gitea_user_id},
            }

        self.forge.provision_repository.side_effect = provision_repository
        setup = self.client.post(f"/api/v1/projects/{project_id}/setup")
        self.assertEqual(setup.status_code, 200, setup.data)
        self.assertEqual(setup.data["setup"]["repository"], "ok")
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{project_id}/provision").status_code,
            200,
        )

    def test_initialize_readme_writes_scaffold_once(self):
        created = self.client.post("/api/v1/projects", self.body(), format="json")
        project_id = created.data["id"]
        first = self.client.post(
            f"/api/v1/projects/{project_id}/initialize",
            {"mode": "readme"},
            format="json",
        )
        self.assertEqual(first.status_code, 200, first.data)
        self.assertTrue(first.data["initialized"])
        self.assertFalse(first.data["is_empty"])
        self.assertEqual(first.data["repository"]["current_sha"], "b" * 40)
        self.assertEqual(self.forge.initialize_scaffold.call_count, 1)
        second = self.client.post(
            f"/api/v1/projects/{project_id}/initialize",
            {"mode": "readme"},
            format="json",
        )
        self.assertEqual(second.status_code, 409)
        push = self.client.post(
            f"/api/v1/projects/{project_id}/initialize",
            {"mode": "push_existing"},
            format="json",
        )
        self.assertEqual(push.status_code, 200)
        self.assertFalse(push.data["initialized"])

    def test_consent_is_owner_only_and_revocable(self):
        project = self.project()
        url = f"/api/v1/projects/{project.pk}/ai-consent"
        self.login(self.moussa)
        self.assertEqual(
            self.client.post(url, {"enabled": True}, format="json").status_code, 403
        )
        self.login(self.aicha)
        self.assertIsNotNone(
            self.client.post(url, {"enabled": True}, format="json").data[
                "ai_consent_at"
            ]
        )
        self.assertIsNone(
            self.client.post(url, {"enabled": False}, format="json").data[
                "ai_consent_at"
            ]
        )

    def test_no_raw_crud_for_internal_objects(self):
        for route in ("snapshots", "forge-identities", "repositories", "stars"):
            self.assertEqual(
                self.client.post("/api/v1/" + route, {}, format="json").status_code, 404
            )
