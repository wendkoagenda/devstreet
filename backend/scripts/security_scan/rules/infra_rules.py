"""Docker, dépendances et configuration serveur (supply chain)."""
import json
import re

from ..models import ERROR, INFO, WARNING, Hit, ScanFile, mask
from ..registry import rule

DOCKERFILES = ('Dockerfile', '*/Dockerfile', '*.Dockerfile')


def _instructions(file: ScanFile):
    """Instructions Dockerfile (numéro de ligne, mot-clé, arguments), continuations `\\` regroupées."""
    buffer, start = '', 0
    for number, raw in enumerate(file.lines, 1):
        line = raw.strip()
        if not buffer and (not line or line.startswith('#')):
            continue
        if not buffer:
            start = number
        buffer += (' ' if buffer else '') + line.rstrip('\\').strip()
        if not line.endswith('\\'):
            parts = buffer.split(None, 1)
            yield start, parts[0].upper(), parts[1] if len(parts) > 1 else ''
            buffer = ''


@rule(
    id='DOCKER-001', title='Conteneur exécuté en root', severity=WARNING, category='supply-chain', globs=DOCKERFILES,
    description='L\'étage final n\'a pas d\'instruction USER (ou utilise root) : une faille dans l\'application donne les droits root du conteneur.',
    recommendation='Créer un utilisateur sans privilèges et l\'activer avec USER avant CMD.',
    sample_path='backend/Dockerfile',
    fail_example='FROM python:3.12-slim\nCMD ["python"]\n',
    pass_example='FROM python:3.12-slim\nRUN useradd app\nUSER app\nCMD ["python"]\n',
)
def runs_as_root(file: ScanFile):
    user, last_from = None, 1
    for number, keyword, args in _instructions(file):
        if keyword == 'FROM':
            user, last_from = None, number
        elif keyword == 'USER':
            user = args.split(':')[0].strip()
    if user in (None, 'root', '0'):
        yield Hit(last_from, 'Aucun utilisateur non-root dans l\'étage final', '', key='final-stage')


SECRET_NAME = re.compile(r'(?i)(SECRET|PASSWORD|PASSWD|TOKEN|PRIVATE|API_?KEY|CREDENTIAL)')


@rule(
    id='DOCKER-002', title='Secret passé par ARG ou ENV', severity=ERROR, category='supply-chain', globs=DOCKERFILES,
    description='Un ARG ou ENV au nom de secret est enregistré dans les couches de l\'image et lisible avec `docker history`.',
    recommendation='Fournir le secret à l\'exécution (variable du conteneur) ou, au build, avec RUN --mount=type=secret.',
    sample_path='backend/Dockerfile',
    fail_example='FROM python:3.12-slim\nARG API_TOKEN\nENV DB_PASSWORD=abc\n',
    pass_example='FROM python:3.12-slim\nARG VITE_API_URL\nENV PYTHONUNBUFFERED=1\n',
)
def secret_in_image(file: ScanFile):
    for number, keyword, args in _instructions(file):
        if keyword not in ('ARG', 'ENV'):
            continue
        for name in re.findall(r'(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)(?:=|\s|$)', args)[:3]:
            if SECRET_NAME.search(name) and not name.endswith('_FILE'):
                yield Hit(number, f'{keyword} {name} : la valeur sera visible dans l\'image', mask(f'{keyword} {args}'), key=f'{keyword}-{name}')
                break


@rule(
    id='DOCKER-003', title='Image de base non épinglée', severity=WARNING, category='supply-chain', globs=DOCKERFILES,
    description='L\'image de base n\'a pas de tag (ou utilise :latest) : le build n\'est pas reproductible et peut changer sans prévenir.',
    recommendation='Indiquer une version précise (python:3.12-slim-bookworm), idéalement avec son digest @sha256.',
    sample_path='backend/Dockerfile',
    fail_example='FROM python\nFROM node:latest\n',
    pass_example='FROM python:3.12-slim-bookworm\n',
)
def unpinned_image(file: ScanFile):
    stages = set()
    for number, keyword, args in _instructions(file):
        if keyword != 'FROM':
            continue
        tokens = [t for t in args.split() if not t.startswith('--')]
        image = tokens[0] if tokens else ''
        if len(tokens) >= 3 and tokens[1].upper() == 'AS':
            alias = tokens[2]
        else:
            alias = None
        if image not in stages and image != 'scratch' and '@sha256:' not in image:
            tag = image.rsplit(':', 1)[1] if ':' in image.split('/')[-1] else ''
            if not tag or tag == 'latest':
                yield Hit(number, f'Image {image} sans version précise', mask(f'FROM {image}'), key=image)
        if alias:
            stages.add(alias)


REQ_GLOBS = ('requirements*.txt', '*/requirements*.txt')


@rule(
    id='DEP-001', title='Dépendances Python non figées', severity=WARNING, category='supply-chain', globs=REQ_GLOBS,
    description='Des dépendances sont déclarées avec >=, ~= ou sans version : le build peut installer une version différente ou compromise.',
    recommendation='Figer chaque version avec == (et mettre à jour volontairement).',
    sample_path='backend/requirements.txt',
    fail_example='django>=4.2\nrequests\n',
    pass_example='# commentaire\ndjango==6.0.6\n-r base.txt\n',
)
def floating_python_deps(file: ScanFile):
    loose = []
    for number, raw in enumerate(file.lines, 1):
        line = raw.split('#', 1)[0].strip()
        if not line or line.startswith('-') or '==' in line or line.startswith(('git+', 'http')):
            continue
        loose.append((number, line))
    if loose:
        names = ', '.join(re.split(r'[<>=~! ]', l, 1)[0] for _, l in loose[:5])
        yield Hit(loose[0][0], f'{len(loose)} dépendance(s) non figée(s) : {names}{"…" if len(loose) > 5 else ""}',
                  '', key='floating')


@rule(
    id='DEP-002', title='Dépendances npm en intervalle de versions', severity=INFO, category='supply-chain',
    globs=('package.json', '*/package.json'),
    description='package.json utilise des intervalles (^, ~, *, latest). Avec un package-lock.json et `npm ci` le build reste reproductible (voir DEP-003 si le lock manque).',
    recommendation='Versionner package-lock.json et installer avec npm ci.',
    sample_path='frontend/package.json',
    fail_example='{"dependencies": {"react": "^19.0.0"}}\n',
    pass_example='{"dependencies": {"react": "19.0.0"}}\n',
)
def floating_npm_deps(file: ScanFile):
    try:
        data = json.loads(file.text)
    except ValueError:
        return
    loose = [
        name for section in ('dependencies', 'devDependencies')
        for name, version in (data.get(section) or {}).items()
        if isinstance(version, str) and re.match(r'^[\^~*><]|^latest$|^x$', version.strip())
    ]
    if not loose:
        return
    yield Hit(1, f'{len(loose)} dépendance(s) en intervalle de versions', '', key='floating')


@rule(
    id='DEP-003', title='package-lock.json absent', severity=WARNING, category='supply-chain',
    globs=('package.json', '*/package.json'),
    description='Sans package-lock.json, deux installations successives peuvent donner des versions différentes.',
    recommendation='Générer et versionner package-lock.json.',
    sample_path='frontend/package.json',
    fail_example='{"name": "x"}\n', pass_example='{"name": "x"}\n',
)
def missing_lock(file: ScanFile):
    lock = file.path.rsplit('/', 1)[0] + '/package-lock.json' if '/' in file.path else 'package-lock.json'
    if file.context is not None and not file.context.exists(lock):
        yield Hit(1, 'package-lock.json absent', '', key='no-lock')


# ---------------------------------------------------------------------------------------------- SUP-001
AUDIT_TOOLS = {
    'pip': ('pip-audit', 'safety check', 'osv-scanner'),
    'npm': ('npm audit', 'osv-scanner', 'audit-ci'),
}


def _dependency_scan_present(file: ScanFile, ecosystem: str) -> bool:
    """Vrai si Dependabot couvre l'écosystème, ou si un workflow lance un audit de dépendances."""
    context = file.context
    if context is None or not hasattr(context, 'all_files') or not hasattr(context, 'read'):
        return False
    for path in context.all_files:
        if path in ('.github/dependabot.yml', '.github/dependabot.yaml'):
            if re.search(rf'package-ecosystem:\s*["\']?{ecosystem}\b', context.read(path)):
                return True
        elif path.startswith('.github/workflows/') and path.endswith(('.yml', '.yaml')):
            text = context.read(path)
            if any(tool in text for tool in AUDIT_TOOLS[ecosystem]):
                return True
    return False


@rule(
    id='SUP-001', title='Aucune analyse des dépendances vulnérables', severity=WARNING, category='supply-chain',
    globs=('requirements.txt', '*/requirements.txt', 'package.json', '*/package.json'),
    description='Ni Dependabot (.github/dependabot.yml) ni une étape d\'audit (pip-audit, npm audit, osv-scanner) dans un workflow : '
                'une dépendance avec une faille connue reste en production sans que personne ne soit prévenu.',
    recommendation='Ajouter .github/dependabot.yml (écosystèmes pip et npm) et/ou un workflow qui lance pip-audit et npm audit.',
    sample_path='backend/requirements.txt',
    fail_example='django==5.0\n', pass_example='django==5.0\n',
)
def no_dependency_scan(file: ScanFile):
    ecosystem = 'pip' if file.path.endswith('requirements.txt') else 'npm'
    if not _dependency_scan_present(file, ecosystem):
        yield Hit(1, f'Aucune analyse automatique des dépendances {ecosystem} (Dependabot ou audit en CI)', '', key=ecosystem)
