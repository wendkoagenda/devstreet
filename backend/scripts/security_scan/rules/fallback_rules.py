"""
Valeurs de repli (fallbacks) : elles masquent les erreurs de configuration et les exceptions.

Une variable absente ou une erreur avalée ne doit pas être « corrigée » en silence : l'application
devrait échouer clairement. Ces règles détectent TOUS les replis, sans exception implicite ;
un repli voulu se justifie dans security-exceptions.json (daté, attribué).
"""
import ast
import re

from ..models import WARNING, Hit, ScanFile, mask
from ..registry import rule
from .helpers import call_name, line_text, parse

PY = ('*.py',)
JS = ('*.ts', '*.tsx', '*.js', '*.jsx')
SHELL = ('*.sh', 'Dockerfile', '*/Dockerfile', '*.Dockerfile', '*.yml', '*.yaml')

ENV_GETTERS = ('os.getenv', 'getenv', 'os.environ.get', 'environ.get')


def _const_name(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else '?'


def _is_none(node):
    return isinstance(node, ast.Constant) and node.value is None


@rule(
    id='FB-001', title='Variable d\'environnement Python avec valeur de repli', severity=WARNING, category='fallback',
    globs=PY,
    description='os.getenv(nom, defaut), os.environ.get(nom, defaut), `os.getenv(nom) or defaut` ou getattr(settings, nom, defaut) : '
                'une variable oubliée est remplacée en silence par une valeur qui peut être fausse en production.',
    recommendation='Lire la variable sans valeur par défaut et échouer au démarrage si elle manque '
                   '(os.environ[nom], ou une fonction qui lève ImproperlyConfigured). Un défaut réellement voulu se justifie en exception.',
    sample_path='backend/config/settings.py',
    fail_example="import os\nHOST = os.getenv('DB_HOST', 'localhost')\nPORT = os.getenv('DB_PORT') or '5432'\n",
    pass_example="import os\nHOST = os.environ['DB_HOST']\nOPTIONAL = os.getenv('PROXY')\nOTHER = os.getenv('X', None)\n",
)
def python_env_fallback(file: ScanFile):
    if not any(word in file.text for word in ('getenv', 'environ', 'getattr')):
        return
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_name(node)
            if name in ENV_GETTERS:
                default = node.args[1] if len(node.args) >= 2 else next(
                    (kw.value for kw in node.keywords if kw.arg == 'default'), None)
                if default is not None and not _is_none(default):
                    yield Hit(node.lineno, f'{name}({_const_name(node.args[0]) if node.args else "?"}) a une valeur de repli',
                              mask(line_text(file, node.lineno)), key=f'{name}:{_const_name(node.args[0]) if node.args else "?"}')
            elif name == 'getattr' and len(node.args) == 3 and isinstance(node.args[0], ast.Name) \
                    and node.args[0].id == 'settings':
                yield Hit(node.lineno, f'getattr(settings, {_const_name(node.args[1])}) a une valeur de repli',
                          mask(line_text(file, node.lineno)), key=f'getattr:{_const_name(node.args[1])}')
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            first = node.values[0]
            if isinstance(first, ast.Call) and call_name(first) in ENV_GETTERS and len(first.args) == 1:
                yield Hit(node.lineno, f'{call_name(first)}({_const_name(first.args[0])}) or <repli>',
                          mask(line_text(file, node.lineno)), key=f'or:{_const_name(first.args[0])}')


ENV_JS = re.compile(r'(?:import\.meta\.env|process\.env)\s*(?:\.\s*([A-Za-z0-9_]+)|\[\s*["\']([A-Za-z0-9_]+)["\']\s*\])\s*(\?\?|\|\|)')


@rule(
    id='FB-002', title='Variable d\'environnement JS/TS avec valeur de repli', severity=WARNING, category='fallback',
    globs=JS,
    description='import.meta.env.X ?? defaut ou process.env.X || defaut : une variable de build oubliée est remplacée en silence '
                '(URL d\'API vide, mauvais serveur, fonctionnalité muette).',
    recommendation='Vérifier la variable au démarrage et lever une erreur explicite si elle manque, plutôt que de la remplacer.',
    sample_path='frontend/src/config.ts',
    fail_example='export const url = import.meta.env.VITE_API_URL ?? "/api";\nconst b = process.env.BUCKET || "";\n',
    pass_example='export const url = import.meta.env.VITE_API_URL;\nconst mode = import.meta.env.MODE;\n',
)
def js_env_fallback(file: ScanFile):
    for number, line in enumerate(file.lines, 1):
        match = ENV_JS.search(line)
        if match:
            name = match.group(1) or match.group(2)
            yield Hit(number, f'{name} {match.group(3)} valeur de repli', mask(line), key=name)


# Journaux de serveur : invisibles pour l'appelant, ils ne « traitent » pas l'erreur.
# print / stdout / stderr, eux, informent directement l'utilisateur d'un outil en ligne de commande : ils comptent comme un traitement.
LOG_PREFIXES = ('logger.', 'logging.', 'log.', 'self.logger.', 'warnings.warn')


def _is_log_call(stmt) -> bool:
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
            and call_name(stmt.value).startswith(LOG_PREFIXES))


def _is_handled(handler: ast.ExceptHandler) -> bool:
    """Vrai si le bloc relance l'erreur ou fait un vrai traitement (appel autre qu'un simple journal)."""
    for stmt in handler.body:
        if _is_log_call(stmt):
            continue
        for sub in ast.walk(stmt):
            if isinstance(sub, (ast.Raise, ast.Call)):
                return True
    return False


def _only_trivial(handler: ast.ExceptHandler) -> bool:
    """Le bloc ne contient (hors journal) que pass/continue/break/…/return constant : l'erreur disparaît."""
    for stmt in handler.body:
        if _is_log_call(stmt) or isinstance(stmt, (ast.Pass, ast.Continue, ast.Break)):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            continue
        if isinstance(stmt, ast.Return) and (stmt.value is None or isinstance(stmt.value, (ast.Constant, ast.List, ast.Dict, ast.Tuple, ast.Set))):
            continue
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, (ast.Constant, ast.List, ast.Dict)):
            continue
        return False
    return True


@rule(
    id='FB-003', title='Exception avalée en Python', severity=WARNING, category='fallback', globs=PY,
    description='Un bloc except ne fait que pass/continue, ou renvoie une valeur constante (avec ou sans journal) : '
                'l\'erreur disparaît pour l\'appelant et le programme continue avec un état faux.',
    recommendation='Relancer l\'erreur, ou la traiter précisément (message à l\'utilisateur, réessai). Un journal seul ne suffit pas quand une valeur de repli est renvoyée.',
    sample_path='backend/app/x.py',
    fail_example='try:\n    run()\nexcept Exception:\n    pass\ntry:\n    run()\nexcept ValueError:\n    result = None\ntry:\n    run()\nexcept OSError:\n    logger.error("x")\n    return None\n',
    pass_example='try:\n    run()\nexcept ValueError:\n    logger.exception("echec")\n    raise\n',
)
def swallowed_exception(file: ScanFile):
    if 'except' not in file.text:
        return
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ExceptHandler) and not _is_handled(node) and _only_trivial(node)):
            continue
        caught = ast.unparse(node.type) if node.type is not None else 'toutes les exceptions'
        logged = any(_is_log_call(stmt) for stmt in node.body)
        substitute = any(isinstance(stmt, (ast.Return, ast.Assign)) for stmt in node.body)
        if not logged:
            yield Hit(node.lineno, f'Exception avalée ({caught}) : aucun journal, aucune relance',
                      mask(line_text(file, node.lineno)), key=f'except:{caught}')
        elif substitute:  # journalisée mais remplacée par une valeur constante : l'appelant ne voit pas l'erreur
            yield Hit(node.lineno, f'Exception journalisée mais remplacée par une valeur de repli ({caught})',
                      mask(line_text(file, node.lineno)), key=f'except-log:{caught}')


EMPTY_CATCH = re.compile(r'catch\s*(?:\([^)]*\))?\s*\{\s*(?://[^\n]*\n\s*|/\*.*?\*/\s*)*\}', re.S)
CONST_CATCH = re.compile(
    r'catch\s*(?:\([^)]*\))?\s*\{\s*(?://[^\n]*\n\s*)*return\s*(?:null|undefined|false|true|\[\]|\{\}|""|\'\'|0)?\s*;?\s*(?://[^\n]*)?\s*\}', re.S)
CONSOLE_STATEMENT = r'console\.\w+\((?:[^()]|\([^()]*\))*\)\s*;?\s*'
LOG_CONST_CATCH = re.compile(
    r'catch\s*(?:\([^)]*\))?\s*\{\s*(?://[^\n]*\n\s*)*(?:' + CONSOLE_STATEMENT + r'(?://[^\n]*\n\s*)*)+'
    r'return\s*(?:null|undefined|false|true|\[\]|\{\}|""|\'\'|0)\s*;?\s*\}', re.S)
PROMISE_CATCH = re.compile(r'\.catch\(\s*(?:\([^)]*\)|\w+)?\s*=>\s*(?:\{\s*\}|null|undefined|\[\]|\{\}|""|\'\'|0|false)\s*\)')


@rule(
    id='FB-004', title='Erreur avalée en JS/TS', severity=WARNING, category='fallback', globs=JS,
    description='catch vide, catch qui renvoie une constante (même après un console.error) et .catch(() => null) font disparaître l\'erreur : '
                'l\'interface continue avec des données fausses sans que personne ne le sache.',
    recommendation='Journaliser, afficher un message à l\'utilisateur ou relancer. Si l\'erreur est vraiment ignorable, le dire dans un commentaire et une exception.',
    sample_path='frontend/src/x.ts',
    fail_example='try { run(); } catch {}\nrun().catch(() => null);\ntry { run(); } catch (e) { return null; }\ntry { run(); } catch (e) { console.error(e); return false; }\n',
    pass_example='try { run(); } catch (e) { console.error(e); throw e; }\nrun().catch((e) => report(e));\n',
)
def swallowed_js_error(file: ScanFile):
    text = file.text
    seen = set()
    for label, pattern in (('catch vide', EMPTY_CATCH), ('catch qui renvoie une constante', CONST_CATCH),
                           ('catch qui journalise puis renvoie une constante', LOG_CONST_CATCH),
                           ('.catch() qui ignore l\'erreur', PROMISE_CATCH)):
        for match in pattern.finditer(text):
            number = text.count('\n', 0, match.start()) + 1
            if number in seen:
                continue
            seen.add(number)
            yield Hit(number, f'Erreur avalée : {label}', mask(file.lines[number - 1]), key=f'{label}')


SHELL_DEFAULT = re.compile(r'\$\{[A-Za-z_][A-Za-z0-9_]*:?[-=][^}]*\}')
DOCKER_ARG_DEFAULT = re.compile(r'^\s*ARG\s+[A-Za-z_][A-Za-z0-9_]*=\S')


@rule(
    id='FB-005', title='Valeur de repli dans un script ou un Dockerfile', severity=WARNING, category='fallback',
    globs=SHELL,
    description='${VAR:-defaut} dans un script, un fichier compose ou un workflow, ou ARG NOM=valeur dans un Dockerfile : '
                'la variable manquante est remplacée en silence au lieu de faire échouer le déploiement.',
    recommendation='Exiger la variable (${VAR:?message}) pour échouer avec un message clair.',
    sample_path='backend/entrypoint.sh',
    fail_example='PORT=${PORT:-8000}\n',
    pass_example='PORT=${PORT:?PORT est obligatoire}\n',
)
def shell_fallback(file: ScanFile):
    for number, line in enumerate(file.lines, 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if SHELL_DEFAULT.search(line):
            yield Hit(number, 'Valeur de repli ${VAR:-...}', mask(line))
        elif file.path.endswith('Dockerfile') and DOCKER_ARG_DEFAULT.match(line):
            yield Hit(number, 'ARG avec valeur par défaut', mask(line))
