"""OAuth2 public PKCE (GCM) → PAT Gitea via DevStreet."""

from unittest.mock import patch
import base64
import secrets

from django.test import override_settings

from app.devstreet_hub.models import ForgeIdentity, GitConnectedComputer, GitOAuthAuthorization
from app.devstreet_hub.services.git_auth_service import _sha256_b64url
from app.devstreet_hub.services.git_oauth_service import GCM_CLIENT_ID
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
class GitOAuthTests(DevStreetHubAPITestCase):
    def setUp(self):
        super().setUp()
        self.git_forge_patch = patch(
            "app.devstreet_hub.services.git_oauth_service.GiteaClient"
        )
        self.git_forge = self.git_forge_patch.start().return_value
        self.addCleanup(self.git_forge_patch.stop)
        self._next_token_id = 8001

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
        self.client.post("/api/v1/forge-access")
        self.identity = ForgeIdentity.objects.get(user=self.aicha)

    def _start(self, *, verifier=None, challenge=None):
        if verifier is None:
            verifier, challenge = _pkce()
        elif challenge is None:
            challenge = _sha256_b64url(verifier)
        response = self.client.get(
            "/api/v1/git-oauth/authorize",
            {
                "response_type": "code",
                "client_id": GCM_CLIENT_ID,
                "redirect_uri": "http://127.0.0.1:39201/",
                "state": "st-test",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "scope": "git",
            },
        )
        return response, verifier

    def test_client_config_exposes_git_commands_without_secrets(self):
        response = self.client.get("/api/v1/git-oauth/client-config")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["client_id"], GCM_CLIENT_ID)
        self.assertIn("git_config_commands", response.data)
        blob = str(response.data)
        self.assertNotIn("admin-never-leaked", blob)
        self.assertTrue(
            any("oauthAuthorizeEndpoint" in c for c in response.data["git_config_commands"])
        )

    def test_authorize_redirects_to_frontend_confirm(self):
        self.client.force_authenticate(user=None)
        response, _ = self._start()
        self.assertEqual(response.status_code, 302)
        self.assertIn("/hub/git-oauth/authorize?request=", response["Location"])
        self.assertEqual(GitOAuthAuthorization.objects.count(), 1)

    def test_approve_and_token_exchange_issues_pat_once(self):
        self.client.force_authenticate(user=None)
        start, verifier = self._start()
        request_id = start["Location"].split("request=")[-1]

        public = self.client.get(f"/api/v1/git-oauth/{request_id}")
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public.data["status"], "pending")

        self.login(self.aicha)
        approved = self.client.post(f"/api/v1/git-oauth/{request_id}/approve")
        self.assertEqual(approved.status_code, 200, approved.data)
        self.assertIn("code=", approved.data["redirect_uri"])
        self.assertIn("state=st-test", approved.data["redirect_uri"])
        code = approved.data["redirect_uri"].split("code=")[1].split("&")[0]

        self.client.force_authenticate(user=None)
        token = self.client.post(
            "/api/v1/git-oauth/token",
            {
                "grant_type": "authorization_code",
                "client_id": GCM_CLIENT_ID,
                "code": code,
                "redirect_uri": "http://127.0.0.1:39201/",
                "code_verifier": verifier,
            },
            format="json",
        )
        self.assertEqual(token.status_code, 200, token.data)
        self.assertIn("access_token", token.data)
        self.assertTrue(token.data["access_token"].startswith("gitea-pat-"))
        self.assertNotIn("admin-never-leaked", str(token.data))
        self.assertEqual(GitConnectedComputer.objects.filter(user=self.aicha).count(), 1)

        # Code à usage unique.
        again = self.client.post(
            "/api/v1/git-oauth/token",
            {
                "grant_type": "authorization_code",
                "client_id": GCM_CLIENT_ID,
                "code": code,
                "redirect_uri": "http://127.0.0.1:39201/",
                "code_verifier": verifier,
            },
            format="json",
        )
        self.assertEqual(again.status_code, 400)

    def test_pkce_mismatch_rejected(self):
        self.client.force_authenticate(user=None)
        start, verifier = self._start()
        request_id = start["Location"].split("request=")[-1]
        self.login(self.aicha)
        approved = self.client.post(f"/api/v1/git-oauth/{request_id}/approve")
        code = approved.data["redirect_uri"].split("code=")[1].split("&")[0]
        self.client.force_authenticate(user=None)
        bad = self.client.post(
            "/api/v1/git-oauth/token",
            {
                "grant_type": "authorization_code",
                "client_id": GCM_CLIENT_ID,
                "code": code,
                "redirect_uri": "http://127.0.0.1:39201/",
                "code_verifier": "x" * 43,
            },
            format="json",
        )
        self.assertEqual(bad.status_code, 400)
        self.assertEqual(GitConnectedComputer.objects.count(), 0)

    def test_deny_redirects_with_error(self):
        self.client.force_authenticate(user=None)
        start, _ = self._start()
        request_id = start["Location"].split("request=")[-1]
        self.login(self.aicha)
        denied = self.client.post(f"/api/v1/git-oauth/{request_id}/deny")
        self.assertEqual(denied.status_code, 200)
        self.assertIn("error=access_denied", denied.data["redirect_uri"])
