"""
Prépare les fichiers d'observabilité (Grafana) pour le job CD - OBSERVABILITE SSH.

    BRANCHE=sandbox SECRETS_JSON='${{ toJSON(secrets) }}' VARS_JSON='${{ toJSON(vars) }}' \
        python -m scripts.deploy_env.render_observabilite --sortie DOSSIER

Écrit (droits 600) :
- observabilite.env : GF_SECURITY_ADMIN_USER et GF_SECURITY_ADMIN_PASSWORD
  (depuis GRAFANA_ADMIN_USER / GRAFANA_ADMIN_PASSWORD) ;
- alerting-contacts.yml : seulement si au moins un webhook d'alerte est présent.

N'affiche jamais une valeur. Code de sortie : 0 écrit, 1 valeurs invalides ou manquantes, 2 entrée invalide.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from scripts.deploy_env import spec as reference


def _quote(name, value):
    if any(char in value for char in ("'", '\n', '\r')):
        raise reference.SpecError(f"{name} : la valeur ne doit contenir ni apostrophe ni retour à la ligne.")
    return f"{name}='{value}'"


def render_observabilite(branch, values):
    """Retourne ({fichier: contenu}, [erreurs]). `values` = secrets + variables GitHub."""
    values = {name.upper(): value for name, value in values.items()}
    errors = []
    grafana_user = values.get(reference.gh_name('GRAFANA_ADMIN_USER', branch), '')
    if not grafana_user:
        errors.append('GRAFANA_ADMIN_USER : manquant.')
    else:
        problem = reference.validate_value('GRAFANA_ADMIN_USER', grafana_user)
        if problem:
            errors.append(problem)
    grafana_password = values.get(reference.gh_name('GRAFANA_ADMIN_PASSWORD', branch), '')
    if not grafana_password:
        errors.append('GRAFANA_ADMIN_PASSWORD : manquant.')
    else:
        problem = reference.validate_value('GRAFANA_ADMIN_PASSWORD', grafana_password)
        if problem:
            errors.append(problem)

    alert_webhooks = {}
    for name in sorted(reference.ALERT_WEBHOOKS):
        value = values.get(reference.gh_name(name, branch), '')
        if not value:
            continue
        problem = reference.validate_value(name, value)
        if problem:
            errors.append(problem)
        else:
            alert_webhooks[name] = value
    if errors:
        return {}, errors

    try:
        files = {
            'observabilite.env': (
                _quote('GF_SECURITY_ADMIN_USER', grafana_user) + '\n'
                + _quote('GF_SECURITY_ADMIN_PASSWORD', grafana_password) + '\n'
            ),
        }
        if alert_webhooks:
            files['alerting-contacts.yml'] = _alerting_contacts_yaml(alert_webhooks)
    except reference.SpecError as error:
        return {}, [str(error)]
    return files, []


def _alerting_contacts_yaml(webhooks):
    """Fichier de provisioning Grafana (contact points + politique). JSON valide = YAML valide."""
    receivers = []
    if 'SLACK_ALERT_WEBHOOK' in webhooks:
        receivers.append({
            'uid': 'slack-alertes',
            'type': 'slack',
            'settings': {'url': webhooks['SLACK_ALERT_WEBHOOK']},
            'disableResolveMessage': False,
        })
    if 'TEAMS_ALERT_WEBHOOK' in webhooks:
        receivers.append({
            'uid': 'teams-alertes',
            'type': 'teams',
            'settings': {'url': webhooks['TEAMS_ALERT_WEBHOOK']},
            'disableResolveMessage': False,
        })
    payload = {
        'apiVersion': 1,
        'contactPoints': [{
            'orgId': 1,
            'name': 'equipe',
            'receivers': receivers,
        }],
        'policies': [{
            'orgId': 1,
            'receiver': 'equipe',
            'group_by': ['grafana_folder', 'alertname'],
        }],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + '\n'


def _write_private(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(content)


def main(argv=None, environ=None, repo_root=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument('--sortie', required=True, help='dossier où écrire observabilite.env')
    args = parser.parse_args(argv)
    environ = os.environ if environ is None else environ
    repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    try:
        branch = reference.check_branch(environ.get('BRANCHE'))
        # Charge la spec pour valider que le depot est coherent (fichiers .env.example presents)
        reference.load_spec(repo_root)
        secrets = reference.json_map(environ.get('SECRETS_JSON'))
        variables = reference.json_map(environ.get('VARS_JSON'))
        # Les secrets priment si un nom est présent des deux côtés (ne devrait pas arriver).
        values = {**variables, **secrets}
    except reference.SpecError as error:
        print(f"Entrée invalide : {error}", file=sys.stderr)
        return 2

    files, errors = render_observabilite(branch, values)
    if errors:
        print(f"Observabilité « {branch} » inutilisable ({len(errors)} écart(s)) :")
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
