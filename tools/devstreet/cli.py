"""Commandes : auth login | auth status | auth logout."""

from __future__ import annotations

import argparse
import base64
import hashlib
import os
import platform
import secrets
import sys
import time
import webbrowser
from urllib.parse import urlsplit

import httpx

from . import __version__
from .git_helper import clear_git_credential, setup_git_credential
from .secure_store import list_accounts, remove_account, store_account


def _api_v1(hub: str) -> str:
    return hub.rstrip("/") + "/api/v1"


def _pkce_pair() -> tuple[str, str]:
    verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii").rstrip("=")
    )
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .decode("ascii")
        .rstrip("=")
    )
    return verifier, challenge


def cmd_login(args: argparse.Namespace) -> int:
    hub = args.hub.rstrip("/")
    api = (args.api or _api_v1(hub)).rstrip("/")
    computer = args.computer or os.environ.get("COMPUTERNAME") or platform.node() or "ordinateur"
    verifier, challenge = _pkce_pair()
    with httpx.Client(timeout=30.0, trust_env=False) as client:
        start = client.post(
            api + "/git-auth/device/start",
            json={
                "computer_name": computer,
                "hub_base_url": hub,
                "code_challenge": challenge,
            },
        )
        if start.status_code >= 400:
            print(
                "Échec du démarrage :",
                start.text[:300],
                file=sys.stderr,
            )
            return 1
        payload = start.json()
        authorize_url = payload["authorize_url"]
        request_id = payload["request_id"]
        interval = int(payload.get("interval_seconds") or 2)
        print("Ouvrez le navigateur pour autoriser cet ordinateur sur DevStreet.")
        print(authorize_url)
        try:
            webbrowser.open(authorize_url)
        except Exception:
            pass
        print("En attente de votre confirmation…")
        deadline = time.time() + 10 * 60
        while time.time() < deadline:
            time.sleep(max(interval, 2))
            poll = client.post(
                api + f"/git-auth/{request_id}/poll",
                json={"code_verifier": verifier},
            )
            if poll.status_code == 429:
                time.sleep(2)
                continue
            if poll.status_code >= 400:
                print("Erreur de vérification :", poll.text[:300], file=sys.stderr)
                return 1
            body = poll.json()
            status = body.get("status")
            if status == "pending":
                continue
            if status == "denied":
                print("Autorisation refusée.")
                return 2
            if status in ("expired", "consumed"):
                print("Demande expirée ou déjà utilisée.")
                return 3
            if status == "authorized":
                token = body["token"]
                login = body["login"]
                gitea_url = body["gitea_url"]
                store_account(
                    hub=hub,
                    login=login,
                    token=token,
                    gitea_url=gitea_url,
                    computer_id=body.get("computer_id"),
                    computer_name=body.get("computer_name") or computer,
                )
                setup_git_credential(gitea_url, login, token)
                print(f"Connecté en tant que {login} ({urlsplit(gitea_url).netloc}).")
                print("git push / git fetch peuvent utiliser cet accès.")
                return 0
            print("Statut inattendu :", status, file=sys.stderr)
            return 1
    print("Délai dépassé.", file=sys.stderr)
    return 4


def cmd_status(_args: argparse.Namespace) -> int:
    accounts = list_accounts()
    if not accounts:
        print("Aucun ordinateur connecté.")
        return 0
    for account in accounts:
        mark = "*" if account.get("active") else " "
        secret = "ok" if account.get("has_secret") else "manquant"
        print(
            f"{mark} {account['login']} @ {account['gitea_url']} "
            f"({account.get('computer_name')}) secret={secret}"
        )
    return 0


def cmd_logout(args: argparse.Namespace) -> int:
    accounts = list_accounts()
    if not accounts:
        print("Rien à déconnecter.")
        return 0
    target = None
    if args.login:
        target = next((a for a in accounts if a["login"] == args.login), None)
    else:
        target = next((a for a in accounts if a.get("active")), accounts[0])
    if not target:
        print("Compte introuvable.", file=sys.stderr)
        return 1
    clear_git_credential(target["gitea_url"], target["login"])
    remove_account(target["hub"], target["login"])
    print(f"Déconnexion locale de {target['login']}.")
    print(
        "Pour révoquer côté serveur : Mon compte → Ordinateurs connectés dans DevStreet."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devstreet",
        description="CLI DevStreet — connexion Git via navigateur",
    )
    parser.add_argument("--version", action="version", version=f"devstreet {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("auth", help="Connexion Git")
    auth_sub = auth.add_subparsers(dest="auth_command", required=True)

    login = auth_sub.add_parser("login", help="Autoriser cet ordinateur")
    login.add_argument(
        "--hub",
        required=True,
        help="URL publique DevStreet (ex. http://localhost:5173)",
    )
    login.add_argument(
        "--api",
        default=None,
        help="Base API v1 (défaut: {hub}/api/v1 via proxy same-origin)",
    )
    login.add_argument("--computer", default=None, help="Nom affiché de l'ordinateur")
    login.set_defaults(func=cmd_login)

    status = auth_sub.add_parser("status", help="Comptes enregistrés")
    status.set_defaults(func=cmd_status)

    logout = auth_sub.add_parser("logout", help="Retirer le secret local")
    logout.add_argument("--login", default=None, help="Login forge à déconnecter")
    logout.set_defaults(func=cmd_logout)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
