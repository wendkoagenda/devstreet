#!/usr/bin/env python3
import argparse

from git_utils import (
    COMMIT_TRAILER,
    ask_input,
    ask_confirm,
    ask_non_empty,
    ensure_git_repository,
    ensure_local_enforcement,
    ensure_protected_paths_access,
    get_status_porcelain_entries,
    get_unstaged_or_untracked_files,
    has_staged_changes,
    print_step,
    print_success,
    print_banner,
    run_command,
    UserQuit,
)
from check_zones import run_zones_audit
from quality_checks import run_quality_checks


COMMIT_TYPES = [
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "chore",
    "ci",
    "revert",
]

DEFAULT_DESCRIPTION_MAX = 100


def stage_selected_files(files, dry_run=False):
    if not files:
        return
    for file_path in files:
        if dry_run:
            print(f"Mode dry-run: git add {file_path}")
            continue
        code, output = run_command(["git", "add", file_path])
        if code != 0:
            raise RuntimeError(f"Echec de git add {file_path}: {output}")


def ask_commit_type():
    print_step("Etape 1 - Type de commit")
    print("Choisissez le type de commit :")
    print("Tapez q pour quitter.")
    for index, commit_type in enumerate(COMMIT_TYPES, start=1):
        print(f"{index}. {commit_type}")

    while True:
        raw = ask_input("Votre choix (numero, q=quitter): ")
        if not raw.isdigit():
            print("Veuillez saisir un numero valide.")
            continue
        index = int(raw)
        if 1 <= index <= len(COMMIT_TYPES):
            selected_type = COMMIT_TYPES[index - 1]
            print_success(f"Type selectionne: {selected_type}")
            return selected_type
        print("Choix hors plage.")


def ask_description(max_length):
    print_step("Etape 3 - Description")
    print(
        "La limite de longueur vient de la convention de commit du projet "
        f"(recommandation), pas d'une regle Git stricte. Maximum: {max_length} caracteres."
    )
    print("Tapez q pour quitter.")

    while True:
        description = ask_non_empty("Description du commit (q=quitter): ")
        used = len(description)
        remaining = max_length - used
        print(
            f"Caracteres utilises: {used}/{max_length} | "
            f"restants: {remaining if remaining >= 0 else 0}"
        )
        if description.endswith("."):
            print("Ne terminez pas la description par un point.")
            continue
        if used > max_length:
            print(f"La description depasse la limite de {used - max_length} caracteres.")
            continue
        print_success("Description validee")
        return description


def main():
    parser = argparse.ArgumentParser(
        description="Commit interactif avec format type(scope): description."
    )
    parser.add_argument("--dry-run", action="store_true", help="Simule le commit sans l'executer.")
    parser.add_argument(
        "--max-description",
        type=int,
        default=DEFAULT_DESCRIPTION_MAX,
        help="Longueur maximale de la description (defaut: 100).",
    )
    args = parser.parse_args()

    print_banner("Commit")

    try:
        if not ensure_git_repository():
            return 1
        if not ensure_local_enforcement():
            return 1

        status_entries = get_status_porcelain_entries()
        if not status_entries:
            print("Aucun changement detecte. Rien a commiter.")
            return 0

        print_step("Preparation")
        print("Statut git actuel :")
        code, status_output = run_command(["git", "status", "--short"])
        if code == 0 and status_output:
            print(status_output)
        print_success("Preparation terminee")

        # Controles avant tout staging : echec = pas de git add.
        if not run_quality_checks():
            return 1
        # Audit zones : avertissement seulement (la CI non-regression bloque les orphelins).
        run_zones_audit(warn_only=True)

        unstaged_files = get_unstaged_or_untracked_files()
        if unstaged_files:
            print_step("Etape 0 - Staging")
            print("Fichiers non stages detectes :")
            for index, file_path in enumerate(unstaged_files, start=1):
                print(f"{index}. {file_path}")

            print("")
            print("Options de staging :")
            print("1. Ajouter tous les fichiers ci-dessus")
            print("2. Choisir les fichiers a ajouter")
            print("3. Ne rien ajouter")
            print("q. Quitter")
            stage_choice = ask_non_empty("Votre choix (1/2/3/q): ")

            if stage_choice == "1":
                stage_selected_files(unstaged_files, dry_run=args.dry_run)
                print_success("Staging termine (option 1)")
            elif stage_choice == "2":
                selected = ask_non_empty("Numeros separes par virgule (ex: 1,3) ou q: ")
                selected_indexes = []
                for chunk in selected.split(","):
                    chunk = chunk.strip()
                    if chunk.isdigit():
                        idx = int(chunk)
                        if 1 <= idx <= len(unstaged_files):
                            selected_indexes.append(idx - 1)
                selected_files = [unstaged_files[i] for i in sorted(set(selected_indexes))]
                if selected_files:
                    stage_selected_files(selected_files, dry_run=args.dry_run)
                    print_success("Staging termine (selection)")
                else:
                    print("Aucun fichier valide selectionne.")
            elif stage_choice == "3":
                print_success("Aucun fichier ajoute (option 3)")
            else:
                print("Choix invalide, aucun fichier ajoute.")

        # Recalculer l'etat apres l'etape de staging.
        has_staged = has_staged_changes()
        if not has_staged and not args.dry_run:
            print("Aucun fichier stage. Impossible de creer un commit.")
            return 1
        if not ensure_protected_paths_access():
            return 1

        commit_type = ask_commit_type()
        print_step("Etape 2 - Scope")
        print("Tapez q pour quitter.")
        scope = ask_non_empty("Scope (ex: crm, production, settings, q=quitter): ").lower()
        print_success(f"Scope valide: {scope}")
        description = ask_description(args.max_description)

        commit_message = f"{commit_type}({scope}): {description}"
        print_step("Apercu")
        print("Message de commit propose :")
        print(commit_message)
        print("Trailer ajoute automatiquement :")
        print(COMMIT_TRAILER)
        print_success("Apercu genere")

        if not ask_confirm("Confirmer le commit"):
            print("Commit annule.")
            return 1

        if args.dry_run:
            print(
                "Mode dry-run: git commit "
                f"-m \"{commit_message}\" -m \"{COMMIT_TRAILER}\""
            )
            print_success("Simulation terminee")
            return 0

        code, output = run_command(
            ["git", "commit", "-m", commit_message, "-m", COMMIT_TRAILER]
        )
        if code != 0:
            print("Erreur pendant le commit :")
            if output:
                print(output)
            return 1

        if output:
            print(output)
        print_success("Commit cree avec succes")
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
    raise SystemExit(main())
