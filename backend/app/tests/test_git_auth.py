"""Autorisation navigateur DevStreet → PAT Gitea (device + PKCE)."""

from datetime import timedelta
from unittest.mock import patch
import base64
import secrets

from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from rest_framework.exceptions import Throttled

from app.devstreet_hub.models import ForgeIdentity, GitConnectedComputer, GitDeviceAuthRequest
from app.devstreet_hub.services.git_auth_service import GitAuthService, _sha256_b64url
from app.tests.devstreet_hub_base import DevStreetHubAPITestCase


def _pkce():
    verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii").rstrip("=")
    )
    challenge = _sha256_b64url(verifier)
    return verifier, challenge


@override_settings(
    FRONTEND_URL="http://localhost:5173",
    CORS_ALLOWED_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"],
    DEVSTREET_HUB_GITEA_URL="http://127.0.0.1:13000",
    DEVSTREET_HUB_GITEA_PUBLIC_URL="http://127.0.0.1:13000",
    DEVSTREET_HUB_GITEA_TOKEN="admin-never-leaked",
)
class GitDeviceAuthTests(DevStreetHubAPITestCase):
    def setUp(self):
        super().setUp()
        self.git_forge_patch = patch(
            "app.devstreet_hub.services.git_auth_service.GiteaClient"
        )
        self.git_forge = self.git_forge_patch.start().return_value
        self.addCleanup(self.git_forge_patch.stop)
        self._next_token_id = 5001

        def create_user_access_token(*, login, email, name, scopes=None):
            token = f"gitea-pat-{self._next_token_id}-secret"
            payload = {
                "id": self._next_token_id,
                "name": name,
                "sha1": token,
                "token_last_eight": token[-8:],
                "scopes": scopes or [],
            }
            self._next_token_id += 1
            return payload

        self.git_forge.create_user_access_token.side_effect = create_user_access_token
        self.git_forge.delete_user_access_token.return_value = None
        # Identité liée (comme après forge-access).
        self.client.post("/api/v1/forge-access")
        self.identity = ForgeIdentity.objects.get(user=self.aicha)

    def _start(self, *, computer="PC-Aicha", challenge=None):
        verifier, ch = _pkce()
        challenge = challenge or ch
        response = self.client.post(
            "/api/v1/git-auth/device/start",
            {
                "computer_name": computer,
                "hub_base_url": "http://localhost:5173",
                "code_challenge": challenge,
            },
            format="json",
        )
        return response, verifier

    def test_authorize_poll_success_and_single_use(self):
        self.client.force_authenticate(user=None)
        start, verifier = self._start()
        self.assertEqual(start.status_code, 201, start.data)
        request_id = start.data["request_id"]
        self.assertIn("/hub/git-auth/authorize?request=", start.data["authorize_url"])
        self.assertNotIn("admin-never-leaked", str(start.data))

        # Pas d'auto-approve : poll reste pending avant confirmation.
        poll_pending = self.client.post(
            f"/api/v1/git-auth/{request_id}/poll",
            {"code_verifier": verifier},
            format="json",
        )
        self.assertEqual(poll_pending.status_code, 200)
        self.assertEqual(poll_pending.data["status"], "pending")
        self.assertNotIn("token", poll_pending.data)

        self.login(self.aicha)
        auth = self.client.post(f"/api/v1/git-auth/{request_id}/authorize")
        self.assertEqual(auth.status_code, 200, auth.data)
        self.assertEqual(auth.data["status"], "authorized")

        # Respecte l'intervalle minimal de polling (CLI : sleep ≥ 2 s).
        req = GitDeviceAuthRequest.objects.get(pk=request_id)
        req.last_poll_at = timezone.now() - timedelta(seconds=3)
        req.save(update_fields=["last_poll_at"])

        self.client.force_authenticate(user=None)
        poll_ok = self.client.post(
            f"/api/v1/git-auth/{request_id}/poll",
            {"code_verifier": verifier},
            format="json",
        )
        self.assertEqual(poll_ok.status_code, 200, poll_ok.data)
        self.assertEqual(poll_ok.data["status"], "authorized")
        self.assertIn("token", poll_ok.data)
        self.assertTrue(poll_ok.data["token"].startswith("gitea-pat-"))
        self.assertEqual(poll_ok.data["login"], self.identity.login)
        self.assertNotIn("admin-never-leaked", str(poll_ok.data))

        # Rejeu : grant consommé.
        GitDeviceAuthRequest.objects.filter(pk=request_id).update(
            last_poll_at=timezone.now() - timedelta(seconds=3)
        )
        poll_replay = self.client.post(
            f"/api/v1/git-auth/{request_id}/poll",
            {"code_verifier": verifier},
            format="json",
        )
        self.assertEqual(poll_replay.status_code, 200)
        self.assertEqual(poll_replay.data["status"], "consumed")
        self.assertNotIn("token", poll_replay.data)

        computer = GitConnectedComputer.objects.get(user=self.aicha)
        self.assertEqual(computer.status, GitConnectedComputer.STATUS_ACTIVE)
        self.git_forge.create_user_access_token.assert_called_once()

    def test_deny_and_expired(self):
        self.client.force_authenticate(user=None)
        start, verifier = self._start(computer="PC-Deny")
        request_id = start.data["request_id"]

        self.login(self.aicha)
        denied = self.client.post(f"/api/v1/git-auth/{request_id}/deny")
        self.assertEqual(denied.status_code, 200)
        self.assertEqual(denied.data["status"], "denied")

        self.client.force_authenticate(user=None)
        poll = self.client.post(
            f"/api/v1/git-auth/{request_id}/poll",
            {"code_verifier": verifier},
            format="json",
        )
        self.assertEqual(poll.data["status"], "denied")
        self.assertNotIn("token", poll.data)

        # Expiration
        start2, verifier2 = self._start(computer="PC-Exp")
        req = GitDeviceAuthRequest.objects.get(pk=start2.data["request_id"])
        req.expires_at = timezone.now() - timedelta(seconds=1)
        req.save(update_fields=["expires_at"])
        poll_exp = self.client.post(
            f"/api/v1/git-auth/{req.id}/poll",
            {"code_verifier": verifier2},
            format="json",
        )
        self.assertEqual(poll_exp.data["status"], "expired")

    def test_pkce_swap_between_two_requests(self):
        self.client.force_authenticate(user=None)
        start_a, verifier_a = self._start(computer="PC-A")
        start_b, verifier_b = self._start(computer="PC-B")
        self.assertEqual(start_a.status_code, 201, start_a.data)
        self.assertEqual(start_b.status_code, 201, start_b.data)
        id_a = start_a.data["request_id"]
        id_b = start_b.data["request_id"]

        self.login(self.aicha)
        self.client.post(f"/api/v1/git-auth/{id_a}/authorize")
        self.client.post(f"/api/v1/git-auth/{id_b}/authorize")

        self.client.force_authenticate(user=None)
        # Échange de vérificateurs : refus.
        bad = self.client.post(
            f"/api/v1/git-auth/{id_a}/poll",
            {"code_verifier": verifier_b},
            format="json",
        )
        self.assertEqual(bad.status_code, 403)

        GitDeviceAuthRequest.objects.filter(pk=id_b).update(
            last_poll_at=timezone.now() - timedelta(seconds=3)
        )
        good = self.client.post(
            f"/api/v1/git-auth/{id_b}/poll",
            {"code_verifier": verifier_b},
            format="json",
        )
        self.assertEqual(good.status_code, 200)
        self.assertEqual(good.data["status"], "authorized")

    def test_unauthenticated_cannot_authorize(self):
        self.client.force_authenticate(user=None)
        start, _ = self._start()
        response = self.client.post(
            f"/api/v1/git-auth/{start.data['request_id']}/authorize"
        )
        self.assertIn(response.status_code, (401, 403))

    def test_two_computers_same_user(self):
        self.client.force_authenticate(user=None)
        start1, v1 = self._start(computer="Maison")
        start2, v2 = self._start(computer="Bureau")
        self.login(self.aicha)
        self.client.post(f"/api/v1/git-auth/{start1.data['request_id']}/authorize")
        self.client.post(f"/api/v1/git-auth/{start2.data['request_id']}/authorize")
        self.client.force_authenticate(user=None)
        self.client.post(
            f"/api/v1/git-auth/{start1.data['request_id']}/poll",
            {"code_verifier": v1},
            format="json",
        )
        self.client.post(
            f"/api/v1/git-auth/{start2.data['request_id']}/poll",
            {"code_verifier": v2},
            format="json",
        )
        self.login(self.aicha)
        listing = self.client.get("/api/v1/git-computers")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.data), 2)
        names = {c["name"] for c in listing.data}
        self.assertEqual(names, {"Maison", "Bureau"})

    def test_revoke_deletes_gitea_token_only(self):
        self.client.force_authenticate(user=None)
        start, verifier = self._start(computer="ToRevoke")
        self.login(self.aicha)
        self.client.post(f"/api/v1/git-auth/{start.data['request_id']}/authorize")
        self.client.force_authenticate(user=None)
        poll = self.client.post(
            f"/api/v1/git-auth/{start.data['request_id']}/poll",
            {"code_verifier": verifier},
            format="json",
        )
        computer_id = poll.data["computer_id"]
        self.login(self.aicha)
        other = GitConnectedComputer.objects.create(
            user=self.aicha,
            name="Autre",
            forge_login=self.identity.login,
            gitea_token_id=9999,
            token_last_eight="abcdefgh",
            status=GitConnectedComputer.STATUS_ACTIVE,
        )
        revoked = self.client.delete(f"/api/v1/git-computers/{computer_id}")
        self.assertEqual(revoked.status_code, 204)
        self.git_forge.delete_user_access_token.assert_called()
        other.refresh_from_db()
        self.assertEqual(other.status, GitConnectedComputer.STATUS_ACTIVE)
        target = GitConnectedComputer.objects.get(pk=computer_id)
        self.assertEqual(target.status, GitConnectedComputer.STATUS_REVOKED)

    def test_wrong_hub_rejected(self):
        self.client.force_authenticate(user=None)
        _, challenge = _pkce()
        response = self.client.post(
            "/api/v1/git-auth/device/start",
            {
                "computer_name": "X",
                "hub_base_url": "https://evil.example",
                "code_challenge": challenge,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_poll_throttle_interval(self):
        service = GitAuthService(forge=self.git_forge)
        verifier, challenge = _pkce()
        item = GitDeviceAuthRequest.objects.create(
            computer_name="Throttle",
            hub_base_url="http://localhost:5173",
            code_challenge=challenge,
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        first = service.poll(request_id=item.id, code_verifier=verifier)
        self.assertEqual(first["status"], "pending")
        with self.assertRaises(Throttled):
            service.poll(request_id=item.id, code_verifier=verifier)

    def test_retrieve_public_has_no_secret(self):
        self.client.force_authenticate(user=None)
        start, _ = self._start()
        detail = self.client.get(f"/api/v1/git-auth/{start.data['request_id']}")
        self.assertEqual(detail.status_code, 200)
        self.assertIn("scope_labels", detail.data)
        blob = str(detail.data)
        self.assertNotIn("admin-never-leaked", blob)
        self.assertNotIn("gitea-pat-", blob)


@override_settings(
    DEBUG=True,
    DEVSTREET_HUB_GITEA_URL="http://127.0.0.1:13000",
    DEVSTREET_HUB_GITEA_TOKEN="test-token",
)
class GiteaPatMustChangePasswordTests(SimpleTestCase):
    """Le flag must_change_password ne doit pas bloquer les PAT après création."""

    def test_create_user_access_token_clears_must_change_password(self):
        import httpx
        from unittest.mock import patch
        from app.devstreet_hub.services.gitea_client import GiteaClient

        calls = []

        def handler(request):
            calls.append(request)
            if request.method == "POST" and request.url.path.endswith("/tokens"):
                return httpx.Response(
                    201,
                    json={
                        "id": 42,
                        "name": "t",
                        "sha1": "a" * 40,
                        "token_last_eight": "a" * 8,
                    },
                )
            return httpx.Response(200, json={})

        original = httpx.Client
        with patch(
            "app.devstreet_hub.services.gitea_client.httpx.Client",
            side_effect=lambda **kwargs: original(
                transport=httpx.MockTransport(handler), **kwargs
            ),
        ), patch.object(
            GiteaClient,
            "reissue_password",
            side_effect=lambda **kw: calls.append(("reissue", kw)) or "temp-secret",
        ) as _:
            client = GiteaClient()
            payload = client.create_user_access_token(
                login="ds-demo",
                email="demo@example.test",
                name="pc",
            )
        self.assertEqual(payload["sha1"], "a" * 40)
        reissues = [c for c in calls if isinstance(c, tuple) and c[0] == "reissue"]
        self.assertGreaterEqual(len(reissues), 2)
        self.assertFalse(reissues[-1][1]["must_change_password"])
