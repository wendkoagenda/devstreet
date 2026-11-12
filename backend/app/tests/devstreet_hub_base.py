"""Jeu Aïcha / Moussa : comptes et IAM de la boilerplate uniquement."""

from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase
from app.core.models import Permission, Role
from app.devstreet_hub.models import Project, Repository, ContributionTask
from app.devstreet_hub.management.commands.init_devstreet_hub import ADMIN_CODES


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class DevStreetHubAPITestCase(APITestCase):
    def setUp(self):
        cache.clear()
        role = Role.objects.create(name="Développeur test")
        role.permissions.set(
            [Permission.objects.get_or_create(code=c)[0] for c in ADMIN_CODES]
        )
        User = get_user_model()
        self.aicha = User.objects.create_user(
            username="aicha", email="aicha@example.test", password="Strong-Password-42!"
        )
        self.moussa = User.objects.create_user(
            username="moussa",
            email="moussa@example.test",
            password="Strong-Password-42!",
        )
        self.outsider = User.objects.create_user(
            username="outsider",
            email="outsider@example.test",
            password="Strong-Password-42!",
        )
        for u in (self.aicha, self.moussa):
            u.roles.add(role)
        self.role = role
        self.login(self.aicha)
        self.forge_patch = patch(
            "app.devstreet_hub.services.workflow_service.GiteaClient"
        )
        self.forge = self.forge_patch.start().return_value
        self.addCleanup(self.forge_patch.stop)
        self.forge.provision_identity.return_value = (
            {"id": 101, "login": "devstreet-user-1"},
            "one-time-secret",
        )
        self.forge.provision_repository.return_value = {
            "id": 201,
            "default_branch": "main",
        }
        self.forge.head.return_value = "a" * 40
        self.forge.pull_request.return_value = {"number": 1}
        self.addCleanup(cache.clear)

    def login(self, actor):
        self.client.force_authenticate(actor)

    def project(self, *, status="published", owner=None):
        owner = owner or self.aicha
        project = Project.objects.create(
            owner=owner,
            title="Gestion de stock",
            slug=f"stock-{Project.objects.count()}",
            status=status,
            created_by=owner.pk,
            updated_by=owner.pk,
        )
        Repository.objects.create(
            project=project,
            name=f"project-{project.pk}",
            namespace="aicha",
            status="ready",
            gitea_repo_id=1000 + project.pk,
        )
        return project

    def task(self, project=None, *, status="open"):
        return ContributionTask.objects.create(
            project=project or self.project(),
            title="Exporter le stock",
            status=status,
            acceptance_criteria=["CSV valide"],
            created_by=self.aicha.pk,
            updated_by=self.aicha.pk,
        )

    def body(self, title="Stock", slug="stock"):
        return {"title": title, "slug": slug, "declared_license": "MIT"}
