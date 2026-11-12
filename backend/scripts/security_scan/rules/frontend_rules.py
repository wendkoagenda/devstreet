"""Frontend React/TypeScript : stockage des jetons, injection HTML, liens, variables exposées."""
import re

from ..models import ERROR, WARNING, Hit, ScanFile, mask
from ..registry import rule

JS = ('*.ts', '*.tsx', '*.js', '*.jsx')

STORAGE_TOKEN = re.compile(r'(?:localStorage|sessionStorage)\s*\.\s*(?:getItem|setItem)\s*\(([^)]*)\)', re.I)
TOKEN_WORDS = re.compile(r'token|jwt', re.I)


@rule(
    id='FE-001', title='Jeton stocké dans le navigateur', severity=ERROR, category='frontend', globs=JS,
    description='Un JWT lu ou écrit dans localStorage/sessionStorage est exfiltrable par n\'importe quelle faille XSS.',
    recommendation='Utiliser des cookies HttpOnly posés par le serveur (voir 00readme/README_SAME_ORIGIN_COOKIES.md).',
    sample_path='frontend/src/x.ts',
    fail_example='const t = localStorage.getItem("accessToken");\n',
    pass_example='const theme = localStorage.getItem("theme");\n',
)
def token_in_storage(file: ScanFile):
    for number, line in enumerate(file.lines, 1):
        match = STORAGE_TOKEN.search(line)
        if match and TOKEN_WORDS.search(match.group(1)):
            yield Hit(number, 'Jeton d\'authentification dans le stockage du navigateur', mask(line))


@rule(
    id='FE-002', title='Injection HTML directe', severity=WARNING, category='frontend', globs=JS,
    description='dangerouslySetInnerHTML ou innerHTML insèrent du HTML non filtré : risque de XSS.',
    recommendation='Afficher du texte via React, ou assainir le HTML (DOMPurify) avant insertion.',
    sample_path='frontend/src/x.tsx',
    fail_example='<div dangerouslySetInnerHTML={{ __html: html }} />\n',
    pass_example='<div>{text}</div>\n',
)
def raw_html(file: ScanFile):
    for number, line in enumerate(file.lines, 1):
        if 'dangerouslySetInnerHTML' in line or re.search(r'\.(?:inner|outer)HTML\s*=(?!=)', line):
            yield Hit(number, 'HTML inséré sans assainissement', mask(line))


BLANK = re.compile(r'''target\s*[=:]\s*\{?\s*["']_blank["']''')
TAG_END = re.compile(r'(?<!=)>')


@rule(
    id='FE-003', title='Lien target="_blank" sans rel', severity=WARNING, category='frontend', globs=JS,
    description='Un lien qui s\'ouvre dans un nouvel onglet sans rel="noopener noreferrer" donne un accès à la page d\'origine.',
    recommendation='Ajouter rel="noopener noreferrer".',
    sample_path='frontend/src/x.tsx',
    fail_example='<a href={url} target="_blank">lien</a>\n',
    pass_example='<a href={url} target="_blank" rel="noreferrer">lien</a>\n',
)
def blank_without_rel(file: ScanFile):
    text = file.text
    for match in BLANK.finditer(text):
        start = text.rfind('<', 0, match.start())
        end_match = TAG_END.search(text, match.end())
        tag = text[start if start != -1 else match.start(): end_match.end() if end_match else len(text)]
        if not re.search(r'rel\s*=\s*[{"\'][^>]*?(noopener|noreferrer)', tag):
            number = text.count('\n', 0, match.start()) + 1
            yield Hit(number, 'target="_blank" sans rel="noopener noreferrer"', mask(file.lines[number - 1]))


SECRET_VITE = re.compile(r'\bVITE_[A-Z0-9_]*(?:SECRET|PASSWORD|PASSWD|TOKEN|PRIVATE|API_?KEY|CREDENTIAL)[A-Z0-9_]*')


@rule(
    id='FE-004', title='Variable VITE_ au nom de secret', severity=ERROR, category='frontend',
    globs=JS + ('Dockerfile', '*/Dockerfile', '*.yml', '*.yaml', '.env*', '*/.env*'),
    description='Toute variable VITE_* est copiée dans le JavaScript public. Un secret qui y est placé est lisible par tous.',
    recommendation='Ne jamais préfixer un secret par VITE_ : il doit rester côté serveur.',
    sample_path='frontend/src/x.ts',
    fail_example='const k = import.meta.env.VITE_API_SECRET;\n',
    pass_example='const u = import.meta.env.VITE_API_URL;\n',
)
def vite_secret(file: ScanFile):
    for number, line in enumerate(file.lines, 1):
        match = SECRET_VITE.search(line)
        if match:
            yield Hit(number, f'{match.group(0)} sera publique dans le bundle', mask(line), key=match.group(0))
