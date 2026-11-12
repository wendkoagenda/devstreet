"""Provisionnement d'identités Gitea : idempotence, non-adoption, reprises."""

from concurrent.futures import ThreadPoolExecutor

from django.db import connection
from django.test import TransactionTestCase

from app.devstreet_hub.models import ForgeIdentity
from app.devstreet_hub.services.errors import Conflict, ExternalUnavailable
from app.devstreet_hub.services.forge_identity_tokens import (
    description_with_marker,
    has_correlation,
)
from app.tests.devstreet_hub_base import DevStreetHubAPITestCase


class ForgeIdentityProvisioningTests(DevStreetHubAPITestCase):
    def test_new_user_creates_and_links_opaque_identity(self):
        response = self.client.post("/api/v1/forge-access")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(response.data["created"])
        self.assertIn("initial_password", response.data)
        identity = ForgeIdentity.objects.get(user=self.aicha)
        self.assertEqual(identity.status, ForgeIdentity.STATUS_LINKED)
        self.assertIsNotNone(identity.gitea_user_id)
        self.assertTrue(identity.login.startswith("ds-"))
        self.assertNotEqual(identity.login, f"devstreet-user-{self.aicha.pk}")
        self.assertNotIn("one-time-secret", str(identity.__dict__))

    def test_linked_user_is_reused_without_new_account(self):
        first = self.client.post("/api/v1/forge-access")
        self.assertEqual(first.status_code, 200)
        create_calls = self.forge.create_user.call_count
        second = self.client.post("/api/v1/forge-access")
        self.assertEqual(second.status_code, 200, second.data)
        self.assertFalse(second.data["created"])
        self.assertNotIn("initial_password", second.data)
        self.assertEqual(self.forge.create_user.call_count, create_calls)
        self.assertEqual(ForgeIdentity.objects.filter(user=self.aicha).count(), 1)

    def test_legacy_login_owned_by_third_party_is_not_adopted(self):
        """Un ancien `devstreet-user-{id}` tiers ne doit ni être adopté ni modifié."""
        legacy_login = f"devstreet-user-{self.aicha.pk}"
        self._forge_users_by_login[legacy_login] = {
            "id": 999,
            "login": legacy_login,
            "email": "aicha@example.test",
            "description": "Compte d'Aïcha",
        }
        response = self.client.post("/api/v1/forge-access")
        self.assertEqual(response.status_code, 200, response.data)
        identity = ForgeIdentity.objects.get(user=self.aicha)
        self.assertNotEqual(identity.login, legacy_login)
        self.assertNotEqual(identity.gitea_user_id, 999)
        # Le compte tiers reste intact dans le mock.
        self.assertEqual(self._forge_users_by_login[legacy_login]["id"], 999)

    def test_django_failure_after_remote_create_is_recoverable(self):
        reserved = {"done": False}
        real_create = self.forge.create_user.side_effect

        def create_then_fail(*, login, email, provisioning_key, password=None):
            user, secret = real_create(
                login=login,
                email=email,
                provisioning_key=provisioning_key,
                password=password,
            )
            if not reserved["done"]:
                reserved["done"] = True
                # Simule l'échec de persistance Django après succès distant.
                raise ExternalUnavailable("timeout après création")
            return user, secret

        self.forge.create_user.side_effect = create_then_fail
        first = self.client.post("/api/v1/forge-access")
        self.assertEqual(first.status_code, 503)
        pending = ForgeIdentity.objects.get(user=self.aicha)
        self.assertEqual(pending.status, ForgeIdentity.STATUS_PENDING)
        self.assertIsNone(pending.gitea_user_id)

        # Le compte distant existe déjà avec notre marqueur.
        remote = self._forge_users_by_login[pending.login]
        self.assertTrue(has_correlation(remote, pending.provisioning_key))

        self.forge.create_user.side_effect = real_create
        second = self.client.post("/api/v1/forge-access")
        self.assertEqual(second.status_code, 200, second.data)
        self.assertTrue(second.data.get("password_recovery_required"))
        self.assertIn("initial_password", second.data)
        pending.refresh_from_db()
        self.assertEqual(pending.status, ForgeIdentity.STATUS_LINKED)
        self.assertEqual(pending.gitea_user_id, remote["id"])

    def test_ambiguous_timeout_does_not_create_duplicate(self):
        real_create = self.forge.create_user.side_effect
        calls = {"n": 0}

        def flaky(*, login, email, provisioning_key, password=None):
            calls["n"] += 1
            if calls["n"] == 1:
                # Timeout avant de savoir si Gitea a créé : on crée quand même
                # côté mock pour simuler un succès distant non confirmé.
                user, _secret = real_create(
                    login=login,
                    email=email,
                    provisioning_key=provisioning_key,
                    password=password,
                )
                raise ExternalUnavailable("timeout ambigu") from None
            return real_create(
                login=login,
                email=email,
                provisioning_key=provisioning_key,
                password=password,
            )

        self.forge.create_user.side_effect = flaky
        self.assertEqual(self.client.post("/api/v1/forge-access").status_code, 503)
        retry = self.client.post("/api/v1/forge-access")
        self.assertEqual(retry.status_code, 200, retry.data)
        self.assertEqual(ForgeIdentity.objects.filter(user=self.aicha).count(), 1)
        logins = [
            u["login"]
            for u in self._forge_users_by_login.values()
            if u["email"] == self.aicha.email
        ]
        self.assertEqual(len(logins), 1)

    def test_foreign_login_collision_marks_conflict(self):
        import uuid

        identity = ForgeIdentity.objects.create(
            user=self.aicha,
            login="ds-testinst-aaaaaaaaaaaa",
            provisioning_key=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            status=ForgeIdentity.STATUS_PENDING,
        )
        self._forge_users_by_login[identity.login] = {
            "id": 777,
            "login": identity.login,
            "email": "other@example.test",
            "description": "pas notre marqueur",
        }
        response = self.client.post("/api/v1/forge-access")
        self.assertEqual(response.status_code, 409, response.data)
        identity.refresh_from_db()
        self.assertEqual(identity.status, ForgeIdentity.STATUS_CONFLICT)
        self.assertIsNone(identity.gitea_user_id)

    def test_deleted_remote_account_does_not_reattach_to_third_party(self):
        self.assertEqual(self.client.post("/api/v1/forge-access").status_code, 200)
        identity = ForgeIdentity.objects.get(user=self.aicha)
        previous_id = identity.gitea_user_id
        # Compte distant disparu ; un tiers réutilise le login.
        self._forge_users_by_id.clear()
        self._forge_users_by_login.clear()
        self._forge_users_by_login[identity.login] = {
            "id": 888,
            "login": identity.login,
            "email": "thief@example.test",
            "description": "compte tiers",
        }
        response = self.client.post("/api/v1/forge-access")
        self.assertEqual(response.status_code, 409, response.data)
        identity.refresh_from_db()
        self.assertEqual(identity.status, ForgeIdentity.STATUS_CONFLICT)
        # On ne remplace pas l'ID local par celui du tiers.
        self.assertEqual(identity.gitea_user_id, previous_id)
        self.assertNotEqual(identity.gitea_user_id, 888)

    def test_same_identity_for_multiple_projects(self):
        self.assertEqual(self.client.post("/api/v1/forge-access").status_code, 200)
        p1 = self.client.post(
            "/api/v1/projects", self.body(title="P1", slug="p1"), format="json"
        ).data["id"]
        p2 = self.client.post(
            "/api/v1/projects", self.body(title="P2", slug="p2"), format="json"
        ).data["id"]
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{p1}/provision").status_code, 200
        )
        self.assertEqual(
            self.client.post(f"/api/v1/projects/{p2}/provision").status_code, 200
        )
        self.assertEqual(ForgeIdentity.objects.filter(user=self.aicha).count(), 1)
        self.assertEqual(self.forge.create_user.call_count, 1)

    def test_secrets_are_not_persisted_on_identity(self):
        response = self.client.post("/api/v1/forge-access")
        secret = response.data["initial_password"]
        identity = ForgeIdentity.objects.get(user=self.aicha)
        blob = str(identity.__dict__) + str(
            list(ForgeIdentity.objects.values().filter(pk=identity.pk))
        )
        self.assertNotIn(secret, blob)


class ForgeIdentityConcurrencyTests(TransactionTestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from app.core.models import Permission, Role
        from app.devstreet_hub.management.commands.init_devstreet_hub import ADMIN_CODES
        from unittest.mock import MagicMock
        import threading

        role = Role.objects.create(name="Développeur concurrent")
        role.permissions.set(
            [Permission.objects.get_or_create(code=c)[0] for c in ADMIN_CODES]
        )
        User = get_user_model()
        self.user = User.objects.create_user(
            username="concurrent",
            email="concurrent@example.test",
            password="Strong-Password-42!",
        )
        self.user.roles.add(role)
        self._store_lock = threading.Lock()
        self._store = {"users": {}, "by_id": {}, "next_id": 501}
        self.forge = MagicMock()

        def get_user_by_login(login):
            with self._store_lock:
                return self._store["users"].get(login)

        def get_user_by_id(gitea_user_id):
            with self._store_lock:
                return self._store["by_id"].get(int(gitea_user_id))

        def create_user(*, login, email, provisioning_key, password=None):
            with self._store_lock:
                existing = self._store["users"].get(login)
                if existing and has_correlation(existing, provisioning_key):
                    return existing, ""
                if existing:
                    raise Conflict("pris")
                user = {
                    "id": self._store["next_id"],
                    "login": login,
                    "email": email,
                    "description": description_with_marker(provisioning_key),
                }
                self._store["next_id"] += 1
                self._store["users"][login] = user
                self._store["by_id"][user["id"]] = user
                return user, "secret"

        self.forge.get_user_by_login.side_effect = get_user_by_login
        self.forge.get_user_by_id.side_effect = get_user_by_id
        self.forge.create_user.side_effect = create_user
        self.forge.reissue_password.return_value = "reissued"

    def test_concurrent_requests_create_single_identity(self):
        from app.devstreet_hub.services.workflow_service import WorkflowService

        service = WorkflowService(forge=self.forge)
        errors = []

        def worker():
            try:
                return service.provision_identity(self.user)
            except Exception as exc:  # noqa: BLE001 — collecter pour l'assertion
                errors.append(exc)
                return None

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: worker(), range(2)))
        connection.close()

        self.assertEqual(errors, [], errors)
        self.assertEqual(len([r for r in results if r is not None]), 2)
        self.assertEqual(ForgeIdentity.objects.filter(user=self.user).count(), 1)
        self.assertEqual(len(self._store["users"]), 1)
