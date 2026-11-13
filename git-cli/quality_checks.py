#!/usr/bin/env python3
"""Controles locaux lances par commit.py : securite, backend, frontend.

Echec d'un controle : menu pour relancer ou quitter proprement (pas d'ejection brutale).
Alignes sur la CI (lint frontend seulement ; tests/build restent dans ci-frontend).
"""
import os
import shutil
import sys
from pathlib import Path

from git_utils import ask_input, colorize, print_step, print_success, run_command

REPO_ROOT = Path(__file__).resolve().parent.parent


def _child_env():
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _backend_python():
    for relative in (
        Path("backend") / "venv" / "Scripts" / "python.exe",
        Path("backend") / "venv" / "bin" / "python",
    ):
        candidate = REPO_ROOT / relative
        if candidate.is_file():
            return str(candidate)
    return None


def _npm_executable():
    """Sous Windows, subprocess ne lance pas le shim `npm` : il faut `npm.cmd`."""
    if sys.platform == "win32":
        return shutil.which("npm.cmd") or shutil.which("npm")
    return shutil.which("npm")


def _print_block(title):
    print("")
    print(colorize(f"  [{title}]", "1;36"))


def _print_output(output):
    if not output:
        return
    for line in output.splitlines():
        print(f"    {line}")


def _looks_like_missing_django(output):
    text = (output or "").lower()
    return "no module named 'django'" in text or "couldn't import django" in text


def _run_captured(title, command, cwd):
    _print_block(title)
    code, output = run_command(command, cwd=str(cwd), env=_child_env())
    _print_output(output)
    if code != 0:
        if _looks_like_missing_django(output):
            print(colorize(
                "    Django absent du venv. Depuis backend/ : "
                ".\\venv\\Scripts\\Activate.ps1 ; pip install -r requirements.txt",
                "33",
            ))
        print(colorize(f"  Echec — {title}", "31"))
        return False
    print(colorize(f"  OK — {title}", "32"))
    return True


def check_securite():
    python = _backend_python()
    if not python:
        _print_block("securite")
        print(colorize("    venv backend introuvable (backend/venv).", "31"))
        return False
    return _run_captured(
        "securite",
        [python, "-m", "scripts.security_scan", "--fail-on", "warning"],
        REPO_ROOT / "backend",
    )


def check_backend():
    python = _backend_python()
    if not python:
        _print_block("backend")
        print(colorize("    venv backend introuvable (backend/venv).", "31"))
        return False
    backend = REPO_ROOT / "backend"

    _print_block("backend — conflits de migrations")
    code, output = run_command(
        [python, "manage.py", "makemigrations", "--merge", "--dry-run", "--noinput"],
        cwd=str(backend),
        env=_child_env(),
    )
    _print_output(output)
    if code != 0:
        if _looks_like_missing_django(output):
            print(colorize(
                "    Django absent du venv. Depuis backend/ : "
                ".\\venv\\Scripts\\Activate.ps1 ; pip install -r requirements.txt",
                "33",
            ))
        print(colorize("  Echec — backend (conflits de migrations)", "31"))
        return False
    if "No conflicts detected to merge." not in (output or ""):
        print(colorize(
            "    Conflit de migrations : lancer makemigrations --merge puis recommencer.",
            "33",
        ))
        print(colorize("  Echec — backend (conflits de migrations)", "31"))
        return False
    print(colorize("  OK — backend (conflits de migrations)", "32"))

    return _run_captured(
        "backend — migrations manquantes",
        [python, "manage.py", "makemigrations", "--check", "--dry-run"],
        backend,
    )


def check_frontend():
    if not (REPO_ROOT / "frontend" / "package.json").is_file():
        _print_block("frontend")
        print(colorize("    frontend/package.json introuvable.", "31"))
        return False
    npm = _npm_executable()
    if not npm:
        _print_block("frontend — lint")
        print(colorize(
            "    npm introuvable dans le PATH. Installez Node.js ou ouvrez un terminal ou npm est disponible.",
            "31",
        ))
        print(colorize("  Echec — frontend — lint", "31"))
        return False
    return _run_captured(
        "frontend — lint",
        [npm, "run", "lint"],
        REPO_ROOT / "frontend",
    )


def _run_once():
    checks = (
        ("securite", check_securite),
        ("backend", check_backend),
        ("frontend", check_frontend),
    )
    for name, fn in checks:
        if not fn():
            return False, name
    return True, None


def _ask_after_failure(failed_name):
    """1 = relancer, 2 / q = quitter. Ne quitte jamais tout seul."""
    print("")
    print(colorize(f"Controle « {failed_name} » en echec.", "31"))
    print("Options :")
    print("  1. Relancer les trois controles")
    print("  2. Quitter (annuler le commit)")
    print("  q. Quitter")
    while True:
        choice = ask_input("Votre choix (1/2/q): ").lower()
        if choice in {"1", "relancer", "r"}:
            return "retry"
        if choice in {"2", "quitter", "n"}:
            return "quit"
        print("Choix invalide. Repondez par 1, 2 ou q.")


def run_quality_checks():
    """
    Lance securite, backend, frontend.
    Retourne True si OK, False si l'utilisateur choisit de quitter apres un echec.
    Lever UserQuit si l'utilisateur tape q.
    """
    print_step("Controles locaux (securite, backend, frontend)")
    print("Les trois doivent passer pour continuer le commit.")
    print("Frontend : lint seulement (tests et build restent dans la CI).")

    while True:
        ok, failed = _run_once()
        if ok:
            print("")
            print_success("Controles locaux OK")
            return True
        action = _ask_after_failure(failed)
        if action == "retry":
            print("")
            print("Relance des controles...")
            continue
        print("Commit annule.")
        return False
