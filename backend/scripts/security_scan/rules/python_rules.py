"""Python : appels dangereux et SQL construit par concaténation."""
import ast

from ..models import ERROR, Hit, ScanFile, mask
from ..registry import rule
from .helpers import call_name, line_text, parse

PY = ('*.py',)
DANGEROUS_CALLS = {
    'eval': 'exécute du code arbitraire',
    'exec': 'exécute du code arbitraire',
    'os.system': 'exécute une commande shell',
    'pickle.loads': 'désérialisation exécutant du code',
    'pickle.load': 'désérialisation exécutant du code',
    'marshal.loads': 'désérialisation non sûre',
}
SUBPROCESS_CALLS = ('subprocess.run', 'subprocess.call', 'subprocess.Popen', 'subprocess.check_output', 'subprocess.check_call')


@rule(
    id='PY-001', title='Appel Python dangereux', severity=ERROR, category='injection', globs=PY,
    description='eval, exec, os.system, pickle ou subprocess avec shell=True permettent l\'injection de code ou de commande.',
    recommendation='Utiliser une alternative sûre (ast.literal_eval, json, subprocess avec une liste d\'arguments).',
    sample_path='backend/app/x.py',
    fail_example='import subprocess\nsubprocess.run(cmd, shell=True)\nvaleur = eval(texte)\n',
    pass_example='import subprocess\nsubprocess.run(["ls", "-l"])\n',
)
def dangerous_call(file: ScanFile):
    if not any(word in file.text for word in ('eval', 'exec', 'system', 'pickle', 'marshal', 'subprocess')):
        return
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        if name in DANGEROUS_CALLS:
            yield Hit(node.lineno, f'{name} : {DANGEROUS_CALLS[name]}', mask(line_text(file, node.lineno)), key=name)
        elif name in SUBPROCESS_CALLS and any(
            kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True
            for kw in node.keywords
        ):
            yield Hit(node.lineno, f'{name} avec shell=True', mask(line_text(file, node.lineno)), key=name + '-shell')


@rule(
    id='PY-002', title='SQL construit par concaténation', severity=ERROR, category='injection', globs=PY,
    description='Une requête SQL (execute, raw, extra) est construite avec une f-string, un format ou une concaténation.',
    recommendation='Utiliser des paramètres : cursor.execute("... %s", [valeur]) ou l\'ORM.',
    sample_path='backend/app/x.py',
    fail_example='cursor.execute(f"SELECT * FROM t WHERE id = {valeur}")\n',
    pass_example='cursor.execute("SELECT * FROM t WHERE id = %s", [valeur])\n',
)
def sql_concatenation(file: ScanFile):
    if not any(word in file.text for word in ('.execute(', '.raw(', '.extra(')):
        return
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ('execute', 'executemany', 'raw', 'extra') and node.args):
            continue
        query = node.args[0]
        built = (
            isinstance(query, ast.JoinedStr)
            or (isinstance(query, ast.BinOp) and isinstance(query.op, (ast.Add, ast.Mod)))
            or (isinstance(query, ast.Call) and isinstance(query.func, ast.Attribute) and query.func.attr == 'format')
        )
        if built:
            yield Hit(node.lineno, f'Requête {node.func.attr}() construite dynamiquement',
                      mask(line_text(file, node.lineno)), key=node.func.attr)
