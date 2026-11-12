#!/usr/bin/env python3
import argparse
import os
import sys

from git_utils import (
    GIT_MASTER_EMAILS,
    IDENTITY_RESTRICTED_BRANCHES,
    PUSH_ENV_KEY,
    ask_confirm,
    ask_input,
    ensure_git_repository,
    ensure_local_enforcement,
    get_current_branch,
    get_git_identity,
    print_banner,
    print_step,
    print_success,
    run_command,
    UserQuit,
)


PROTECTED_BRANCHES = set(IDENTITY_RESTRICTED_BRANCHES)


def remote_branch_exists(branch):
    code, output = run_command(["git", "ls-remote", "--heads", "origin", branch])
    return code == 0 and bool(output.strip())


def commits_to_push_count(branch):
    if remote_branch_exists(branch):
        code, output = run_command(["git", "rev-list", "--count", f"origin/{branch}..HEAD"])
        if code != 0:
            raise RuntimeError("Impossible de verifier les commits a pousser.")
        return int(output), True

    return 1, False


def enforce_restricted_push_identity(branch):
    if branch not in IDENTITY_RESTRICTED_BRANCHES:
        return True

    user, email = get_git_identity()
    if email in GIT_MASTER_EMAILS:
        print_success(f"Identite autorisee pour {branch}: {user} <{email}>")
        return True

    print(f"Push refuse sur {branch}.")
    print("Email non autorise pour les branches protegees.")
    print(f"Branches concernees: {', '.join(IDENTITY_RESTRICTED_BRANCHES)}")
    print("Emails autorises:")
    for allowed_email in GIT_MASTER_EMAILS:
        print(f"- {allowed_email}")
    print(f"Identite actuelle: {user} <{email}>")
    return False


def confirm_protected_branch(branch):
    print(f"Attention: vous etes sur une branche protegee: {branch}")
    if not ask_confirm("Confirmer que vous voulez continuer"):
        print("Operation annulee.")
        return False

    typed = ask_input(f"Tapez exactement '{branch}' pour confirmer (ou q): ")
    if typed != branch:
        print("Confirmation invalide. Operation annulee.")
        return False
    print_success(f"Branche protegee confirmee: {branch}")
    return True


def git_push(branch, dry_run=False):
    command = ["git", "push", "origin", branch]
    if dry_run:
        print(f"Mode dry-run: commande simulee: {' '.join(command)}")
        print(f"Variable d'environnement requise: {PUSH_ENV_KEY}=1")
        return True

    print(f"Lancement du push: {' '.join(command)}")
    env = os.environ.copy()
    env[PUSH_ENV_KEY] = "1"
    code, output = run_command(command, env=env)
    if code != 0:
        print("Erreur pendant le push:")
        if output:
            print(output)
        return False

    if output:
        print(output)
    print("Push termine avec succes.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Push securise: controle de la branche et de l'identite avant git push."
    )
    parser.add_argument("--branch", help="Branche a pousser (par defaut: branche courante).")
    parser.add_argument("--dry-run", action="store_true", help="N'execute pas le push, affiche seulement la commande.")
    args = parser.parse_args()

    print_banner("Push")

    try:
        print_step("Preparation")
        if not ensure_git_repository():
            return 1
        if not ensure_local_enforcement():
            return 1
        print_success("Depot Git valide")

        print_step("Etape 1 - Verification branche")
        branch = args.branch or get_current_branch()
        commits_count, remote_exists = commits_to_push_count(branch)
        print_success(f"Branche detectee: {branch}")
        if not enforce_restricted_push_identity(branch):
            return 1
        if remote_exists and commits_count == 0:
            print(f"Aucun commit a pousser sur origin/{branch}.")
            return 0

        if branch in PROTECTED_BRANCHES:
            print_step("Etape 2 - Protection branche")
            if not confirm_protected_branch(branch):
                return 1

        print_step("Etape 3 - Confirmation push")
        remote_label = f"origin/{branch}" if remote_exists else "nouvelle branche distante"
        print("")
        print("Resume avant push:")
        print(f"- Branche: {branch}")
        print(f"- Cible distante: {remote_label}")
        print(f"- Commits a pousser: {commits_count if remote_exists else 'inconnu (branche non creee sur origin)'}")
        print("Tapez q pour quitter.")

        if not ask_confirm("Voulez-vous executer le push maintenant"):
            print("Push annule par l'utilisateur.")
            return 1
        if not git_push(branch, dry_run=args.dry_run):
            return 1
        print_success("Processus push termine")

        return 0
    except RuntimeError as error:
        print(f"Erreur: {error}")
        return 1
    except UserQuit:
        print("Operation annulee par l'utilisateur.")
        return 1
    except KeyboardInterrupt:
        print("\nOperation annulee.")
        return 1


if __name__ == "__main__":
    sys.exit(main())