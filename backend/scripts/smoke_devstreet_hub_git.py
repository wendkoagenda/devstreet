"""Test local réel de lecture et push Git ; n'envoie jamais le dépôt devstreet sur la forge.

Réservé aux comptes .local de démonstration. Le mot de passe Git de ces fixtures est
réinitialisé via l'API administrative pour tester sans interface navigateur.
"""

import base64
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from django.conf import settings
from django.contrib.auth import get_user_model
from app.devstreet_hub.models import Project, ForgeIdentity
from app.devstreet_hub.services.gitea_client import GiteaClient
from app.devstreet_hub.services.workflow_service import WorkflowService


def main():
    if not settings.DEBUG:
        raise SystemExit("Test réservé au développement local.")
    credentials = json.loads(
        (Path(settings.BASE_DIR) / ".local/demo.credentials.json").read_text(
            encoding="utf-8"
        )
    )
    User = get_user_model()
    owner = User.objects.get(pk=credentials["aicha-chantier"]["id"])
    contributor = User.objects.get(pk=credentials["moussa-chantier"]["id"])
    project = (
        Project.objects.filter(owner=owner, repository__status="ready")
        .order_by("-id")
        .first()
    )
    if project is None:
        raise SystemExit("Exécuter d’abord la collection Postman.")
    repository = project.repository
    forge = GiteaClient()
    path = forge.repo_path(repository)
    for filename, content in [
        (
            "README.md",
            "# Stock\n\nApplication de démonstration créée pour le test DevStreet Hub.\n",
        ),
        ("stock.py", "def export_stock():\n    return []\n"),
    ]:
        existing = forge.request("GET", path + "/contents/" + filename, missing_ok=True)
        if existing is None:
            forge.request(
                "POST",
                path + "/contents/" + filename,
                {
                    "content": base64.b64encode(content.encode()).decode(),
                    "message": "Initialiser le projet de démonstration",
                    "branch": repository.default_branch,
                },
            )
    WorkflowService().provision_identity(contributor)
    tokens = {}
    credentials["forge"] = {}
    for actor in (owner, contributor):
        identity = ForgeIdentity.objects.get(user=actor)
        password = secrets.token_urlsafe(32)
        forge.request(
            "PATCH",
            "/admin/users/" + identity.login,
            {"password": password, "must_change_password": False},
        )
        response = httpx.post(
            forge.url + "/api/v1/users/" + identity.login + "/tokens",
            auth=(identity.login, password),
            json={
                "name": "local-smoke-" + secrets.token_hex(5),
                "scopes": ["write:repository"],
            },
            timeout=15,
        )
        response.raise_for_status()
        tokens[actor.pk] = (identity.login, password, response.json()["sha1"])
        credentials["forge"][str(actor.pk)] = {
            "login": identity.login,
            "password": password,
        }
    directory = Path(settings.BASE_DIR) / ".local/git-smoke"
    directory.mkdir(exist_ok=True)

    def git(args, actor, check=True):
        login, password, token = tokens[actor.pk]
        env = os.environ.copy()
        env.update(
            {
                "GIT_TERMINAL_PROMPT": "0",
                "GIT_CONFIG_COUNT": "2",
                "GIT_CONFIG_KEY_0": "http.extraHeader",
                "GIT_CONFIG_VALUE_0": "Authorization: Basic "
                + base64.b64encode((login + ":" + token).encode()).decode(),
                "GIT_CONFIG_KEY_1": "credential.helper",
                "GIT_CONFIG_VALUE_1": "",
            }
        )
        result = subprocess.run(
            ["git", *args], cwd=directory, env=env, capture_output=True, text=True
        )
        if check and result.returncode:
            raise RuntimeError("Échec de la vérification Git : " + args[0])
        return result

    git(["init"], owner)
    # Le dépôt de test ne contient que les fichiers synthétiques créés ci-dessus.
    git(
        [
            "fetch",
            forge.url + "/" + repository.namespace + "/" + repository.name + ".git",
            repository.default_branch,
        ],
        owner,
    )
    destination = (
        forge.url + "/" + repository.namespace + "/" + repository.name + ".git"
    )
    git(["push", destination, "FETCH_HEAD:refs/heads/smoke-owner"], owner)
    denied = git(
        ["push", destination, "FETCH_HEAD:refs/heads/smoke-denied"],
        contributor,
        check=False,
    )
    if denied.returncode == 0:
        raise RuntimeError("Le compte sans droit a pu pousser.")
    sha = forge.head(repository)
    sources = forge.collect_sources(repository, sha)
    # Révoquer les tokens de test immédiatement après les vérifications.
    for actor in (owner, contributor):
        login, password, token = tokens[actor.pk]
        response = httpx.get(
            forge.url + "/api/v1/users/" + login + "/tokens",
            auth=(login, password),
            timeout=15,
        )
        response.raise_for_status()
        entries = response.json()
        for entry in entries:
            if entry.get("name", "").startswith("local-smoke-"):
                response = httpx.delete(
                    forge.url
                    + "/api/v1/users/"
                    + login
                    + "/tokens/"
                    + str(entry["id"]),
                    auth=(login, password),
                    timeout=15,
                )
                response.raise_for_status()
    (Path(settings.BASE_DIR) / ".local/demo.credentials.json").write_text(
        json.dumps(credentials, ensure_ascii=False), encoding="utf-8"
    )
    print(
        "PASS : lecture Git et push propriétaire réels ; push tiers refusé ; collecte au SHA ("
        + str(len(sources))
        + " sources) ; tokens de test révoqués"
    )


if __name__ == "__main__":
    main()
