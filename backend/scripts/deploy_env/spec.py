"""
Liste de référence des variables et secrets de déploiement.

Sources :
- `backend/.env.example` et `frontend/.env.example` : ligne active = obligatoire, `# NOM=` = facultative,
  marqueur `# @secret` = secret GitHub (sinon variable). Les valeurs de ces fichiers ne sont jamais déployées ;
- les noms de déploiement (`DEPLOY_*`, `VM_SSH_*`) définis ci-dessous.

Variables et secrets sont stockés dans l'environnement GitHub qui porte le nom de la branche (`sandbox`, `main`, `prod`),
sous leur nom simple : `SECRET_KEY` de l'environnement `prod`. Voir 00readme/PLAN_CD.md.
"""
import json
import re
from dataclasses import dataclass
from pathlib import Path

BRANCHES = ('sandbox', 'main', 'prod')

# Origine d'une valeur : backend, frontend, déploiement, observabilité, ou généré par `preparer-vm`
SOURCES = ('backend', 'frontend', 'deploy', 'observabilite', 'minio', 'gitea', 'vm')

_LINE = re.compile(r'^(?P<commented>#\s*)?(?P<name>[A-Z][A-Z0-9_]*)=(?P<rest>.*)$')
_SECRET_MARKER = re.compile(r'#\s*@secret\b')


class SpecError(Exception):
    """Fichier de référence ou de valeurs invalide."""


@dataclass(frozen=True)
class Var:
    name: str
    secret: bool
    required: bool
    source: str
    # Modes d'accès à la VM (DEPLOY_ACCES) qui utilisent cette valeur ; vide = tous
    acces: tuple = ()

    def applies(self, acces):
        return not self.acces or acces in self.acces


# Secrets de notification CD : lus par l'orchestrateur uniquement, jamais rendus sur la VM
NOTIF_WEBHOOKS = frozenset({'SLACK_NOTIF_WEBHOOK', 'TEAMS_NOTIF_WEBHOOK'})
# Webhooks d'alertes Grafana : facultatifs ; rendus uniquement dans alerting-contacts.yml
ALERT_WEBHOOKS = frozenset({'SLACK_ALERT_WEBHOOK', 'TEAMS_ALERT_WEBHOOK'})

DEPLOY_VARS = (
    Var('DEPLOY_NAMESPACE', secret=False, required=True, source='deploy'),
    Var('DEPLOY_DOMAIN', secret=False, required=True, source='deploy'),
    Var('DEPLOY_LETSENCRYPT_EMAIL', secret=False, required=True, source='deploy'),
    Var('DEPLOY_ACCES', secret=False, required=True, source='deploy'),
    Var('DEPLOY_DB_MODE', secret=False, required=True, source='deploy'),
    # Taille disque VM attendue (Go) : documentation + controle deployer ; le resize cloud reste manuel/GCP
    Var('DEPLOY_DISK_GB', secret=False, required=True, source='deploy'),
    # Webhooks Slack / Teams (facultatifs) : notifications post-déploiement dans CD - ORCHESTRATEUR
    Var('SLACK_NOTIF_WEBHOOK', secret=True, required=False, source='deploy'),
    Var('TEAMS_NOTIF_WEBHOOK', secret=True, required=False, source='deploy'),
    # Accès SSH direct (IP publique et clé privée) : écrits par `preparer-vm`
    Var('VM_SSH_HOST', secret=True, required=True, source='vm', acces=('ssh',)),
    Var('VM_SSH_USER', secret=True, required=True, source='vm', acces=('ssh',)),
    Var('VM_SSH_PRIVATE_KEY', secret=True, required=True, source='vm', acces=('ssh',)),
    Var('VM_SSH_KNOWN_HOSTS', secret=False, required=True, source='vm', acces=('ssh',)),
    # Accès GCP sans IP publique (tunnel IAP, Workload Identity Federation) : aucun secret
    Var('GCP_PROJECT_ID', secret=False, required=True, source='deploy', acces=('gcp',)),
    Var('GCP_ZONE', secret=False, required=True, source='deploy', acces=('gcp',)),
    Var('GCP_INSTANCE', secret=False, required=True, source='deploy', acces=('gcp',)),
    Var('GCP_WIF_PROVIDER', secret=False, required=True, source='deploy', acces=('gcp',)),
    Var('GCP_SERVICE_ACCOUNT', secret=False, required=True, source='deploy', acces=('gcp',)),
)

# Fichier local observabilite.env.<branche> : console Grafana (CD - OBSERVABILITE SSH)
OBSERVABILITE_VARS = (
    Var('GRAFANA_ADMIN_USER', secret=False, required=True, source='observabilite'),
    Var('GRAFANA_ADMIN_PASSWORD', secret=True, required=True, source='observabilite'),
    Var('SLACK_ALERT_WEBHOOK', secret=True, required=False, source='observabilite'),
    Var('TEAMS_ALERT_WEBHOOK', secret=True, required=False, source='observabilite'),
)

# Fichier local minio.env.<branche> : compte root MinIO (CD - MINIO SSH)
MINIO_VARS = (
    Var('MINIO_ROOT_USER', secret=False, required=True, source='minio'),
    Var('MINIO_ROOT_PASSWORD', secret=True, required=True, source='minio'),
)

# Fichier local gitea.env.<branche> : forge Gitea de la VM (CD - GITEA SSH). Facultatif par environnement ;
# s'il existe, `definir` et le rendu exigent les cinq valeurs.
# Le jeton API et le secret du webhook (DEVSTREET_HUB_GITEA_*) restent dans backend.env.<branche>.
GITEA_VARS = (
    Var('GITEA_DOMAIN', secret=False, required=False, source='gitea'),
    Var('GITEA_DB_PASSWORD', secret=True, required=False, source='gitea'),
    Var('GITEA_ADMIN_USER', secret=False, required=False, source='gitea'),
    Var('GITEA_ADMIN_PASSWORD', secret=True, required=False, source='gitea'),
    Var('GITEA_ADMIN_EMAIL', secret=False, required=False, source='gitea'),
)

ACCES_MODES = ('ssh', 'gcp')

_ENUMS = {
    'DEPLOY_ACCES': ACCES_MODES,
    'DEPLOY_DB_MODE': ('interne', 'externe'),
}
_GRAFANA_PASSWORD_MIN = 16
_MINIO_PASSWORD_MIN = 16
_GITEA_PASSWORD_MIN = 16
# Gitea réserve certains noms (dont « admin ») : le compte administrateur doit en porter un autre
_GITEA_USER = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{2,39}$')
_GITEA_RESERVED_USERS = ('admin', 'administrator', 'root', 'api', 'user', 'org', 'assets', 'devtest')
_MINIO_KEY_MIN = 16
_MINIO_KEY_MAX = 40
_GRAFANA_USER = re.compile(r'^[A-Za-z0-9._-]{1,64}$')
_MINIO_USER = re.compile(r'^[A-Za-z0-9._-]{3,64}$')
_S3_BUCKET = re.compile(r'^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$')
_PATTERNS = {
    'GCP_PROJECT_ID': (re.compile(r'^[a-z][a-z0-9-]{4,28}[a-z0-9]$'), "identifiant de projet GCP (ex. mon-projet-123)"),
    'GCP_ZONE': (re.compile(r'^[a-z]+-[a-z]+[0-9]+-[a-z]$'), "zone GCP (ex. europe-west1-b)"),
    'GCP_INSTANCE': (re.compile(r'^[a-z]([-a-z0-9]{0,61}[a-z0-9])?$'), "nom d'instance GCP"),
    'GCP_WIF_PROVIDER': (
        re.compile(r'^projects/[0-9]+/locations/global/workloadIdentityPools/[A-Za-z0-9-]+/providers/[A-Za-z0-9-]+$'),
        "fournisseur Workload Identity (projects/<numero>/locations/global/workloadIdentityPools/<pool>/providers/<fournisseur>)",
    ),
    'GCP_SERVICE_ACCOUNT': (
        re.compile(r'^[a-z][a-z0-9-]{4,28}[a-z0-9]@[a-z][a-z0-9-]{4,28}[a-z0-9]\.iam\.gserviceaccount\.com$'),
        "adresse de compte de service (nom@projet.iam.gserviceaccount.com)",
    ),
}
_NAMESPACE = re.compile(r'^[a-z0-9][a-z0-9-]{1,40}$')
_DOMAIN = re.compile(r'^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$')
_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_HTTPS_URL = re.compile(r'^https://\S+$')
_DISK_GB = re.compile(r'^[1-9][0-9]{1,2}$')


def parse_example(text, source):
    """Lit un `.env.example` et retourne la liste des `Var` qu'il déclare."""
    if source not in ('backend', 'frontend'):
        raise SpecError(f"Source inconnue : {source}")
    found = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        match = _LINE.match(raw.strip())
        if not match:
            continue
        name = match.group('name')
        secret = bool(_SECRET_MARKER.search(match.group('rest')))
        if secret and source == 'frontend':
            raise SpecError(f"{name} (ligne {number}) : le frontend est public, aucun secret n'y est permis.")
        if name in found:
            raise SpecError(f"{name} est déclaré deux fois (ligne {number}).")
        found[name] = Var(name, secret=secret, required=match.group('commented') is None, source=source)
    return list(found.values())


def load_spec(repo_root):
    """Backend, frontend et déploiement réunis. Un nom ne peut venir que d'une seule source."""
    repo_root = Path(repo_root)
    spec = []
    for source in ('backend', 'frontend'):
        path = repo_root / source / '.env.example'
        if not path.is_file():
            raise SpecError(f"Fichier introuvable : {path}")
        spec.extend(parse_example(path.read_text(encoding='utf-8'), source))
    spec.extend(DEPLOY_VARS)
    spec.extend(OBSERVABILITE_VARS)
    spec.extend(MINIO_VARS)
    spec.extend(GITEA_VARS)
    seen = set()
    for var in spec:
        if var.name in seen:
            raise SpecError(f"{var.name} est défini par deux sources.")
        seen.add(var.name)
        if var.name.upper().startswith('GITHUB_'):
            raise SpecError(
                f"{var.name} : GitHub refuse les noms de secrets et de variables commençant par GITHUB_ "
                "(ex. OAUTH_GITHUB_CLIENT_ID)."
            )
    return spec


def check_branch(branch):
    if branch not in BRANCHES:
        raise SpecError(f"Branche inconnue : {branch!r} (attendu : {', '.join(BRANCHES)}).")
    return branch


def gh_name(name, branch):
    """
    Nom GitHub d'une valeur dans l'environnement `branch` : le nom simple, l'environnement porte la branche.
    Seul point à changer si le rangement des valeurs dans GitHub évolue.
    """
    check_branch(branch)
    return name


def parse_dotenv(text):
    """Fichier de valeurs local : `NOM=valeur`, sans commentaire en fin de ligne (une valeur peut contenir `#`)."""
    values = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[len('export '):].lstrip()
        name, separator, value = line.partition('=')
        name = name.strip()
        if not separator or not re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
            raise SpecError(f"Ligne {number} invalide (attendu NOM=valeur, nom en MAJUSCULES).")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1]
        values[name] = value
    return values


def validate_value(name, value):
    """Message d'erreur si la valeur d'un nom de déploiement est invalide, sinon None."""
    if name in _ENUMS and value not in _ENUMS[name]:
        return f"{name} : valeur attendue parmi {', '.join(_ENUMS[name])}."
    if name == 'DEPLOY_NAMESPACE' and not _NAMESPACE.match(value):
        return f"{name} : 2 à 41 caractères, minuscules, chiffres et tirets (ex. boilerplate-develop)."
    if name == 'DEPLOY_DOMAIN' and not _DOMAIN.match(value):
        return f"{name} : nom de domaine attendu en minuscules, sans schéma ni chemin (ex. develop.monapp.com)."
    if name == 'DEPLOY_LETSENCRYPT_EMAIL' and not _EMAIL.match(value):
        return f"{name} : adresse e-mail attendue."
    if name == 'DEPLOY_DISK_GB':
        if not _DISK_GB.match(value) or not (20 <= int(value) <= 500):
            return f"{name} : entier entre 20 et 500 (Go), ex. 100."
    if name in NOTIF_WEBHOOKS and not _HTTPS_URL.match(value):
        return f"{name} : URL https attendue (Incoming Webhook Slack ou Teams)."
    if name in ALERT_WEBHOOKS and not _HTTPS_URL.match(value):
        return f"{name} : URL https attendue (Incoming Webhook Slack ou Teams)."
    if name == 'GRAFANA_ADMIN_USER' and not _GRAFANA_USER.match(value):
        return f"{name} : 1 à 64 caractères (lettres, chiffres, point, tiret, underscore)."
    if name == 'GRAFANA_ADMIN_PASSWORD' and len(value) < _GRAFANA_PASSWORD_MIN:
        return f"{name} : au moins {_GRAFANA_PASSWORD_MIN} caractères."
    if name == 'MINIO_ROOT_USER' and not _MINIO_USER.match(value):
        return f"{name} : 3 à 64 caractères (lettres, chiffres, point, tiret, underscore)."
    if name == 'MINIO_ROOT_PASSWORD' and len(value) < _MINIO_PASSWORD_MIN:
        return f"{name} : au moins {_MINIO_PASSWORD_MIN} caractères."
    if name == 'GITEA_DOMAIN' and not _DOMAIN.match(value):
        return f"{name} : nom de domaine attendu en minuscules, sans schéma ni chemin (ex. git.monapp.com)."
    if name == 'GITEA_ADMIN_USER':
        if not _GITEA_USER.match(value) or value.lower() in _GITEA_RESERVED_USERS:
            return f"{name} : 3 à 40 caractères (lettres, chiffres, point, tiret, underscore), pas un nom réservé par Gitea (admin, root, api...)."
    if name == 'GITEA_ADMIN_EMAIL' and not _EMAIL.match(value):
        return f"{name} : adresse e-mail attendue."
    if name in ('GITEA_DB_PASSWORD', 'GITEA_ADMIN_PASSWORD') and len(value) < _GITEA_PASSWORD_MIN:
        return f"{name} : au moins {_GITEA_PASSWORD_MIN} caractères."
    if name == 'S3_BUCKET_NAME' and not _S3_BUCKET.match(value):
        return f"{name} : nom de bucket S3 (minuscules, 3–63, ex. boilerplate-sandbox)."
    if name in ('S3_ACCESS_KEY', 'S3_SECRET_KEY'):
        if not (_MINIO_KEY_MIN <= len(value) <= _MINIO_KEY_MAX):
            return f"{name} : {_MINIO_KEY_MIN} à {_MINIO_KEY_MAX} caractères (limite MinIO)."
    if name in _PATTERNS and not _PATTERNS[name][0].match(value):
        return f"{name} : {_PATTERNS[name][1]} attendu."
    return None


def check_values(spec, source, values):
    """
    Contrôle un fichier de valeurs local : noms inconnus, valeurs vides ou invalides, valeurs manquantes.
    Les valeurs propres à un mode d'accès (GCP_*, VM_SSH_*) ne sont exigées que pour le DEPLOY_ACCES du fichier.
    """
    expected = {var.name: var for var in spec if var.source == source}
    acces = values.get('DEPLOY_ACCES')
    errors = []
    for name, value in values.items():
        if name not in expected:
            hint = ' (généré par preparer-vm)' if any(v.name == name and v.source == 'vm' for v in spec) else ''
            errors.append(f"{name} : nom absent de la liste de référence{hint}.")
        elif not value and expected[name].required:
            errors.append(f"{name} : valeur obligatoire vide.")
        else:
            problem = validate_value(name, value) if value else None
            if problem:
                errors.append(problem)
    for name, var in expected.items():
        # Sans DEPLOY_ACCES valide, on ne peut pas dire quelles valeurs de mode sont attendues : l'écart est déjà signalé
        if var.required and name not in values and (not var.acces or var.applies(acces)):
            errors.append(f"{name} : variable obligatoire manquante.")
    return errors


def check_environment(spec, branch, secret_names, variable_names, acces):
    """
    Compare l'état de GitHub à la liste de référence pour une branche.
    `secret_names` et `variable_names` : noms présents (valeur non vide) dans l'environnement de la branche.
    `acces` : valeur de DEPLOY_ACCES pour cette branche (None si absente : seules les valeurs communes sont contrôlées).
    """
    secrets = {name.upper() for name in secret_names}
    variables = {name.upper() for name in variable_names}
    errors = []
    for var in spec:
        if var.acces and not var.applies(acces):
            continue
        key = gh_name(var.name, branch)
        in_secrets, in_variables = key in secrets, key in variables
        if var.required and not in_secrets and not in_variables:
            errors.append(f"{key} : manquant ({'secret' if var.secret else 'variable'} obligatoire).")
        elif var.secret and in_variables:
            errors.append(f"{key} : enregistré comme variable (lisible par tous) alors que c'est un secret.")
        elif not var.secret and in_secrets:
            errors.append(f"{key} : enregistré comme secret alors que c'est une variable.")
    return errors


def json_map(raw):
    """Dictionnaire {nom: valeur} depuis `toJSON(secrets)` ou `toJSON(vars)`, valeurs vides écartées."""
    try:
        data = json.loads(raw or '{}')
    except json.JSONDecodeError:
        raise SpecError("JSON invalide.") from None
    if not isinstance(data, dict):
        raise SpecError("Objet JSON attendu.")
    return {str(name): str(value) for name, value in data.items() if value}


def json_value(raw, name):
    """Valeur d'un nom dans `toJSON(vars)` (nom insensible à la casse), '' si absent. Pour les variables, jamais les secrets."""
    for key, value in json_map(raw).items():
        if key.upper() == name.upper():
            return value
    return ''


def names_from_json(raw):
    """Noms dont la valeur n'est pas vide, depuis `toJSON(secrets)` ou `toJSON(vars)`. Ne conserve aucune valeur."""
    return set(json_map(raw))
