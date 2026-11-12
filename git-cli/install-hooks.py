#!/usr/bin/env python3
from pathlib import Path

from git_utils import colorize, print_banner, run_command


def print_success(message):
    print(colorize(f"Succes: {message}", "32"))


def main():
    print_banner("Install Hooks")

    repo_root = Path(__file__).resolve().parents[1]
    hooks_dir = repo_root / ".githooks"
    required_hooks = [hooks_dir / "commit-msg", hooks_dir / "pre-push"]
    access_control_file = repo_root / "git-cli" / "access_control.conf"

    print(f"Repository: {repo_root}")
    print(f"Hooks path attendu: {hooks_dir}")

    for hook in required_hooks:
        if not hook.exists():
            print(colorize(f"Erreur: hook manquant: {hook}", "31"))
            return 1
    if not access_control_file.exists():
        print(colorize(f"Erreur: configuration manquante: {access_control_file}", "31"))
        return 1

    code, output = run_command(["git", "config", "core.hooksPath", ".githooks"], cwd=str(repo_root))
    if code != 0:
        print(colorize("Erreur: impossible de configurer core.hooksPath", "31"))
        if output:
            print(output)
        return 1
    print_success("core.hooksPath configure sur .githooks")

    if output:
        print(output)

    code, current = run_command(["git", "config", "--get", "core.hooksPath"], cwd=str(repo_root))
    if code != 0:
        print(colorize("Erreur: impossible de verifier core.hooksPath", "31"))
        return 1
    print_success(f"Valeur actuelle: {current}")
    print("")
    print("Installation terminee.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
