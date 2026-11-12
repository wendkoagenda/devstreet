"""
Vérifie, dans un workflow, que les variables et secrets d'une branche sont tous présents, bien classés et valides.
Le job doit déclarer `environment: <branche>` : `secrets` et `vars` contiennent alors les valeurs de cet environnement.

    SECRETS_JSON='${{ toJSON(secrets) }}' VARS_JSON='${{ toJSON(vars) }}' BRANCHE=prod \
        python -m scripts.deploy_env.verifier

Ne lit que les noms des secrets (aucune valeur n'est affichée). Les variables de déploiement (DEPLOY_*, GCP_*) sont aussi
contrôlées sur leur forme, car les workflows les utilisent dans des commandes.
Code de sortie : 0 conforme, 1 écarts, 2 entrée invalide.
"""
import os
import sys
from pathlib import Path

from scripts.deploy_env import spec as reference


def main(environ=None, repo_root=None):
    environ = os.environ if environ is None else environ
    repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    try:
        branch = reference.check_branch(environ.get('BRANCHE'))
        definitions = reference.load_spec(repo_root)
        secrets = reference.names_from_json(environ.get('SECRETS_JSON'))
        variables = reference.names_from_json(environ.get('VARS_JSON'))
        acces = reference.json_value(environ.get('VARS_JSON'), reference.gh_name('DEPLOY_ACCES', branch)) or None
    except reference.SpecError as error:
        print(f"Entrée invalide : {error}", file=sys.stderr)
        return 2

    errors = reference.check_environment(definitions, branch, secrets, variables, acces)
    for var in definitions:
        if var.source != 'deploy' or not var.applies(acces):
            continue
        value = reference.json_value(environ.get('VARS_JSON'), reference.gh_name(var.name, branch))
        problem = reference.validate_value(var.name, value) if value else None
        if problem:
            errors.append(f"{reference.gh_name(var.name, branch)} : {problem.split(' : ', 1)[-1]}")
    if errors:
        print(f"Environnement « {branch} » incomplet ({len(errors)} écart(s)) :")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Environnement « {branch} » conforme (accès : {acces}).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
