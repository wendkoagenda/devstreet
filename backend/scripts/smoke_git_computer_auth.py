"""Smoke réel : device-auth DevStreet → PAT Gitea → git fetch/push → révocation.

N'envoie jamais le dépôt « devstreet ». Utilise un clone jetable sous backend/.local/.
La confirmation navigateur est simulée via l'API authentifiée (même service que la page).
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings

from app.devstreet_hub.conf import config
from app.devstreet_hub.models import ForgeIdentity, GitConnectedComputer
from app.devstreet_hub.services.gitea_client import GiteaClient
from app.devstreet_hub.services.git_auth_service import GitAuthService


ROOT = Path(settings.BASE_DIR)
WORKDIR = ROOT / ".local" / "git-computer-auth-smoke"
REPO_NAME = "ds-computer-auth-smoke"


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


def _git(cwd: Path, args: list[str], *, login: str, token: str, check: bool = True):
    """Git HTTPS avec PAT en Basic Auth (jamais dans l'URL du remote)."""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    basic = base64.b64encode(f"{login}:{token}".encode()).decode()
    cmd = [
        "git",
        "-c",
        "credential.helper=",
        "-c",
        f"http.extraHeader=Authorization: Basic {basic}",
        "-c",
        "user.email=smoke@devstreet.local",
        "-c",
        "user.name=DevStreet Smoke",
        *args,
    ]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} a échoué ({result.returncode}): "
            f"{(result.stderr or result.stdout)[:500]}"
        )
    return result


def _ensure_smoke_actor():
    """Compte Django + ForgeIdentity jetables (évite les e-mails démo déjà sur Gitea)."""
    from app.core.models import Permission, Role
    from app.devstreet_hub.management.commands.init_devstreet_hub import ADMIN_CODES
    from app.devstreet_hub.services.workflow_service import WorkflowService

    User = get_user_model()
    email = "smoke-computer-auth@devstreet.local"
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": "smoke-computer-auth",
            "is_active": True,
        },
    )
    if created or not user.has_usable_password():
        user.set_password("Smoke-Computer-Auth-42!")
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
        # Reprend / crée sans toucher aux comptes démo conflictuels.
        if identity and identity.status == ForgeIdentity.STATUS_CONFLICT:
            identity.delete()
        WorkflowService().provision_identity(user)
        identity = ForgeIdentity.objects.get(user=user)
    return user, identity


def _ensure_smoke_repo(forge: GiteaClient, login: str) -> str:
    """Crée ou réutilise un dépôt privé jetable sous le compte forge."""
    existing = forge.request(
        "GET",
        f"/repos/{login}/{REPO_NAME}",
        missing_ok=True,
    )
    if existing is None:
        forge.request(
            "POST",
            f"/admin/users/{login}/repos",
            {
                "name": REPO_NAME,
                "private": True,
                "auto_init": True,
                "default_branch": "main",
                "description": "Dépôt jetable smoke Connecter mon ordinateur",
            },
        )
    public = (config("GITEA_PUBLIC_URL") or config("GITEA_URL")).rstrip("/")
    return f"{public}/{login}/{REPO_NAME}.git"


def main() -> int:
    if not settings.DEBUG:
        raise SystemExit("Smoke réservé au développement local (DEBUG=True).")
    owner, identity = _ensure_smoke_actor()
    print(f"acteur={owner.email} login={identity.login} status={identity.status}")
    if identity.status != ForgeIdentity.STATUS_LINKED:
        raise SystemExit(
            f"Identité forge non liée ({identity.status}). Impossible de continuer."
        )
    forge = GiteaClient()
    clone_url = _ensure_smoke_repo(forge, identity.login)

    hub = settings.FRONTEND_URL.rstrip("/")
    verifier, challenge = _pkce()
    computer_name = f"Smoke-{secrets.token_hex(3)}"

    with override_settings(
        # Garantit l'acceptation de l'URL hub locale.
        FRONTEND_URL=hub,
    ):
        service = GitAuthService(forge=forge)
        started = service.start_device_auth(
            computer_name=computer_name,
            hub_base_url=hub,
            code_challenge=challenge,
        )
        request_id = started["request_id"]
        # Confirmation explicite (équivalent bouton Autoriser, sans navigateur).
        authorized = service.authorize(owner, request_id)
        assert authorized["status"] == "authorized"

        # Respecte l'intervalle de polling.
        time.sleep(2.1)
        grant = service.poll(request_id=request_id, code_verifier=verifier)
        assert grant["status"] == "authorized", grant
        token = grant["token"]
        login = grant["login"]
        computer_id = grant["computer_id"]
        assert "admin" not in token.lower()
        assert login == identity.login

        # Rejeu : plus de jeton.
        time.sleep(2.1)
        replay = service.poll(request_id=request_id, code_verifier=verifier)
        assert replay["status"] == "consumed"
        assert "token" not in replay

    # Clone + push avec le PAT (Basic), dépôt jetable uniquement.
    run_dir = WORKDIR / secrets.token_hex(4)
    if WORKDIR.exists():
        shutil.rmtree(WORKDIR, ignore_errors=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    clone_dir = run_dir / "repo"
    _git(run_dir, ["clone", clone_url, str(clone_dir)], login=login, token=token)
    marker = f"smoke-{secrets.token_hex(4)}.txt"
    (clone_dir / marker).write_text("ok\n", encoding="utf-8")
    _git(clone_dir, ["add", marker], login=login, token=token)
    _git(clone_dir, ["commit", "-m", "smoke computer auth"], login=login, token=token)
    _git(clone_dir, ["push", "origin", "HEAD"], login=login, token=token)
    _git(clone_dir, ["fetch", "origin"], login=login, token=token)
    print("OK push/fetch avec PAT device-auth")

    # Révocation serveur.
    service = GitAuthService(forge=forge)
    service.revoke_computer(owner, computer_id)
    computer = GitConnectedComputer.objects.get(pk=computer_id)
    assert computer.status == GitConnectedComputer.STATUS_REVOKED

    # Push doit échouer après révocation.
    (clone_dir / marker).write_text("revoked\n", encoding="utf-8")
    _git(clone_dir, ["add", marker], login=login, token=token)
    _git(
        clone_dir,
        ["commit", "-m", "should fail after revoke"],
        login=login,
        token=token,
    )
    failed = _git(
        clone_dir,
        ["push", "origin", "HEAD"],
        login=login,
        token=token,
        check=False,
    )
    if failed.returncode == 0:
        raise RuntimeError("Le push a réussi après révocation — PAT encore valide.")
    print("OK push refusé après révocation")

    # Deuxième ordinateur : ne doit pas être touché.
    verifier2, challenge2 = _pkce()
    started2 = service.start_device_auth(
        computer_name=f"Smoke2-{secrets.token_hex(3)}",
        hub_base_url=hub,
        code_challenge=challenge2,
    )
    service.authorize(owner, started2["request_id"])
    time.sleep(2.1)
    grant2 = service.poll(
        request_id=started2["request_id"], code_verifier=verifier2
    )
    other = GitConnectedComputer.objects.get(pk=grant2["computer_id"])
    assert other.status == GitConnectedComputer.STATUS_ACTIVE
    # Nettoyage du 2e PAT pour ne pas laisser traîner.
    service.revoke_computer(owner, other.pk)
    print("OK second ordinateur indépendant puis nettoyé")

    # Hub arbitraire refusé (même règle que l'API start).
    from rest_framework.exceptions import ValidationError

    try:
        service.start_device_auth(
            computer_name="BadHub",
            hub_base_url="https://evil.example",
            code_challenge=challenge2,
        )
        raise RuntimeError("hub arbitraire accepté")
    except ValidationError:
        print("OK hub arbitraire rejeté")

    print("SMOKE git-computer-auth: SUCCÈS")
    print(f"clone_url={clone_url}")
    print(f"workdir={run_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"SMOKE ÉCHEC: {exc}", file=sys.stderr)
        raise
