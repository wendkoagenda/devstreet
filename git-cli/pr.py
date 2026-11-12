#!/usr/bin/env python3
import argparse

from git_utils import (
    PR_MARKER,
    ask_confirm,
    ask_input,
    ensure_git_repository,
    ensure_local_enforcement,
    get_current_branch,
    print_banner,
    print_step,
    print_success,
    run_command,
    UserQuit,
)


PROTECTED_SOURCE_BRANCHES = set()
MAX_PR_TITLE_LENGTH = 500
PR_TYPES = [
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


def ensure_gh_available():
    code, output = run_command(["gh", "--version"])
    if code != 0:
        print("Erreur: gh CLI n'est pas installe ou inaccessible.")
        return False
    if output:
        first_line = output.splitlines()[0]
        print(f"gh detecte: {first_line}")
    return True


def ensure_gh_authenticated():
    code, output = run_command(["gh", "auth", "status"])
    if code != 0:
        print("Erreur: gh CLI n'est pas authentifie.")
        if output:
            print(output)
        print("Connectez-vous avec: gh auth login")
        return False
    return True


def remote_branch_exists(branch):
    code, output = run_command(["git", "ls-remote", "--heads", "origin", branch])
    return code == 0 and bool(output.strip())


def fetch_origin_refs(dry_run=False):
    command = ["git", "fetch", "origin"]
    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True
    code, output = run_command(command)
    if code != 0:
        print("Erreur pendant la synchronisation des references distantes:")
        if output:
            print(output)
        return False
    return True


def local_commits_not_on_remote(branch):
    code, output = run_command(["git", "rev-list", "--count", f"origin/{branch}..{branch}"])
    if code != 0:
        raise RuntimeError("Impossible de verifier les commits locaux non pushes.")
    return int(output.strip() or "0")


def has_commits_for_pr(source_branch, target_branch):
    code, output = run_command(
        ["git", "rev-list", "--count", f"origin/{target_branch}..origin/{source_branch}"]
    )
    if code != 0:
        raise RuntimeError("Impossible de verifier les commits entre la source et la cible.")
    commits_count = int(output.strip() or "0")
    return commits_count > 0, commits_count


def choose_target_branch(source_branch, default_base=None):
    if default_base:
        print_success(f"Branche cible forcee: {default_base}")
        return default_base

    print_step("Etape 3 - Branche cible")
    print("Choisissez la branche cible de la pull request :")
    if source_branch == "develop":
        default_target = "main"
    elif source_branch == "main":
        default_target = "prod"
    else:
        default_target = "develop"
    print(f"1. {default_target}")
    print("2. autre")
    print("Tapez q pour quitter.")
    choice = ask_input("Votre choix (1/2/q): ")
    if choice == "1":
        print_success(f"Branche cible selectionnee: {default_target}")
        return default_target
    if choice == "2":
        custom = ask_input("Nom de la branche cible (ou q): ")
        if custom:
            print_success(f"Branche cible selectionnee: {custom}")
            return custom
    print(f"Choix invalide, {default_target} sera utilise par defaut.")
    print_success(f"Branche cible selectionnee: {default_target}")
    return default_target


def validate_branch_flow(source_branch, target_branch):
    if source_branch in PROTECTED_SOURCE_BRANCHES:
        print(f"Erreur: impossible de creer une PR depuis la branche {source_branch}.")
        print("Creez une branche feature/hotfix puis relancez la commande.")
        return False

    if source_branch == "develop" and target_branch != "main":
        print(
            "Erreur: une PR depuis develop est autorisee uniquement "
            "vers la branche main."
        )
        print("Selectionnez main comme branche cible puis relancez la commande.")
        return False

    if source_branch == "main" and target_branch != "prod":
        print(
            "Erreur: une PR depuis main est autorisee uniquement "
            "vers la branche prod."
        )
        print("Selectionnez prod comme branche cible puis relancez la commande.")
        return False

    return True


def _get_recent_commits_for_pr(target_branch):
    code, output = run_command(
        ["git", "log", "--oneline", f"origin/{target_branch}..HEAD", "-n", "5"]
    )
    if code == 0 and output.strip():
        return "Rappel - commits inclus dans cette PR (max 5):", output.strip()

    code, output = run_command(["git", "log", "--oneline", "-n", "5"])
    if code == 0 and output.strip():
        return "Rappel - 5 derniers commits:", output.strip()

    return None, None


def ask_pr_type():
    print("Choisissez le type de PR :")
    for index, pr_type in enumerate(PR_TYPES, start=1):
        print(f"{index}. {pr_type}")
    print("Tapez q pour quitter.")

    while True:
        raw = ask_input("Votre choix (numero/q): ")
        if not raw.isdigit():
            print("Veuillez saisir un numero valide.")
            continue
        index = int(raw)
        if 1 <= index <= len(PR_TYPES):
            selected_type = PR_TYPES[index - 1]
            print_success(f"Type selectionne: {selected_type}")
            return selected_type
        print("Choix hors plage.")


def ask_pr_title(target_branch):
    print_step("Etape 4 - Titre")
    print(f"Longueur maximale du titre: {MAX_PR_TITLE_LENGTH} caracteres.")
    commits_label, commits_output = _get_recent_commits_for_pr(target_branch)
    if commits_label and commits_output:
        print(commits_label)
        print(commits_output)

    pr_type = ask_pr_type()

    while True:
        scope = ask_input("Scope de la PR (ex: cli, auth, api, ou q): ").lower()
        if not scope:
            print("Le scope est obligatoire.")
            continue
        break
    print_success(f"Scope valide: {scope}")

    prefix = f"pr-{pr_type}({scope}): "
    max_description_length = MAX_PR_TITLE_LENGTH - len(prefix)
    if max_description_length <= 0:
        raise RuntimeError("Impossible de construire un titre PR valide avec ce scope.")

    print(f"Prefixe applique: {prefix}")
    print(f"Longueur maximale restante pour le titre: {max_description_length} caracteres.")

    while True:
        value = ask_input("Titre de la PR (sans prefixe, ou q): ")
        if not value:
            print("Le titre est obligatoire.")
            continue
        if len(value) > max_description_length:
            print(
                "Le titre depasse la limite de "
                f"{len(value) - max_description_length} caracteres."
            )
            continue
        final_title = f"{prefix}{value}"
        print_success("Titre valide")
        return final_title


def ask_pr_body():
    print_step("Etape 5 - Description")
    print("Description de la PR (multiligne).")
    print("Terminez la saisie avec une ligne contenant uniquement un point.")
    print("Tapez q seul sur une ligne pour quitter.")
    lines = []
    while True:
        line = input()
        if line.strip().lower() in {"q", "quit", "exit"}:
            raise UserQuit()
        if line.strip() == ".":
            break
        lines.append(line)
    body = "\n".join(lines).strip()
    final_body = body or "Aucune description fournie."
    if PR_MARKER not in final_body:
        final_body = f"{final_body}\n\n{PR_MARKER}"
    print_success("Description validee")
    return final_body


def push_branch_if_needed(branch, dry_run=False):
    if not remote_branch_exists(branch):
        print(f"La branche {branch} n'existe pas encore sur origin.")
        if not ask_confirm("Voulez-vous pousser la branche maintenant"):
            print("Creation de PR annulee (branche non poussee).")
            return False
        command = ["git", "push", "-u", "origin", branch]
    else:
        ahead_count = local_commits_not_on_remote(branch)
        if ahead_count == 0:
            print_success(f"Branche distante deja presente et a jour: origin/{branch}")
            return True
        print(
            f"{ahead_count} commit(s) local(aux) non pousse(s) detecte(s) "
            f"sur {branch}."
        )
        if not ask_confirm("Voulez-vous pousser ces commits maintenant"):
            print("Creation de PR annulee (commits locaux non pousses).")
            return False
        command = ["git", "push", "origin", branch]

    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True

    code, output = run_command(command)
    if code != 0:
        print("Erreur pendant le push de la branche :")
        if output:
            print(output)
        return False
    if output:
        print(output)
    print_success(f"Branche synchronisee: {branch}")
    return True


def create_pr(source_branch, target_branch, title, body, draft=False, dry_run=False):
    command = [
        "gh",
        "pr",
        "create",
        "--base",
        target_branch,
        "--head",
        source_branch,
        "--title",
        title,
        "--body",
        body,
    ]
    if draft:
        command.append("--draft")

    if dry_run:
        print(f"Mode dry-run: {' '.join(command)}")
        return True

    code, output = run_command(command)
    if code != 0:
        print("Erreur pendant la creation de la pull request :")
        if output:
            print(output)
        return False

    if output:
        print("Pull request creee :")
        print(output)
    print_success("Pull request creee")
    return True


def main():
    parser = argparse.ArgumentParser(description="Creation interactive de pull request avec gh CLI.")
    parser.add_argument("--draft", action="store_true", help="Cree une pull request en brouillon.")
    parser.add_argument("--dry-run", action="store_true", help="Simule la commande sans execution.")
    parser.add_argument("--base", help="Branche cible de la PR (sinon question interactive).")
    args = parser.parse_args()

    print_banner("Pull Request")

    try:
        print_step("Preparation")
        if not ensure_git_repository():
            return 1
        if not ensure_local_enforcement():
            return 1
        print_success("Depot Git valide")

        print_step("Etape 1 - Verifications GH")
        if not ensure_gh_available():
            return 1
        print_success("GH CLI detecte")

        if not args.dry_run and not ensure_gh_authenticated():
            return 1
        if args.dry_run:
            print_success("Authentification GH ignoree (--dry-run)")
        else:
            print_success("GH authentifie")

        print_step("Etape 2 - Branche source")
        source_branch = get_current_branch()
        print_success(f"Branche source: {source_branch}")

        target_branch = choose_target_branch(source_branch, args.base)
        if not validate_branch_flow(source_branch, target_branch):
            return 1
        title = ask_pr_title(target_branch)
        body = ask_pr_body()

        print_step("Etape 6 - Apercu")
        print("Apercu de la pull request :")
        print(f"- Source: {source_branch}")
        print(f"- Cible: {target_branch}")
        print(f"- Titre: {title}")
        print(f"- Draft: {'oui' if args.draft else 'non'}")
        print("Description:")
        print(body)
        print_success("Apercu genere")

        if not ask_confirm("Confirmer la creation de la pull request"):
            print("Creation de pull request annulee.")
            return 1

        print_step("Etape 7 - Synchronisation branche")
        if not push_branch_if_needed(source_branch, dry_run=args.dry_run):
            return 1

        print_step("Etape 8 - Creation PR")
        if not fetch_origin_refs(dry_run=args.dry_run):
            return 1
        has_commits, commits_count = has_commits_for_pr(source_branch, target_branch)
        if not has_commits:
            print(
                "Creation de PR refusee: aucun commit detecte entre "
                f"{target_branch} et {source_branch}."
            )
            print("Action requise: ajoutez au moins un commit sur la branche source.")
            return 1
        print_success(f"Commits detectes pour la PR: {commits_count}")

        if not create_pr(
            source_branch=source_branch,
            target_branch=target_branch,
            title=title,
            body=body,
            draft=args.draft,
            dry_run=args.dry_run,
        ):
            return 1

        print_success("Processus PR termine")
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
    raise SystemExit(main())
