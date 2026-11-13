"""
Prépare les fichiers MinIO pour le job CD - MINIO SSH.

    BRANCHE=sandbox SECRETS_JSON='...' VARS_JSON='...' \
        python -m scripts.deploy_env.render_minio --sortie DOSSIER

Écrit (droits 600) :
- minio.env : MINIO_ROOT_USER / MINIO_ROOT_PASSWORD ;
- minio-app.env : seulement si USE_S3=True (S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_KEY).

N'affiche jamais une valeur. Code de sortie : 0 écrit, 1 valeurs invalides, 2 entrée invalide.
"""
import argparse
import os
import sys
from pathlib import Path

from scripts.deploy_env import spec as reference


def _quote(name, value):
    if any(char in value for char in ("'", '\n', '\r')):
        raise reference.SpecError(f"{name} : la valeur ne doit contenir ni apostrophe ni retour à la ligne.")
    return f"{name}='{value}'"


def _truthy(value):
    return (value or '').strip().lower() in ('1', 'true', 'yes', 'on')


def render_minio(branch, values):
    """Retourne ({fichier: contenu}, [erreurs])."""
    values = {name.upper(): value for name, value in values.items()}
    errors = []

    root_user = values.get(reference.gh_name('MINIO_ROOT_USER', branch), '')
    if not root_user:
        errors.append('MINIO_ROOT_USER : manquant.')
    else:
        problem = reference.validate_value('MINIO_ROOT_USER', root_user)
        if problem:
            errors.append(problem)

    root_password = values.get(reference.gh_name('MINIO_ROOT_PASSWORD', branch), '')
    if not root_password:
        errors.append('MINIO_ROOT_PASSWORD : manquant.')
    else:
        problem = reference.validate_value('MINIO_ROOT_PASSWORD', root_password)
        if problem:
            errors.append(problem)

    use_s3 = _truthy(values.get(reference.gh_name('USE_S3', branch), ''))
    app = {}
    if use_s3:
        for name in ('S3_BUCKET_NAME', 'S3_ACCESS_KEY', 'S3_SECRET_KEY'):
            value = values.get(reference.gh_name(name, branch), '')
            if not value:
                errors.append(f"{name} : manquant (requis quand USE_S3=True).")
            else:
                problem = reference.validate_value(name, value)
                if problem:
                    errors.append(problem)
                else:
                    app[name] = value

    if errors:
        return {}, errors

    try:
        files = {
            'minio.env': (
                _quote('MINIO_ROOT_USER', root_user) + '\n'
                + _quote('MINIO_ROOT_PASSWORD', root_password) + '\n'
            ),
        }
        if app:
            files['minio-app.env'] = '\n'.join(_quote(n, v) for n, v in app.items()) + '\n'
    except reference.SpecError as error:
        return {}, [str(error)]
    return files, []


def _write_private(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(content)


def main(argv=None, environ=None, repo_root=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument('--sortie', required=True, help='dossier où écrire minio.env')
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

    files, errors = render_minio(branch, values)
    if errors:
        print(f"MinIO « {branch} » inutilisable ({len(errors)} écart(s)) :")
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
