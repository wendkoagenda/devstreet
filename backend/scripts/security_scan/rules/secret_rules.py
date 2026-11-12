"""Secrets : valeurs codées en dur et fichiers sensibles versionnés."""
import re
from fnmatch import fnmatch

from ..models import CRITICAL, ERROR, Hit, ScanFile, mask
from ..registry import rule

CODE_GLOBS = ('*.py', '*.ts', '*.tsx', '*.js', '*.jsx', '*.sh', '*.yml', '*.yaml', 'Dockerfile', '*/Dockerfile',
              '.env*', '*/.env*', '*.conf')

KNOWN_TOKENS = {
    'clé privée': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY'),
    'clé AWS': re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    'clé API Google': re.compile(r'\bAIza[0-9A-Za-z_\-]{35}\b'),
    'token GitHub': re.compile(r'\bgh[pousr]_[A-Za-z0-9]{36,}\b'),
    'clé Stripe live': re.compile(r'\bsk_live_[0-9a-zA-Z]{20,}\b'),
    'token Slack': re.compile(r'\bxox[baprs]-[0-9A-Za-z\-]{20,}'),
}
ASSIGNED_SECRET = re.compile(
    r"""(?ix)(?<![A-Za-z])(?:password|passwd|pwd|secret|api_?key|private_?key|auth_?token|access_?token|signing_?key|secret_?key)\w*\s*[:=]\s*(["'])([^"'\s]{8,})\1"""
)
PLACEHOLDER = re.compile(r'(?i)(example|exemple|changeme|change-me|your|votre|xxx|\*{3}|<|\$|\{|dummy|placeholder|todo|test)')

# Un nom de clé (accessToken, user_token…) n'est pas un secret : lettres seules, sans chiffre
IDENTIFIER = re.compile(r'[A-Za-z_.\-]+')


@rule(
    id='SEC-001', title='Secret codé en dur', severity=CRITICAL, category='secrets', globs=CODE_GLOBS,
    description='Une clé, un mot de passe ou un token figure en clair dans un fichier versionné.',
    recommendation='Retirer la valeur du dépôt, la révoquer/régénérer (elle est compromise), puis la lire depuis une variable d\'environnement.',
    sample_path='backend/config/x.py',
    fail_example='AWS = "AKIAABCDEFGHIJKLMNOP"\nDB_PASSWORD = "Sup3rS3cretValue"\n',
    pass_example='DB_PASSWORD = os.getenv("DB_PASSWORD")\nEXEMPLE = "votre-mot-de-passe"\n',
)
def hardcoded_secret(file: ScanFile):
    for number, line in enumerate(file.lines, 1):
        for label, pattern in KNOWN_TOKENS.items():
            if pattern.search(line):
                yield Hit(number, f'{label} détecté(e) dans le code', mask(line))
        match = ASSIGNED_SECRET.search(line)
        if match and not PLACEHOLDER.search(match.group(2)) and not IDENTIFIER.fullmatch(match.group(2)):
            yield Hit(number, 'Valeur secrète affectée en dur', mask(line))


SENSITIVE_FILES = ('.env', '*/.env', '.env.*', '*/.env.*', '*.pem', '*.key', '*.p12', '*.pfx', 'id_rsa', '*/id_rsa',
                   '*.sqlite3', '*.log')
SAFE_FILES = ('*.example', '*.sample', '*.template')


@rule(
    id='SEC-002', title='Fichier sensible versionné', severity=CRITICAL, category='secrets',
    globs=('*',), description='Un fichier d\'environnement, une clé privée, une base locale ou un journal est suivi par git.',
    recommendation='Le retirer du suivi (git rm --cached), l\'ajouter à .gitignore, et régénérer les secrets qu\'il contenait.',
    sample_path='backend/.env', fail_example='SECRET_KEY=abc\n', pass_example='SECRET_KEY=\n',
    pass_path='backend/.env.example',
)
def sensitive_file(file: ScanFile):
    if any(fnmatch(file.path, g) for g in SAFE_FILES):
        return
    if file.path.endswith('.example') or file.path.endswith('.sample'):
        return
    if any(fnmatch(file.path, g) for g in SENSITIVE_FILES):
        yield Hit(1, f'Fichier sensible présent dans le dépôt : {file.path}', '', key=file.path)
