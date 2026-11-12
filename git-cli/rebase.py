#!/usr/bin/env python3
import argparse
import sys

from git_utils import (
    ask_confirm,
    ask_input,
    ensure_git_repository,
    ensure_local_enforcement,
    print_banner,
    print_step,
    print_success,
    run_command,
    UserQuit,
)


DEFAULT_REBASE_TARGET = "origin/develop"


def run_fetch(dry_run=False):
    command = ["git", "fetch", "origin"]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code != 0:
        print("Erreur pendant git fetch origin:")
        if output:
            print(output)
        return False
    if output:
        print(output)
    return True


def run_rebase(target, dry_run=False):
    command = ["git", "rebase", target]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code != 0:
        print("Erreur pendant le rebase:")
        if output:
            print(output)
        return False
    if output:
        print(output)
    return True


def run_rebase_operation(operation_flag, dry_run=False):
    command = ["git", "rebase", operation_flag]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code != 0:
        print(f"Erreur pendant git rebase {operation_flag}:")
        if output:
            print(output)
        return False
    if output:
        print(output)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Rebase CLI: cible par defaut origin/develop."
    )
    parser.add_argument("--onto", default=DEFAULT_REBASE_TARGET, help="Reference de rebase (defaut: origin/develop).")
    parser.add_argument("--dry-run", action="store_true", help="Simule les commandes sans execution.")

    operation_group = parser.add_mutually_exclusive_group()
    operation_group.add_argument("--continue", dest="rebase_continue", action="store_true", help="Continue un rebase en cours.")
    operation_group.add_argument("--abort", dest="rebase_abort", action="store_true", help="Abandonne un rebase en cours.")
    operation_group.add_argument("--skip", dest="rebase_skip", action="store_true", help="Passe le commit en conflit pendant un rebase.")

    args = parser.parse_args()

    print_banner("Rebase")

    try:
        print_step("Preparation")
        if not ensure_git_repository():
            return 1
        if not ensure_local_enforcement():
            return 1
        print_success("Depot Git valide")

        if args.rebase_continue or args.rebase_abort or args.rebase_skip:
            print_step("Etape 1 - Pilotage rebase en cours")
            if args.rebase_continue:
                operation_flag = "--continue"
            elif args.rebase_abort:
                operation_flag = "--abort"
            else:
                operation_flag = "--skip"

            print(f"Operation demandee: git rebase {operation_flag}")
            print("Tapez q pour quitter.")
            if not ask_confirm("Confirmer l'operation"):
                print("Operation annulee par l'utilisateur.")
                return 1
            if not run_rebase_operation(operation_flag, dry_run=args.dry_run):
                return 1
            print_success(f"Operation git rebase {operation_flag} terminee")
            return 0

        print_step("Etape 1 - Fetch origin")
        if not run_fetch(dry_run=args.dry_run):
            return 1
        print_success("Fetch origin termine")

        print_step("Etape 2 - Confirmation rebase")
        print(f"Cible de rebase: {args.onto}")
        print("Commande: git rebase <cible>")
        print("Tapez q pour quitter.")
        if not ask_confirm("Confirmer le rebase"):
            print("Rebase annule par l'utilisateur.")
            return 1

        print_step("Etape 3 - Execution rebase")
        if not run_rebase(args.onto, dry_run=args.dry_run):
            return 1
        print_success("Rebase termine avec succes")
        return 0
    except UserQuit:
        print("Operation annulee par l'utilisateur.")
        return 1
    except RuntimeError as error:
        print(f"Erreur: {error}")
        return 1
    except KeyboardInterrupt:
        print("\nOperation annulee.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
