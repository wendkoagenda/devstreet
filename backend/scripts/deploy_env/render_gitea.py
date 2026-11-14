"""
Prépare le fichier Gitea pour le job CD - GITEA SSH.

    BRANCHE=prod SECRETS_JSON='...' VARS_JSON='...' \
        python -m scripts.deploy_env.render_gitea --sortie DOSSIER

Écrit (droits 600) gitea.env : GITEA_DOMAIN, GITEA_DB_PASSWORD, GITEA_ADMIN_USER, GITEA_ADMIN_PASSWORD, GITEA_ADMIN_EMAIL.

N'affiche jamais une valeur. Code de sortie : 0 écrit, 1 valeurs invalides, 2 entrée invalide.
"""
import argparse
import os
import sys
from pathlib import Path

from scripts.deploy_env import spec as reference

NAMES = ('GITEA_DOMAIN', 'GITEA_DB_PASSWORD', 'GITEA_ADMIN_USER', 'GITEA_ADMIN_PASSWORD', 'GITEA_ADMIN_EMAIL')


def _quote(name, value):
    if any(char in value for char in ("'", '\n', '\r')):
        raise reference.SpecError(f"{name} : la valeur ne doit contenir ni apostrophe ni retour à la ligne.")
    return f"{name}='{value}'"


def render_gitea(branch, values):
    """Retourne ({fichier: contenu}, [erreurs])."""
    values = {name.upper(): value for name, value in values.items()}
    errors = []
    found = {}
    for name in NAMES:
        value = values.get(reference.gh_name(name, branch), '')
        if not value:
            errors.append(f"{name} : manquant.")
            continue
        problem = reference.validate_value(name, value)
        if problem:
            errors.append(problem)
        else:
            found[name] = value
    if errors:
        return {}, errors
    try:
        content = '\n'.join(_quote(name, found[name]) for name in NAMES) + '\n'
    except reference.SpecError as error:
        return {}, [str(error)]
    return {'gitea.env': content}, []


def _write_private(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(content)


def main(argv=None, environ=None, repo_root=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument('--sortie', required=True, help='dossier où écrire gitea.env')
    args = parser.parse_args(argv)
    environ = os.environ if environ is None else environ
    repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    try:
        branch = reference.check_branch(environ.get('BRANCHE'))
        reference.load_spec(repo_root)
        secrets = reference.json_map(environ.get('SECRETS_JSON'))
        variables = reference.json_map(environ.get('VARS_JSON'))
        values = {**variables, **secrets}
    except reference.SpecError as error:
        print(f"Entrée invalide : {error}", file=sys.stderr)
        return 2

    files, errors = render_gitea(branch, values)
    if errors:
        print(f"Gitea « {branch} » inutilisable ({len(errors)} écart(s)) :")
        for error in errors:
            print(f"  - {error}")
        return 1
    output = Path(args.sortie)
    output.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        _write_private(output / name, content)
    print(f"Écrit dans {output} : {', '.join(files)} (valeurs non affichées).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
