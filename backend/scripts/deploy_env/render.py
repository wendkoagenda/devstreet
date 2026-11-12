"""
Prépare, dans un workflow de déploiement, les fichiers d'environnement d'une branche pour la VM.

    BRANCHE=prod SECRETS_JSON='${{ toJSON(secrets) }}' VARS_JSON='${{ toJSON(vars) }}' \
    BACKEND_IMAGE=ghcr.io/... FRONTEND_IMAGE=ghcr.io/... DEPLOY_SHA=<40 hex> \
        python -m scripts.deploy_env.render --sortie DOSSIER

Écrit (droits 600) :
- backend.env : les variables de backend/.env.example, une valeur entre apostrophes par ligne ;
- compose.env : réglages du namespace (images, domaine, base) lus par docker compose et par deployer.sh.

N'affiche jamais une valeur. Code de sortie : 0 écrit, 1 valeurs invalides ou manquantes, 2 entrée invalide.
"""
import argparse
import os
import re
import sys
from pathlib import Path

from scripts.deploy_env import spec as reference

_IMAGE = re.compile(r'^ghcr\.io/[a-z0-9._/-]+:[A-Za-z0-9_.-]+$')
_SHA = re.compile(r'^[0-9a-f]{40}$')
_COMPOSE_FROM_BACKEND = ('DB_NAME', 'DB_USER', 'DB_PASSWORD')


def _quote(name, value):
    """Valeur entre apostrophes (littérale pour docker compose et pour sh). Les apostrophes et fins de ligne sont refusées."""
    if any(char in value for char in ("'", '\n', '\r')):
        raise reference.SpecError(f"{name} : la valeur ne doit contenir ni apostrophe ni retour à la ligne.")
    return f"{name}='{value}'"


def host_allowed(domain, allowed_hosts):
    """Même règle que Django : nom exact, `.exemple.fr` (domaine et sous-domaines) ou `*`."""
    for host in (item.strip() for item in allowed_hosts.split(',')):
        if host == '*' or host == domain:
            return True
        if host.startswith('.') and (domain == host[1:] or domain.endswith(host)):
            return True
    return False


def render(definitions, branch, secrets, variables, images, sha):
    """Retourne ({fichier: contenu}, [erreurs]). `secrets` et `variables` : {nom GitHub: valeur}."""
    secrets = {name.upper(): value for name, value in secrets.items()}
    variables = {name.upper(): value for name, value in variables.items()}
    errors = []

    def value_of(var):
        store = secrets if var.secret else variables
        return store.get(reference.gh_name(var.name, branch), '')

    acces = variables.get(reference.gh_name('DEPLOY_ACCES', branch))
    backend, deploy = {}, {}
    for var in definitions:
        if var.source not in ('backend', 'deploy') or (var.acces and not var.applies(acces)):
            continue
        value = value_of(var)
        if not value:
            if var.required:
                errors.append(f"{reference.gh_name(var.name, branch)} : manquant.")
            continue
        problem = reference.validate_value(var.name, value) if var.source == 'deploy' else None
        if problem:
            errors.append(problem)
        (backend if var.source == 'backend' else deploy)[var.name] = value
    if errors:
        return {}, errors

    if deploy['DEPLOY_DB_MODE'] == 'interne' and backend['DB_HOST'] != 'db':
        errors.append("DB_HOST doit valoir « db » quand DEPLOY_DB_MODE=interne (la base est le service db du namespace).")
    if not host_allowed(deploy['DEPLOY_DOMAIN'], backend['ALLOWED_HOSTS']):
        errors.append("ALLOWED_HOSTS ne contient pas DEPLOY_DOMAIN : Django refuserait les requêtes du proxy et le contrôle de santé.")
    if not _IMAGE.match(images['BACKEND_IMAGE']) or not _IMAGE.match(images['FRONTEND_IMAGE']):
        errors.append("Références d'images invalides (attendu ghcr.io/<chemin>:<tag>).")
    if not _SHA.match(sha):
        errors.append("DEPLOY_SHA doit être un commit complet de 40 caractères hexadécimaux.")
    if errors:
        return {}, errors

    compose = {
        'DEPLOY_NAMESPACE': deploy['DEPLOY_NAMESPACE'],
        'DEPLOY_DOMAIN': deploy['DEPLOY_DOMAIN'],
        'DEPLOY_LETSENCRYPT_EMAIL': deploy['DEPLOY_LETSENCRYPT_EMAIL'],
        'DEPLOY_DB_MODE': deploy['DEPLOY_DB_MODE'],
        'DEPLOY_SHA': sha,
        'BACKEND_IMAGE': images['BACKEND_IMAGE'],
        'FRONTEND_IMAGE': images['FRONTEND_IMAGE'],
    }
    compose.update({name: backend[name] for name in _COMPOSE_FROM_BACKEND})
    try:
        files = {
            'backend.env': '\n'.join(_quote(name, value) for name, value in backend.items()) + '\n',
            'compose.env': '\n'.join(_quote(name, value) for name, value in compose.items()) + '\n',
        }
    except reference.SpecError as error:
        return {}, [str(error)]
    return files, []


def _write_private(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(content)


def main(argv=None, environ=None, repo_root=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument('--sortie', required=True, help='dossier où écrire backend.env et compose.env')
    args = parser.parse_args(argv)
    environ = os.environ if environ is None else environ
    repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    try:
        branch = reference.check_branch(environ.get('BRANCHE'))
        definitions = reference.load_spec(repo_root)
        secrets = reference.json_map(environ.get('SECRETS_JSON'))
        variables = reference.json_map(environ.get('VARS_JSON'))
        absentes = [name for name in ('BACKEND_IMAGE', 'FRONTEND_IMAGE', 'DEPLOY_SHA') if not environ.get(name)]
        if absentes:
            raise reference.SpecError(f"Variable d'environnement absente : {', '.join(absentes)}.")
        images = {name: environ[name] for name in ('BACKEND_IMAGE', 'FRONTEND_IMAGE')}
        sha = environ['DEPLOY_SHA']
    except reference.SpecError as error:
        print(f"Entrée invalide : {error}", file=sys.stderr)
        return 2

    files, errors = render(definitions, branch, secrets, variables, images, sha)
    if errors:
        print(f"Environnement « {branch} » inutilisable ({len(errors)} écart(s)) :")
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
