"""Jeu Aïcha / Moussa : comptes et IAM de la boilerplate uniquement."""

from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase
from app.core.models import Permission, Role
from app.devstreet_hub.models import Project, Repository, ContributionTask
from app.devstreet_hub.management.commands.init_devstreet_hub import ADMIN_CODES
from app.devstreet_hub.services.forge_identity_tokens import (
    description_with_marker,
    has_correlation,
)


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
        self._forge_users_by_login = {}
        self._forge_users_by_id = {}
        self._next_gitea_id = 101

        def get_user_by_login(login):
            return self._forge_users_by_login.get(login)

        def get_user_by_id(gitea_user_id):
            return self._forge_users_by_id.get(int(gitea_user_id))

        def create_user(*, login, email, provisioning_key, password=None):
            existing = self._forge_users_by_login.get(login)
            if existing:
                if has_correlation(existing, provisioning_key):
                    return existing, ""
                from app.devstreet_hub.services.errors import Conflict

                raise Conflict(
                    "Compte Git déjà présent sans preuve de propriété DevStreet Hub : "
                    "rapprochement administratif requis."
                )
            password = password or "one-time-secret"
            user = {
                "id": self._next_gitea_id,
                "login": login,
                "email": email,
                "description": description_with_marker(provisioning_key),
            }
            self._next_gitea_id += 1
            self._forge_users_by_login[login] = user
            self._forge_users_by_id[user["id"]] = user
            return user, password

        def reissue_password(*, login, email):
            return "reissued-secret"

        def provision_identity(actor, *, login=None, provisioning_key=None):
            # Compatibilité ancienne signature des mocks.
            from app.devstreet_hub.services.forge_identity_tokens import (
                login_for_key,
                new_provisioning_key,
            )

            key = provisioning_key or new_provisioning_key()
            return create_user(
                login=login or login_for_key(key),
                email=actor.email,
                provisioning_key=key,
            )

        self.forge.get_user_by_login.side_effect = get_user_by_login
        self.forge.get_user_by_id.side_effect = get_user_by_id
        self.forge.create_user.side_effect = create_user
        self.forge.reissue_password.side_effect = reissue_password
        self.forge.provision_identity.side_effect = provision_identity
        def provision_repository(repository, identity):
            return {
                "id": 2000 + int(getattr(repository, "pk", 0) or 0),
                "default_branch": "main",
                "private": True,
                "owner": {"id": identity.gitea_user_id},
            }

        self.forge.provision_repository.side_effect = provision_repository
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
