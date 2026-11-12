#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from git_utils import (
    ask_confirm,
    ask_input,
    ensure_git_repository,
    has_any_working_tree_changes,
    ensure_local_enforcement,
    get_current_branch,
    is_git_diagnostic_line,
    print_banner,
    print_step,
    print_success,
    run_command,
    UserQuit,
)


TARGET_BRANCH = "develop"


def ensure_clean_working_tree():
    if has_any_working_tree_changes():
        print("Merge refuse: changements locaux detectes (staged/unstaged/untracked).")
        print("Action requise: committez ou stash vos changements avant le merge.")
        return False
    return True


def branch_exists_locally(branch):
    code, _ = run_command(["git", "show-ref", "--verify", f"refs/heads/{branch}"])
    return code == 0


def fetch_source_branch(source_branch, dry_run=False):
    command = ["git", "fetch", "origin", f"{source_branch}:{source_branch}"]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code != 0:
        print(f"Erreur pendant la recuperation de la branche '{source_branch}' depuis origin:")
        if output:
            print(output)
        return False
    if output:
        print(output)
    return True


def fetch_origin_branch(branch, dry_run=False):
    command = ["git", "fetch", "origin", branch]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code != 0:
        print(f"Erreur pendant la recuperation de la branche '{branch}' depuis origin:")
        if output:
            print(output)
        return False
    if output:
        print(output)
    return True


def ensure_source_branch_available(source_branch, dry_run=False):
    if branch_exists_locally(source_branch):
        return True

    print(f"Branche source '{source_branch}' absente en local. Tentative de recuperation depuis origin...")
    if not fetch_source_branch(source_branch, dry_run=dry_run):
        return False
    if dry_run:
        return True
    return branch_exists_locally(source_branch)


def get_repo_root():
    code, output = run_command(["git", "rev-parse", "--show-toplevel"])
    if code != 0 or not output:
        raise RuntimeError("Impossible de detecter la racine du depot Git.")
    return Path(output.strip())


def is_merge_in_progress(repo_root):
    return (repo_root / ".git" / "MERGE_HEAD").exists()


def unresolved_conflicts():
    code, output = run_command(["git", "diff", "--name-only", "--diff-filter=U"])
    if code != 0:
        raise RuntimeError("Impossible de verifier les conflits non resolus.")
    return [
        line.strip()
        for line in output.splitlines()
        if line.strip() and not is_git_diagnostic_line(line)
    ]


def finalize_merge_commit(dry_run=False):
    command = ["git", "commit", "--no-edit"]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code != 0:
        print("Erreur pendant la finalisation du merge:")
        if output:
            print(output)
        return False
    if output:
        print(output)
    return True


def abort_merge(dry_run=False):
    command = ["git", "merge", "--abort"]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code != 0:
        print("Erreur pendant l'abandon du merge:")
        if output:
            print(output)
        return False
    if output:
        print(output)
    return True


def continue_merge(repo_root, dry_run=False):
    if not is_merge_in_progress(repo_root):
        print("Aucun merge en cours a continuer.")
        return False

    conflicts = unresolved_conflicts()
    if conflicts:
        print("Impossible de continuer: des conflits restent non resolus.")
        for file_path in conflicts:
            print(f"- {file_path}")
        return False

    return finalize_merge_commit(dry_run=dry_run)


def run_merge(source_branch, dry_run=False):
    command = ["git", "merge", source_branch]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code == 0:
        if output:
            print(output)
        return True

    if output:
        print(output)
    return False


def run_merge_ref(ref_name, dry_run=False):
    command = ["git", "merge", ref_name]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code == 0:
        if output:
            print(output)
        return True

    if output:
        print(output)
    return False


def print_conflict_guidance():
    print("")
    print("Conflits detectes.")
    print("1) Resolvez les fichiers en conflit dans votre editeur")
    print("2) git add <fichiers>")
    print("3) Choisissez une option:")
    print("   - python git-cli/merge.py --continue")
    print("   - python git-cli/merge.py --abort")


def conflict_assistant_loop(repo_root, dry_run=False):
    print_step("Assistant conflit")
    print("Le merge est en pause. Vous pouvez rester dans ce menu.")

    while True:
        print("")
        print("Options:")
        print("1. Re-verifier le merge (git status + conflits)")
        print("2. Continuer le merge")
        print("3. Abandonner le merge")
        print("q. Quitter le CLI (sans casser l'etat merge)")
        choice = ask_input("Votre choix (1/2/3/q): ")

        if choice == "1":
            code, output = run_command(["git", "status"])
            if code == 0 and output:
                print(output)
            else:
                print("Impossible d'afficher git status.")
            conflicts = unresolved_conflicts()
            if conflicts:
                print("Conflits toujours presents:")
                for file_path in conflicts:
                    print(f"- {file_path}")
            else:
                print_success("Tous les conflits semblent resolus")
            continue

        if choice == "2":
            if continue_merge(repo_root, dry_run=dry_run):
                print_success("Merge finalise avec succes")
                return 0
            print("Le merge ne peut pas etre finalise pour le moment.")
            continue

        if choice == "3":
            if abort_merge(dry_run=dry_run):
                print_success("Merge abandonne")
                return 0
            print("Echec de l'abandon du merge.")
            continue

        print("Choix invalide.")


def main():
    parser = argparse.ArgumentParser(
        description="Merge CLI vers develop avec reprise de conflit."
    )
    parser.add_argument("--from", dest="source_branch", help="Branche source a merger vers develop.")
    parser.add_argument("--continue", dest="merge_continue", action="store_true", help="Continue un merge en cours.")
    parser.add_argument("--abort", dest="merge_abort", action="store_true", help="Abandonne un merge en cours.")
    parser.add_argument(
        "--sync-pr-head",
        dest="sync_pr_head",
        action="store_true",
        help="Met a jour la branche courante (head PR) en mergeant origin/<base> dedans.",
    )
    parser.add_argument(
        "--base",
        default=TARGET_BRANCH,
        help="Branche base pour --sync-pr-head (defaut: develop).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simule les commandes sans execution.")
    args = parser.parse_args()

    print_banner("Merge")

    try:
        mode_flags = [
            bool(args.source_branch),
            bool(args.merge_continue),
            bool(args.merge_abort),
            bool(args.sync_pr_head),
        ]
        if sum(mode_flags) != 1:
            print(
                "Usage invalide: indiquez exactement un mode parmi "
                "--from / --continue / --abort / --sync-pr-head."
            )
            return 1

        print_step("Preparation")
        if not ensure_git_repository():
            return 1
        if not ensure_local_enforcement():
            return 1
        repo_root = get_repo_root()
        print_success("Depot Git valide")

        if args.merge_continue:
            print_step("Etape Continue")
            if not continue_merge(repo_root, dry_run=args.dry_run):
                return 1
            print_success("Merge continue termine")
            return 0

        if args.merge_abort:
            print_step("Etape Abort")
            if not is_merge_in_progress(repo_root):
                print("Aucun merge en cours a annuler.")
                return 1
            if not abort_merge(dry_run=args.dry_run):
                return 1
            print_success("Merge annule")
            return 0

        if args.sync_pr_head:
            base_branch = args.base.strip()
            print_step("Etape Sync PR Head - Validations")
            current_branch = get_current_branch()
            if not base_branch:
                print("Merge refuse: la branche base est obligatoire.")
                return 1
            if current_branch == base_branch:
                print("Merge refuse: la branche courante (head) ne peut pas etre la base.")
                print(f"Branche courante/base: {current_branch}")
                return 1
            if not ensure_clean_working_tree():
                return 1
            if not fetch_origin_branch(base_branch, dry_run=args.dry_run):
                return 1
            print_success("Validations OK")

            print_step("Etape Sync PR Head - Confirmation")
            print(f"Head PR (courante): {current_branch}")
            print(f"Base PR: {base_branch}")
            print(f"Action: merge origin/{base_branch} -> {current_branch}")
            print("Tapez q pour quitter.")
            if not ask_confirm("Confirmer la synchronisation de la branche head PR"):
                print("Synchronisation annulee par l'utilisateur.")
                return 1

            print_step("Etape Sync PR Head - Execution")
            if run_merge_ref(f"origin/{base_branch}", dry_run=args.dry_run):
                print_success("Synchronisation head PR terminee avec succes")
                return 0

            if not is_merge_in_progress(repo_root):
                print("Echec de la synchronisation (hors conflit).")
                return 1

            print_conflict_guidance()
            return conflict_assistant_loop(repo_root, dry_run=args.dry_run)

        source_branch = args.source_branch
        print_step("Etape 1 - Validations")
        current_branch = get_current_branch()
        if current_branch != TARGET_BRANCH:
            print(f"Merge refuse: vous devez etre sur {TARGET_BRANCH}.")
            print(f"Branche actuelle: {current_branch}")
            return 1
        if source_branch == TARGET_BRANCH:
            print("Merge refuse: la branche source ne peut pas etre develop.")
            return 1
        if not ensure_source_branch_available(source_branch, dry_run=args.dry_run):
            print(f"Merge refuse: impossible de recuperer la branche source '{source_branch}'.")
            return 1
        if not ensure_clean_working_tree():
            return 1
        print_success("Validations OK")

        print_step("Etape 2 - Confirmation")
        print(f"Cible: {TARGET_BRANCH}")
        print(f"Source: {source_branch}")
        print("Tapez q pour quitter.")
        if not ask_confirm("Confirmer le lancement du merge"):
            print("Merge annule par l'utilisateur.")
            return 1

        print_step("Etape 3 - Execution merge")
        if run_merge(source_branch, dry_run=args.dry_run):
            print_success("Merge termine avec succes")
            return 0

        if not is_merge_in_progress(repo_root):
            print("Echec du merge (hors conflit).")
            return 1

        print_conflict_guidance()
        return conflict_assistant_loop(repo_root, dry_run=args.dry_run)
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
