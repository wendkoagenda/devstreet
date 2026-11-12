#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

VERSION = "2.0"
VERSION_DATE = "octobre 2026"
GIT_CLI_VERSION = VERSION
COMMIT_TRAILER = f"X-Git-CLI: onepourcent-git-cli/{GIT_CLI_VERSION}"
PR_MARKER = f"<!-- X-Git-CLI-PR: onepourcent-git-cli/{GIT_CLI_VERSION} -->"
PUSH_ENV_KEY = "ONEPOURCENT_GITCLI_PUSH"
REQUIRED_HOOKS = (".githooks/commit-msg", ".githooks/pre-push")
ACCESS_CONTROL_FILE = "git-cli/access_control.conf"
IDENTITY_RESTRICTED_BRANCHES = tuple()
GIT_MASTER_EMAILS = tuple()
PROTECTED_PATHS = tuple()

BANNER = r"""
      ___                ____                                          _
     / _ \  _ __    ___ |  _ \   ___   _   _  _ __   ___   ___  _ __  | |_
    | | | || '_ \  / _ \| |_) | / _ \ | | | || '__| / __| / _ \| '_ \ | __|
    | |_| || | | ||  __/|  __/ | (_) || |_| || |   | (__ |  __/| | | || |_
     \___/ |_| |_| \___||_|     \___/  \__,_||_|    \___| \___||_| |_| \__|
"""


def colorize(text, color_code):
    if not sys.stdout.isatty():
        return text
    return f"\033[{color_code}m{text}\033[0m"


class UserQuit(Exception):
    pass


def print_banner(command_name):
    print(colorize(BANNER, "36"))
    print(colorize(f"    Git CLI v{GIT_CLI_VERSION}  -  {command_name}", "1;36"))
    print(colorize(f"    {VERSION_DATE}", "2"))
    print(colorize("    " + "-" * 48, "2"))
    print("")


def print_step(title):
    separator = "*" * 72
    print("")
    print(colorize(separator, "36"))
    print(colorize(f"* {title}", "36"))
    print(colorize(separator, "36"))


def print_success(message):
    print(colorize(f"Succes: {message}", "32"))


def ask_input(prompt_text):
    value = input(prompt_text).strip()
    if value.lower() in {"q", "quit", "exit"}:
        raise UserQuit()
    return value


def ask_confirm(prompt_text):
    while True:
        answer = ask_input(f"{prompt_text} [o/N, q=quitter]: ").lower()
        if answer in {"", "n", "non", "no"}:
            return False
        if answer in {"o", "oui", "y", "yes"}:
            return True
        print("Reponse invalide. Repondez par o, n ou q.")


def ask_non_empty(prompt_text):
    while True:
        value = ask_input(prompt_text)
        if value:
            return value
        print("Ce champ est obligatoire.")


def run_command(command, cwd=None, stream=False, env=None):
    if stream:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
        process.wait()
        return process.returncode, ""

    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output.strip()


def is_git_diagnostic_line(line):
    lowered = line.strip().lower()
    diagnostic_prefixes = (
        "warning:",
        "fatal:",
        "error:",
        "hint:",
        "avertissement:",
        "erreur:",
        "indice:",
    )
    return lowered.startswith(diagnostic_prefixes)


def _dedupe_preserve_order(items):
    return list(dict.fromkeys(items))


def get_status_porcelain_entries(cwd=None):
    completed = subprocess.run(
        ["git", "status", "--porcelain=1", "-z"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("Impossible de lire le statut git.")

    raw_output = completed.stdout or ""
    raw_tokens = [
        token for token in raw_output.split("\0") if token and not is_git_diagnostic_line(token)
    ]

    entries = []
    index = 0
    while index < len(raw_tokens):
        token = raw_tokens[index]
        if len(token) < 3:
            index += 1
            continue

        x_flag, y_flag = token[0], token[1]
        path = token[3:].strip()
        if not path:
            index += 1
            continue

        # En format -z, rename/copy ajoute un token avec le chemin destination.
        if (x_flag in {"R", "C"} or y_flag in {"R", "C"}) and index + 1 < len(raw_tokens):
            destination_path = raw_tokens[index + 1].strip()
            if destination_path and not is_git_diagnostic_line(destination_path):
                path = destination_path
            index += 1

        entries.append({"x": x_flag, "y": y_flag, "path": path})
        index += 1

    return entries


def has_any_working_tree_changes(cwd=None):
    return bool(get_status_porcelain_entries(cwd=cwd))


def get_unstaged_or_untracked_files(cwd=None):
    files = []
    for entry in get_status_porcelain_entries(cwd=cwd):
        x_flag = entry["x"]
        y_flag = entry["y"]
        path = entry["path"]
        if x_flag == "?" and y_flag == "?":
            files.append(path)
            continue
        if y_flag != " ":
            files.append(path)
    return _dedupe_preserve_order(files)


def has_staged_changes(cwd=None):
    for entry in get_status_porcelain_entries(cwd=cwd):
        x_flag = entry["x"]
        y_flag = entry["y"]
        if x_flag == "?" and y_flag == "?":
            continue
        if x_flag != " ":
            return True
    return False


def confirm(message):
    answer = input(f"{message} [o/N]: ").strip().lower()
    return answer in {"o", "oui", "y", "yes"}


def ensure_git_repository():
    code, output = run_command(["git", "rev-parse", "--is-inside-work-tree"])
    if code != 0 or output.lower() != "true":
        print("Erreur: ce dossier n'est pas un depot git.")
        return False
    return True


def get_current_branch():
    code, output = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if code != 0 or not output:
        raise RuntimeError("Impossible de detecter la branche courante.")
    return output


def ensure_local_enforcement(repo_root=None):
    """
    Validate local hook enforcement in free mode:
    - core.hooksPath must be .githooks
    - required hooks must exist
    """
    root = Path(repo_root) if repo_root else Path.cwd()
    code, hooks_path = run_command(["git", "config", "--get", "core.hooksPath"], cwd=str(root))
    if code != 0 or hooks_path.strip() != ".githooks":
        print("Erreur: hooks Git non actives localement.")
        print("Executez: python git-cli/install-hooks.py")
        return False

    for rel_hook in REQUIRED_HOOKS:
        hook_path = root / rel_hook
        if not hook_path.exists():
            print(f"Erreur: hook manquant: {hook_path}")
            print("Executez: python git-cli/install-hooks.py")
            return False

    config_path = root / ACCESS_CONTROL_FILE
    if not config_path.exists():
        print(f"Erreur: fichier de configuration manquant: {config_path}")
        print("Ajoutez git-cli/access_control.conf.")
        return False

    return True


def _parse_csv(value):
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _load_access_control():
    code, root_output = run_command(["git", "rev-parse", "--show-toplevel"])
    repo_root = Path(root_output.strip()) if code == 0 and root_output.strip() else Path.cwd()
    config_path = repo_root / ACCESS_CONTROL_FILE
    default_emails = ("elisee.wou@gmail.com",)
    default_branches = ("main", "develop", "prod")
    default_paths = ("terraform/", ".github/workflows/")

    if not config_path.exists():
        return default_emails, default_branches, default_paths

    entries = {}
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        entries[key.strip()] = value

    emails = _parse_csv(entries.get("GIT_MASTER_EMAILS", ",".join(default_emails)))
    branches = _parse_csv(entries.get("IDENTITY_RESTRICTED_BRANCHES", ",".join(default_branches)))
    protected_paths = _parse_csv(entries.get("PROTECTED_PATHS", ",".join(default_paths)))
    return emails, branches, protected_paths


def is_protected_path(file_path):
    normalized = file_path.replace("\\", "/")
    for protected in PROTECTED_PATHS:
        rule = protected.replace("\\", "/")
        if rule.endswith("/"):
            if normalized.startswith(rule):
                return True
        elif normalized == rule:
            return True
    return False


def get_staged_files(cwd=None):
    files = []
    for entry in get_status_porcelain_entries(cwd=cwd):
        x_flag = entry["x"]
        y_flag = entry["y"]
        if x_flag == "?" and y_flag == "?":
            continue
        if x_flag != " ":
            files.append(entry["path"])
    return _dedupe_preserve_order(files)


def get_git_identity():
    code_user, user = run_command(["git", "config", "--get", "user.name"])
    code_email, email = run_command(["git", "config", "--get", "user.email"])
    if code_user != 0 or code_email != 0 or not user or not email:
        raise RuntimeError("Impossible de lire l'identite Git locale (user.name / user.email).")
    return user.strip(), email.strip()


def ensure_protected_paths_access(staged_files=None):
    files = staged_files if staged_files is not None else get_staged_files()
    if not files:
        return True

    protected_touched = [path for path in files if is_protected_path(path)]
    if not protected_touched:
        return True

    _, email = get_git_identity()
    if email in GIT_MASTER_EMAILS:
        return True

    print("Commit refuse: vous modifiez des fichiers/dossiers proteges.")
    print(f"Email actuel: {email}")
    print("Emails autorises:")
    for allowed_email in GIT_MASTER_EMAILS:
        print(f"- {allowed_email}")
    print("Chemins proteges touches:")
    for protected_path in protected_touched:
        print(f"- {protected_path}")
    print(f"Configuration centrale: {ACCESS_CONTROL_FILE}")
    return False


GIT_MASTER_EMAILS, IDENTITY_RESTRICTED_BRANCHES, PROTECTED_PATHS = _load_access_control()
