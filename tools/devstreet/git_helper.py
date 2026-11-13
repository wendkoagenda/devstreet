"""Configure Git pour réutiliser le PAT DevStreet sans écraser les autres helpers."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


def _run_git(*args: str, ok_codes: tuple[int, ...] = (0,)) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in ok_codes:
        raise RuntimeError(result.stderr.strip() or "git a échoué")
    return result.stdout.strip()


def setup_git_credential(gitea_url: str, login: str, token: str) -> None:
    """Enregistre le PAT pour l'hôte Gitea et ajoute un helper DevStreet en tête."""
    host = urlsplit(gitea_url).netloc
    if not host:
        raise RuntimeError("URL Gitea invalide")

    helper_script = Path(__file__).resolve().parent / "git-credential-devstreet.py"
    python = shutil.which("python") or shutil.which("py")
    if not python:
        raise RuntimeError("Interpréteur Python introuvable pour le credential helper.")

    # Helper DevStreet en premier, sans retirer manager-core / wincred existants.
    # Code 1 : aucun helper configuré (cas normal) ; toute autre erreur de git remonte.
    listed = _run_git(
        "config", "--global", "--get-all", "credential.helper", ok_codes=(0, 1)
    )
    existing = [line for line in listed.splitlines() if line.strip()]

    helper_value = f"!{python} {helper_script}"
    # Remplace une ancienne entrée DevStreet si présente.
    filtered = [h for h in existing if "git-credential-devstreet" not in h]
    # Code 5 : clé absente, rien à retirer.
    _run_git("config", "--global", "--unset-all", "credential.helper", ok_codes=(0, 5))
    _run_git("config", "--global", "--add", "credential.helper", helper_value)
    for helper in filtered:
        _run_git("config", "--global", "--add", "credential.helper", helper)

    # Alimente aussi le store OS via git credential approve (compatible manager).
    payload = (
        f"protocol=https\nhost={host}\nusername={login}\npassword={token}\n\n"
    )
    proc = subprocess.run(
        ["git", "credential", "approve"],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        # Non bloquant : le helper DevStreet suffit.
        pass


def clear_git_credential(gitea_url: str, login: str) -> None:
    host = urlsplit(gitea_url).netloc
    if not host:
        return
    payload = f"protocol=https\nhost={host}\nusername={login}\n\n"
    subprocess.run(
        ["git", "credential", "reject"],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
