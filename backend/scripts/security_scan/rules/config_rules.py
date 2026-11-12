"""Configuration serveur et dépôt : en-têtes HTTP, .gitignore, source maps."""
import re

from ..models import ERROR, WARNING, Hit, ScanFile, mask
from ..registry import rule


@rule(
    id='CFG-001', title='En-têtes de sécurité nginx absents', severity=WARNING, category='production',
    globs=('*nginx*.conf', 'nginx*.conf'),
    description='Le serveur web ne pose ni X-Content-Type-Options, ni X-Frame-Options, ni politique de sécurité de contenu.',
    recommendation='Ajouter les en-têtes (add_header ... always) ou inclure un fichier security-headers.conf.',
    sample_path='frontend/nginx.conf',
    fail_example='server {\n    listen 80;\n}\n',
    pass_example='server {\n    listen 80;\n    include /etc/nginx/security-headers.conf;\n}\n',
)
def nginx_security_headers(file: ScanFile):
    if not re.search(r'^\s*server\s*\{', file.text, re.M):
        return  # fichier sans bloc server (configuration principale)
    text = file.text.lower()
    if 'security-headers' in text:
        return
    missing = [h for h in ('x-content-type-options', 'x-frame-options') if h not in text]
    if missing:
        yield Hit(1, 'En-têtes manquants : ' + ', '.join(missing), '', key='headers')


@rule(
    id='CFG-002', title='.env non ignoré par git', severity=ERROR, category='secrets', globs=('.gitignore',),
    description='Aucune règle du .gitignore racine ne protège les fichiers .env : ils risquent d\'être commités.',
    recommendation='Ajouter .env et .env.* (sauf *.example) au .gitignore.',
    sample_path='.gitignore',
    fail_example='node_modules/\n',
    pass_example='node_modules/\n.env\n',
)
def gitignore_env(file: ScanFile):
    if not any(re.match(r'^(/|\*\*/)?(backend/|frontend/)?\.env', line.strip()) for line in file.lines):
        yield Hit(1, 'Aucune règle .env dans .gitignore', '', key='no-env')


@rule(
    id='CFG-003', title='Source maps publiques', severity=WARNING, category='production',
    globs=('vite.config.ts', '*/vite.config.ts', 'vite.config.js', '*/vite.config.js'),
    description='sourcemap: true publie le code source lisible du frontend en production.',
    recommendation='Désactiver les source maps de production, ou les téléverser vers un outil de suivi d\'erreurs privé.',
    sample_path='frontend/vite.config.ts',
    fail_example='export default { build: { sourcemap: true } }\n',
    pass_example='export default { build: { sourcemap: false } }\n',
)
def public_sourcemaps(file: ScanFile):
    for number, line in enumerate(file.lines, 1):
        if re.search(r'sourcemap\s*:\s*(true|["\']inline["\'])', line):
            yield Hit(number, 'Source maps activées pour le build', mask(line))
