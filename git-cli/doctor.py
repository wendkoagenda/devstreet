#!/usr/bin/env python3
import platform
import shutil
import sys
from pathlib import Path

from git_utils import (
    GIT_MASTER_EMAILS,
    ACCESS_CONTROL_FILE,
    IDENTITY_RESTRICTED_BRANCHES,
    PROTECTED_PATHS,
    colorize,
    ensure_local_enforcement,
    get_status_porcelain_entries,
    print_banner,
    run_command,
)


def status_line(ok, label, details=""):
    if ok:
        mark = colorize("[OK]", "32")
    else:
        mark = colorize("[KO]", "31")
    suffix = f" - {details}" if details else ""
    print(f"{mark} {label}{suffix}")


def command_version(cmd):
    code, output = run_command(cmd)
    if code != 0:
        return False, ""
    return True, output.splitlines()[0] if output else ""


def get_repo_root():
    code, output = run_command(["git", "rev-parse", "--show-toplevel"])
    if code != 0 or not output:
        return None
    return Path(output.strip())


def get_git_identity(repo_root):
    code_user, user = run_command(["git", "config", "--get", "user.name"], cwd=str(repo_root))
    code_email, email = run_command(["git", "config", "--get", "user.email"], cwd=str(repo_root))
    if code_user != 0 or code_email != 0:
        return None, None
    return (user or "").strip(), (email or "").strip()


def check_hooks(repo_root):
    hooks_ok = ensure_local_enforcement(repo_root)
    code, hooks_path = run_command(["git", "config", "--get", "core.hooksPath"], cwd=str(repo_root))
    hooks_path = hooks_path.strip() if code == 0 and hooks_path else "<non defini>"
    status_line(hooks_ok, "Hooks locaux actifs", f"core.hooksPath={hooks_path}")


def check_tools():
    print(colorize("\nOutils", "36"))
    ok, line = command_version(["git", "--version"])
    status_line(ok, "Git", line)

    python_line = f"Python {sys.version.split()[0]}"
    status_line(True, "Python", python_line)

    npm_path = shutil.which("npm.cmd") if os_is_windows() else shutil.which("npm")
    if npm_path:
        ok, line = command_version([npm_path, "--version"])
        detail = f"{line} ({npm_path})" if ok else npm_path
        status_line(ok, "npm", detail)
    else:
        status_line(False, "npm", "introuvable dans PATH")

    gh_path = shutil.which("gh")
    if gh_path:
        ok, line = command_version(["gh", "--version"])
        status_line(ok, "gh", line)
        auth_ok, _ = run_command(["gh", "auth", "status"])
        status_line(auth_ok == 0, "gh auth", "connecte" if auth_ok == 0 else "non connecte")
    else:
        status_line(False, "gh", "introuvable dans PATH")


def os_is_windows():
    return platform.system().lower().startswith("win")


def check_repo(repo_root):
    print(colorize("\nRepository", "36"))
    status_line(True, "Racine repo", str(repo_root))

    code_branch, branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(repo_root))
    if code_branch == 0 and branch:
        status_line(True, "Branche courante", branch.strip())
    else:
        status_line(False, "Branche courante", "indisponible")

    try:
        changed = len(get_status_porcelain_entries(cwd=str(repo_root)))
        details = "working tree propre" if changed == 0 else f"{changed} changements detectes"
        status_line(True, "Etat du working tree", details)
    except RuntimeError:
        status_line(False, "Etat du working tree", "impossible a lire")

    user, email = get_git_identity(repo_root)
    if user and email:
        status_line(True, "Identite Git", f"{user} <{email}>")
        current_branch = branch.strip() if code_branch == 0 and branch else ""
        if current_branch in IDENTITY_RESTRICTED_BRANCHES:
            branch_allowed = email in GIT_MASTER_EMAILS
            status_line(
                branch_allowed,
                f"Autorisation push {current_branch}",
                "autorise" if branch_allowed else "non autorise",
            )
        else:
            status_line(True, "Autorisation push (branche courante)", "aucune restriction d'identite")
        status_line(True, "GIT_MASTER_EMAILS", ", ".join(GIT_MASTER_EMAILS))
        status_line(True, "Branches protegees", ", ".join(IDENTITY_RESTRICTED_BRANCHES))
    else:
        status_line(False, "Identite Git", "user.name / user.email non configures")

    check_hooks(repo_root)
    status_line(True, "Configuration acces", ACCESS_CONTROL_FILE)
    status_line(True, "Chemins proteges", ", ".join(PROTECTED_PATHS) if PROTECTED_PATHS else "aucun")


def main():
    print_banner("Doctor")

    repo_root = get_repo_root()
    if repo_root is None:
        status_line(False, "Depot Git", "non detecte")
        print("\nExecutez cette commande depuis un depot Git.")
        return 1

    check_tools()
    check_repo(repo_root)

    print(colorize("\nConseil", "36"))
    print("Si un check est KO, commencez par executer:")
    print("python git-cli/install-hooks.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
