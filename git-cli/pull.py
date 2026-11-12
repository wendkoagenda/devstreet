#!/usr/bin/env python3
import argparse
import sys

from git_utils import (
    ask_confirm,
    ask_input,
    ensure_git_repository,
    has_any_working_tree_changes,
    ensure_local_enforcement,
    get_current_branch,
    print_banner,
    print_step,
    print_success,
    run_command,
    UserQuit,
)


def ensure_clean_working_tree():
    if has_any_working_tree_changes():
        print("Pull refuse: changements locaux detectes (staged/unstaged/untracked).")
        print("Action requise: committez ou stash vos changements avant le pull.")
        return False
    return True


def remote_branch_exists(branch):
    code, output = run_command(["git", "ls-remote", "--heads", "origin", branch])
    return code == 0 and bool(output.strip())


def ensure_no_unpushed_commits(branch):
    if not remote_branch_exists(branch):
        print(f"Pull refuse: la branche distante origin/{branch} n'existe pas.")
        print("Action requise: poussez d'abord la branche locale avec git-cli/push.py.")
        return False

    code, output = run_command(["git", "rev-list", "--count", f"origin/{branch}..HEAD"])
    if code != 0:
        raise RuntimeError("Impossible de verifier les commits locaux non pushes.")
    ahead_count = int(output.strip() or "0")
    if ahead_count > 0:
        print(f"Pull refuse: {ahead_count} commit(s) local(aux) non pousse(s) detecte(s).")
        print("Action requise: poussez d'abord vos commits avec git-cli/push.py.")
        return False
    return True


def pull_branch(branch, dry_run=False):
    command = ["git", "pull", "--rebase", "origin", branch]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True

    code, output = run_command(command)
    if code != 0:
        print("Erreur pendant le pull --rebase:")
        if output:
            print(output)
        return False
    if output:
        print(output)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Pull strict: branche courante uniquement, working tree propre, zero commit non pousse."
    )
    parser.add_argument("--dry-run", action="store_true", help="Simule les verifications et la commande pull.")
    args = parser.parse_args()

    print_banner("Pull")

    try:
        print_step("Preparation")
        if not ensure_git_repository():
            return 1
        if not ensure_local_enforcement():
            return 1
        print_success("Depot Git valide")

        print_step("Etape 1 - Branche courante")
        branch = get_current_branch()
        print_success(f"Branche detectee: {branch}")

        print_step("Etape 2 - Verification working tree")
        if not ensure_clean_working_tree():
            return 1
        print_success("Aucun changement local detecte")

        print_step("Etape 3 - Verification commits non pushes")
        if not ensure_no_unpushed_commits(branch):
            return 1
        print_success("Aucun commit local non pousse")

        print_step("Etape 4 - Confirmation")
        print("Pull strict cible toujours la meme branche locale/distante.")
        print(f"Commande: git pull --rebase origin {branch}")
        print("Tapez q pour quitter.")
        if not ask_confirm("Voulez-vous lancer le pull maintenant"):
            print("Pull annule par l'utilisateur.")
            return 1

        print_step("Etape 5 - Execution pull")
        if not pull_branch(branch, dry_run=args.dry_run):
            return 1
        print_success("Pull termine avec succes")
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
