"""Django / DRF : configuration de production, authentification, exposition de l'API."""
import ast
import re

from ..models import ERROR, CRITICAL, WARNING, Hit, ScanFile, mask
from ..registry import rule
from .helpers import assigned, call_name, is_env_getter, line_text, parse

SETTINGS_GLOBS = ('*/settings.py', '*/settings/*.py')
PY = ('*.py',)


def _default_literal(node: ast.AST):
    """Valeur par défaut littérale d'un getenv(nom, defaut), ou d'une constante affectée directement."""
    if isinstance(node, ast.Constant):
        return node.value
    if is_env_getter(node) and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        return node.args[1].value
    return None


@rule(
    id='DJ-001', title='Clé de signature avec valeur par défaut', severity=CRITICAL, category='production',
    globs=SETTINGS_GLOBS,
    description='SECRET_KEY ou JWT_SIGNING_KEY a une valeur littérale ou une valeur de repli : en production, tout le monde la connaît.',
    recommendation='Lire la clé sans valeur par défaut et refuser de démarrer si elle manque (voir config/env_secrets.py).',
    sample_path='backend/config/settings.py',
    fail_example="import os\nSECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')\n",
    pass_example="import os\nSECRET_KEY = os.environ['SECRET_KEY']\nSECRET_KEY, JWT_SIGNING_KEY = read_signing_secrets()\n",
)
def default_signing_key(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for name in ('SECRET_KEY', 'JWT_SIGNING_KEY'):
        for node in assigned(tree, name):
            value = _default_literal(node.value)
            if isinstance(value, str) and value:
                yield Hit(node.lineno, f'{name} possède une valeur par défaut littérale',
                          mask(line_text(file, node.lineno)), key=name)


@rule(
    id='DJ-002', title='DEBUG activé par défaut', severity=ERROR, category='production', globs=SETTINGS_GLOBS,
    description='DEBUG vaut True en dur ou par défaut : pages d\'erreur détaillées, variables et chemins exposés.',
    recommendation="Lire DEBUG depuis l'environnement avec False comme valeur par défaut.",
    sample_path='backend/config/settings.py',
    fail_example="import os\nDEBUG = os.getenv('DEBUG', 'True') == 'True'\n",
    pass_example="import os\nDEBUG = os.getenv('DEBUG', 'False').lower() == 'true'\n",
)
def debug_default(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for node in assigned(tree, 'DEBUG'):
        if isinstance(node.value, ast.Constant) and node.value.value is True:
            yield Hit(node.lineno, 'DEBUG = True en dur', mask(line_text(file, node.lineno)), key='DEBUG')
            continue
        for sub in ast.walk(node.value):
            if is_env_getter(sub) and len(sub.args) >= 2 and isinstance(sub.args[1], ast.Constant) \
                    and str(sub.args[1].value).lower() in ('true', '1', 'yes'):
                yield Hit(node.lineno, 'DEBUG vaut True par défaut', mask(line_text(file, node.lineno)), key='DEBUG')
                break


@rule(
    id='DJ-003', title='ALLOWED_HOSTS ouvert à tous', severity=ERROR, category='production', globs=SETTINGS_GLOBS,
    description='ALLOWED_HOSTS contient "*" : attaques par en-tête Host (liens de réinitialisation empoisonnés, cache).',
    recommendation='Lister les noms de domaine réels.',
    sample_path='backend/config/settings.py',
    fail_example="ALLOWED_HOSTS = ['*']\n",
    pass_example="ALLOWED_HOSTS = ['app.exemple.fr']\n",
)
def allowed_hosts_wildcard(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for node in assigned(tree, 'ALLOWED_HOSTS'):
        for sub in ast.walk(node.value):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str) and '*' in sub.value:
                yield Hit(node.lineno, 'ALLOWED_HOSTS contient un joker', mask(line_text(file, node.lineno)), key='ALLOWED_HOSTS')
                break


@rule(
    id='DJ-004', title='CORS ouvert à toutes les origines', severity=ERROR, category='production', globs=SETTINGS_GLOBS,
    description='CORS_ALLOW_ALL_ORIGINS à True : n\'importe quel site peut appeler l\'API depuis le navigateur d\'un utilisateur.',
    recommendation='Lister les origines autorisées dans CORS_ALLOWED_ORIGINS.',
    sample_path='backend/config/settings.py',
    fail_example='CORS_ALLOW_ALL_ORIGINS = True\n',
    pass_example="CORS_ALLOWED_ORIGINS = ['https://app.exemple.fr']\n",
)
def cors_allow_all(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for name in ('CORS_ALLOW_ALL_ORIGINS', 'CORS_ORIGIN_ALLOW_ALL'):
        for node in assigned(tree, name):
            if isinstance(node.value, ast.Constant) and node.value.value is True:
                yield Hit(node.lineno, f'{name} = True', mask(line_text(file, node.lineno)), key=name)


@rule(
    id='DJ-005', title='Route publique (AllowAny)', severity=WARNING, category='auth', globs=PY,
    description='Une vue DRF est accessible sans authentification. C\'est parfois voulu (connexion, mot de passe oublié), mais doit être justifié.',
    recommendation='Utiliser IsAuthenticated ou une permission métier. Si la route doit rester publique, l\'ajouter aux exceptions avec une justification et ajouter une limitation de débit.',
    sample_path='backend/app/core/views/x.py',
    fail_example="@permission_classes([AllowAny])\ndef vue(request):\n    pass\n",
    pass_example="@permission_classes([IsAuthenticated])\ndef vue(request):\n    pass\n",
)
def allow_any(file: ScanFile):
    if 'AllowAny' not in file.text:
        return
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        candidates = []
        if isinstance(node, ast.Call) and call_name(node) == 'permission_classes':
            candidates = node.args
        elif isinstance(node, ast.keyword) and node.arg == 'permission_classes':
            candidates = [node.value]
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'permission_classes' for t in node.targets):
            candidates = [node.value]
        for candidate in candidates:
            for sub in ast.walk(candidate):
                if isinstance(sub, ast.Name) and sub.id == 'AllowAny':
                    yield Hit(sub.lineno, 'Vue accessible sans authentification',
                              mask(line_text(file, sub.lineno)))


@rule(
    id='DJ-006', title='Documentation de l\'API toujours exposée', severity=ERROR, category='production',
    globs=('*/urls.py',),
    description='Les routes Swagger/ReDoc sont déclarées sans condition : le schéma complet de l\'API est public en production.',
    recommendation='Ne les ajouter que si un réglage (ENABLE_API_DOCS) l\'autorise, ou les protéger par une permission.',
    sample_path='backend/config/urls.py',
    fail_example="urlpatterns = [\n    path('swagger/', view),\n]\n",
    pass_example="urlpatterns = []\nif settings.ENABLE_API_DOCS:\n    urlpatterns += [path('swagger/', view)]\n",
)
def docs_always_public(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for statement in tree.body:  # niveau module uniquement : un `if` englobant exclut la route
        if not isinstance(statement, (ast.Assign, ast.AugAssign)):
            continue
        for sub in ast.walk(statement):
            if isinstance(sub, ast.Call) and call_name(sub) in ('path', 're_path', 'url') and sub.args \
                    and isinstance(sub.args[0], ast.Constant) and isinstance(sub.args[0].value, str) \
                    and sub.args[0].value.startswith(('swagger', 'redoc')):
                yield Hit(sub.lineno, f"Route de documentation « {sub.args[0].value} » sans condition",
                          mask(line_text(file, sub.lineno)), key=sub.args[0].value)


@rule(
    id='DJ-010', title='Admin Django toujours exposé', severity=ERROR, category='production',
    globs=('*/urls.py',),
    description="La route /admin/ est déclarée sans condition : l'interface d'administration est publique en production et contourne les règles d'accès de l'API.",
    recommendation="Ne l'ajouter que si un réglage (ENABLE_ADMIN) l'autorise.",
    sample_path='backend/config/urls.py',
    fail_example="urlpatterns = [\n    path('admin/', admin.site.urls),\n]\n",
    pass_example="urlpatterns = []\nif settings.ENABLE_ADMIN:\n    urlpatterns += [path('admin/', admin.site.urls)]\n",
)
def admin_always_public(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for statement in tree.body:  # niveau module uniquement : un `if` englobant exclut la route
        if not isinstance(statement, (ast.Assign, ast.AugAssign)):
            continue
        for sub in ast.walk(statement):
            if (isinstance(sub, ast.Call) and call_name(sub) in ('path', 're_path', 'url') and sub.args
                    and isinstance(sub.args[0], ast.Constant) and isinstance(sub.args[0].value, str)
                    and sub.args[0].value.startswith('admin')):
                yield Hit(sub.lineno, f"Route d'administration « {sub.args[0].value} » sans condition",
                          mask(line_text(file, sub.lineno)), key=sub.args[0].value)


@rule(
    id='DJ-011', title='Migration destructive', severity=WARNING, category='data',
    globs=('*/migrations/*.py',),
    description="Une migration supprime un champ, un modèle ou des données (RemoveField, DeleteModel, RunSQL DROP/DELETE/TRUNCATE) : "
                "les données sont perdues et l'ancienne version du code, encore en ligne pendant le déploiement, casse.",
    recommendation="Déployer d'abord une version qui n'utilise plus le champ, sauvegarder la base, puis déclarer la migration "
                   "dans security-exceptions.json (relue, datée, attribuée).",
    sample_path='backend/app/core/migrations/0009_remove.py',
    fail_example="from django.db import migrations\n\n\nclass Migration(migrations.Migration):\n    operations = [\n"
                 "        migrations.RemoveField(model_name='user', name='phone'),\n    ]\n",
    pass_example="from django.db import migrations, models\n\n\nclass Migration(migrations.Migration):\n    operations = [\n"
                 "        migrations.AddField(model_name='user', name='phone', field=models.CharField(max_length=20, blank=True)),\n    ]\n",
)
def destructive_migration(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = (call_name(node) or '').rsplit('.', 1)[-1]
        if name in ('RemoveField', 'DeleteModel'):
            yield Hit(node.lineno, f'Opération destructive {name}', mask(line_text(file, node.lineno)), key=f'{name}:{node.lineno}')
        elif name == 'RunSQL' and node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str) \
                and re.search(r'\b(DROP|TRUNCATE|DELETE)\b', node.args[0].value, re.IGNORECASE):
            yield Hit(node.lineno, 'RunSQL supprime des données ou des objets', mask(line_text(file, node.lineno)),
                      key=f'RunSQL:{node.lineno}')


@rule(
    id='DJ-007', title='Protection CSRF désactivée', severity=WARNING, category='auth', globs=PY,
    description='csrf_exempt retire la protection CSRF d\'une vue.',
    recommendation='Retirer le décorateur ; pour une API à jetons Bearer le risque est faible mais doit être justifié.',
    sample_path='backend/app/core/views/x.py',
    fail_example='@csrf_exempt\ndef vue(request):\n    pass\n',
    pass_example='def vue(request):\n    pass\n',
)
def csrf_exempt(file: ScanFile):
    if 'csrf_exempt' not in file.text:
        return
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            for dec in node.decorator_list:
                name = dec.id if isinstance(dec, ast.Name) else getattr(dec, 'attr', '')
                if name == 'csrf_exempt':
                    yield Hit(dec.lineno, 'Vue exemptée de la protection CSRF', mask(line_text(file, dec.lineno)))


REQUIRED_HTTP_SETTINGS = ('SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE', 'SECURE_HSTS_SECONDS')


@rule(
    id='DJ-008', title='Réglages HTTP sécurisés absents', severity=WARNING, category='production',
    globs=SETTINGS_GLOBS,
    description='Cookies Secure et HSTS ne sont pas configurés (ou sont désactivés en dur) : cookies et sessions peuvent circuler en clair.',
    recommendation='Définir SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE et SECURE_HSTS_SECONDS (actifs hors DEBUG).',
    sample_path='backend/config/settings.py',
    fail_example='INSTALLED_APPS = []\n',
    pass_example='INSTALLED_APPS = []\nSESSION_COOKIE_SECURE = True\nCSRF_COOKIE_SECURE = True\nSECURE_HSTS_SECONDS = 3600\n',
)
def http_security_settings(file: ScanFile):
    tree = parse(file)
    if not tree or not list(assigned(tree, 'INSTALLED_APPS')):
        return  # fichier de réglages partiel : non concerné
    for name in REQUIRED_HTTP_SETTINGS:
        nodes = list(assigned(tree, name))
        if not nodes:
            yield Hit(1, f'{name} n\'est pas défini', '', key=name)
        for node in nodes:
            if isinstance(node.value, ast.Constant) and node.value.value in (False, 0):
                yield Hit(node.lineno, f'{name} désactivé en dur', mask(line_text(file, node.lineno)), key=name)


# ---------------------------------------------------------------------------------------------- DJ-009
MIN_PASSWORD_LENGTH = 10
REQUIRED_VALIDATORS = ('UserAttributeSimilarityValidator', 'MinimumLengthValidator', 'CommonPasswordValidator',
                       'NumericPasswordValidator')
DJANGO_DEFAULT_MIN_LENGTH = 8


def _validator_min_length(entry: ast.Dict):
    """min_length déclaré dans OPTIONS, sinon la valeur par défaut de Django (8)."""
    for key, value in zip(entry.keys, entry.values):
        if isinstance(key, ast.Constant) and key.value == 'OPTIONS' and isinstance(value, ast.Dict):
            for okey, ovalue in zip(value.keys, value.values):
                if isinstance(okey, ast.Constant) and okey.value == 'min_length' and isinstance(ovalue, ast.Constant):
                    return ovalue.value
    return DJANGO_DEFAULT_MIN_LENGTH


@rule(
    id='DJ-009', title='Politique de mot de passe trop faible', severity=WARNING, category='auth', globs=SETTINGS_GLOBS,
    description=f'AUTH_PASSWORD_VALIDATORS est absent, incomplet, ou MinimumLengthValidator accepte moins de {MIN_PASSWORD_LENGTH} caractères '
                '(8 par défaut dans Django). Les mots de passe courts ou prévisibles se devinent en quelques essais.',
    recommendation=f'Garder les 4 validateurs de Django et fixer OPTIONS {{"min_length": 12}} (au moins {MIN_PASSWORD_LENGTH}).',
    sample_path='backend/config/settings.py',
    fail_example="INSTALLED_APPS = []\nAUTH_PASSWORD_VALIDATORS = [\n    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},\n]\n",
    pass_example="INSTALLED_APPS = []\nAUTH_PASSWORD_VALIDATORS = [\n"
                 "    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},\n"
                 "    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},\n"
                 "    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},\n"
                 "    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},\n]\n",
)
def weak_password_policy(file: ScanFile):
    tree = parse(file)
    if not tree or not list(assigned(tree, 'INSTALLED_APPS')):
        return
    nodes = list(assigned(tree, 'AUTH_PASSWORD_VALIDATORS'))
    if not nodes:
        yield Hit(1, 'AUTH_PASSWORD_VALIDATORS n\'est pas défini', '', key='absent')
        return
    for node in nodes:
        if not isinstance(node.value, ast.List):
            continue
        present = {}
        for entry in node.value.elts:
            if isinstance(entry, ast.Dict):
                for key, value in zip(entry.keys, entry.values):
                    if isinstance(key, ast.Constant) and key.value == 'NAME' and isinstance(value, ast.Constant):
                        present[str(value.value).rsplit('.', 1)[-1]] = entry
        for name in REQUIRED_VALIDATORS:
            if name not in present:
                yield Hit(node.lineno, f'Validateur manquant : {name}', mask(line_text(file, node.lineno)), key=f'missing:{name}')
        if 'MinimumLengthValidator' in present:
            length = _validator_min_length(present['MinimumLengthValidator'])
            if not isinstance(length, int) or length < MIN_PASSWORD_LENGTH:
                yield Hit(node.lineno, f'Longueur minimale du mot de passe : {length} (au moins {MIN_PASSWORD_LENGTH} attendus)',
                          mask(line_text(file, node.lineno)), key='min-length')
