#!/usr/bin/env python3
"""Audit des zones protegees : motifs orphelins + fichiers hors zone.

Lancement : python git-cli/check_zones.py

En mode commit (warn_only=True) : affiche un avertissement, ne bloque jamais.
En lancement manuel : code de sortie 2 si motifs orphelins (comme la CI).
"""
import os
import sys
from pathlib import Path

from git_utils import colorize, print_step, print_success, run_command

REPO_ROOT = Path(__file__).resolve().parent.parent


def _backend_python():
    for relative in (
        Path("backend") / "venv" / "Scripts" / "python.exe",
        Path("backend") / "venv" / "bin" / "python",
    ):
        candidate = REPO_ROOT / relative
        if candidate.is_file():
            return str(candidate)
    return None


def _child_env():
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_zones_audit(warn_only=False):
    """
    Lance python -m scripts.regression_guard --audit.
    warn_only=True : toujours True (avertissement pour commit.py).
    warn_only=False : True si exit 0, False si orphelins (exit 2) ou erreur.
    """
    print_step("Audit des zones protegees")
    python = _backend_python()
    if not python:
        message = "venv backend introuvable : audit des zones ignore."
        if warn_only:
            print(colorize(f"  Avertissement : {message}", "33"))
            return True
        print(colorize(f"  Echec : {message}", "31"))
        return False

    print(colorize("  [audit]", "1;36"))
    code, output = run_command(
        [python, "-m", "scripts.regression_guard", "--root", str(REPO_ROOT), "--audit"],
        cwd=str(REPO_ROOT / "backend"),
        env=_child_env(),
    )
    if output:
        for line in output.splitlines():
            print(f"    {line}")

    if code == 0:
        print_success("Audit zones : aucun motif orphelin")
        if output and "hors zone" in output.lower():
            print(colorize(
                "  Info : des fichiers sont hors zone (volontaire pour le metier) ; "
                "voir le resume ci-dessus.",
                "33",
            ))
        return True

    if code == 2:
        print(colorize("  Avertissement : motifs ou chemins orphelins detectes.", "33"))
        print(colorize(
            "  La CI non-regression bloquera tant que regression-guard.json "
            "ou PROTECTED_PATHS ne seront pas mis a jour.",
            "33",
        ))
        if warn_only:
            return True
        return False

    print(colorize(f"  Avertissement : audit zones code {code}.", "33"))
    return True if warn_only else False


def main():
    ok = run_zones_audit(warn_only=False)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
