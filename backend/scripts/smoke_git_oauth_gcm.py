"""POC isolé : OAuth Hub → PAT → clone public + push git:PAT (config/coffre isolés).

N'utilise pas le helper %LOCALAPPDATA%\\DevStreet. N'envoie rien sur le dépôt DevStreet.
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings

from app.core.models import Permission, Role
from app.devstreet_hub.conf import config
from app.devstreet_hub.management.commands.init_devstreet_hub import ADMIN_CODES
from app.devstreet_hub.models import ForgeIdentity
from app.devstreet_hub.services.gitea_client import GiteaClient
from app.devstreet_hub.services.git_oauth_service import GCM_CLIENT_ID, GitOAuthService
from app.devstreet_hub.services.workflow_service import WorkflowService


ROOT = Path(__file__).resolve().parents[1]
WORKDIR = ROOT / ".local" / "git-oauth-gcm-poc"
REPO_NAME = "ds-oauth-gcm-poc"
ISOLATED_GITCONFIG = WORKDIR / "gitconfig"
ISOLATED_CREDS = WORKDIR / "gcm-store"


def _pkce() -> tuple[str, str]:
    verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii").rstrip("=")
    )
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .decode("ascii")
        .rstrip("=")
    )
    return verifier, challenge


def _git(cwd: Path, args: list[str], *, env: dict, check: bool = True):
    result = subprocess.run(
        ["git", *args], cwd=cwd, env=env, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} échoué: {(result.stderr or result.stdout)[:600]}"
        )
    return result


def _ensure_actor():
    User = get_user_model()
    email = "smoke-oauth-gcm@devstreet.local"
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": "smoke-oauth-gcm", "is_active": True},
    )
    if created or not user.has_usable_password():
        user.set_password("Smoke-Oauth-Gcm-42!")
        user.save()
    role, _ = Role.objects.get_or_create(name="DevStreet Hub Developer")
    for code in ADMIN_CODES:
        perm, _ = Permission.objects.get_or_create(code=code, defaults={"name": code})
        role.permissions.add(perm)
    user.roles.add(role)

    identity = ForgeIdentity.objects.filter(user=user).first()
    if (
        not identity
        or identity.status != ForgeIdentity.STATUS_LINKED
        or not identity.login
        or not identity.gitea_user_id
    ):
        if identity and identity.status == ForgeIdentity.STATUS_CONFLICT:
            identity.delete()
        WorkflowService().provision_identity(user)
        identity = ForgeIdentity.objects.get(user=user)
    return user, identity


def _ensure_public_repo(forge: GiteaClient, login: str, *, email: str) -> str:
    forge.ensure_user_public_visibility(login, email=email)
    existing = forge.request("GET", f"/repos/{login}/{REPO_NAME}", missing_ok=True)
    if existing is None:
        forge.request(
            "POST",
            f"/admin/users/{login}/repos",
            {
                "name": REPO_NAME,
                "private": False,
                "auto_init": True,
                "default_branch": "main",
                "description": "Dépôt jetable POC OAuth GCM",
            },
        )
    elif existing.get("private"):
        forge.request("PATCH", f"/repos/{login}/{REPO_NAME}", {"private": False})
    public = (config("GITEA_PUBLIC_URL") or config("GITEA_URL")).rstrip("/")
    return f"{public}/{login}/{REPO_NAME}.git"


def main() -> int:
    if not settings.DEBUG:
        raise SystemExit("POC réservé au développement local (DEBUG=True).")
    gitea_url = (config("GITEA_PUBLIC_URL") or config("GITEA_URL") or "").rstrip("/")
    if not gitea_url or not config("GITEA_TOKEN"):
        print("Gitea non configuré — POC annulé.")
        return 2

    if WORKDIR.exists():
        shutil.rmtree(WORKDIR, ignore_errors=True)
    WORKDIR.mkdir(parents=True)
    ISOLATED_CREDS.mkdir(parents=True)

    ISOLATED_GITCONFIG.write_text(
        "\n".join(
            [
                "[user]",
                "  name = DevStreet POC",
                "  email = poc@devstreet.local",
                f'[credential "{gitea_url}"]',
                "  provider = generic",
                f"  oauthClientId = {GCM_CLIENT_ID}",
                "  oauthUseClientAuthHeader = false",
                "  oauthDefaultUserName = git",
                "  oauthScopes = git",
                "  oauthRedirectUri = http://127.0.0.1",
                "[credential]",
                "  helper =",
                "  helper = manager",
                "",
            ]
        ),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = str(ISOLATED_GITCONFIG)
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_CREDENTIAL_STORE"] = "plaintext"
    env["GCM_PLAINTEXT_STORE_PATH"] = str(ISOLATED_CREDS)
    env["GCM_INTERACTIVE"] = "never"
    env["GCM_NAMESPACE"] = "devstreet-poc"

    owner, identity = _ensure_actor()
    forge = GiteaClient()
    clone = _ensure_public_repo(forge, identity.login, email=owner.email)
    print(f"acteur={owner.email} login={identity.login}")
    print(f"dépôt={clone}")

    # 1) Clone public sans credential
    anon = WORKDIR / "clone-anon"
    _git(WORKDIR, ["-c", "credential.helper=", "clone", clone, str(anon)], env=env)
    print("Clone public sans credential: OK")

    hub = settings.FRONTEND_URL.rstrip("/")
    with override_settings(FRONTEND_URL=hub):
        oauth = GitOAuthService(forge=forge)
        verifier, challenge = _pkce()
        started = oauth.start_authorize(
            {
                "response_type": "code",
                "client_id": GCM_CLIENT_ID,
                "redirect_uri": "http://127.0.0.1:39201/",
                "state": "poc",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "scope": "git",
            }
        )
        approved = oauth.approve(owner, started["request_id"])
        code = approved["redirect_uri"].split("code=")[1].split("&")[0]
        token_payload = oauth.exchange_token(
            {
                "grant_type": "authorization_code",
                "client_id": GCM_CLIENT_ID,
                "code": code,
                "redirect_uri": "http://127.0.0.1:39201/",
                "code_verifier": verifier,
            }
        )
        pat = token_payload["access_token"]
        assert pat and "admin" not in pat.lower()

    work = WORKDIR / "push-work"
    shutil.copytree(anon, work)
    (work / "POC.md").write_text("# oauth poc\n", encoding="utf-8")
    _git(work, ["add", "POC.md"], env=env)
    _git(work, ["commit", "-m", "poc: oauth push"], env=env)
    basic = base64.b64encode(f"git:{pat}".encode()).decode()
    _git(
        work,
        [
            "-c",
            "credential.helper=",
            "-c",
            f"http.extraHeader=Authorization: Basic {basic}",
            "push",
            "origin",
            "HEAD:main",
        ],
        env=env,
    )
    print("Push username=git + PAT: OK")

    (work / "POC2.md").write_text("second\n", encoding="utf-8")
    _git(work, ["add", "POC2.md"], env=env)
    _git(work, ["commit", "-m", "poc: second"], env=env)
    _git(
        work,
        [
            "-c",
            "credential.helper=",
            "-c",
            f"http.extraHeader=Authorization: Basic {basic}",
            "push",
            "origin",
            "HEAD:main",
        ],
        env=env,
    )
    print("Second push: OK")

    host = urlsplit(gitea_url).netloc
    print("")
    print("=== RAPPORT POC ===")
    print("GO: OAuth Hub (approve+token) → PAT Gitea.")
    print("GO: clone anonyme sans credential.")
    print("GO: push HTTPS avec username « git » + PAT (oauthDefaultUserName).")
    print("GO: config Git isolée sans helper LOCALAPPDATA.")
    print(
        f"MANUEL: premier push interactif GCM sur {host} "
        "(oauthAuthorizeEndpoint/Token → Hub) sur machine neuve."
    )
    print(f"Workdir: {WORKDIR}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print("POC ÉCHEC:", error)
        raise
