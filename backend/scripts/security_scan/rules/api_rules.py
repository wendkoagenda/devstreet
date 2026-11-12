"""
Routes de l'API : versionnement et limitation de débit (rate limiting).

- Toute route d'API doit porter une version dans son chemin (/api/v1/...), pour pouvoir faire évoluer
  l'API sans casser les clients existants.
- Toute route doit être limitée en débit : une limite globale par défaut (DEFAULT_THROTTLE_CLASSES),
  et une limite propre sur les routes publiques (connexion, jeton, mot de passe oublié) qui sont les plus attaquées.
"""
import ast
import re

from ..models import ERROR, WARNING, Hit, ScanFile, mask
from ..registry import rule
from .helpers import assigned, call_name, line_text, parse

URLS = ('*/urls.py',)
PY = ('*.py',)
SETTINGS = ('*/settings.py', '*/settings/*.py')

VERSION_PREFIX = re.compile(r'^\^?v\d+(/|$)')
# Routes qui ne sont pas des routes d'API métier
NON_API_PREFIXES = ('admin/', 'swagger', 'redoc', 'static', 'media', '__debug__')


def _route_text(node: ast.Call):
    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
        return node.args[0].value
    return None


def _is_include(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and call_name(node) in ('include', 'django.urls.include')


@rule(
    id='RT-001', title='Route d\'API sans version', severity=ERROR, category='api', globs=URLS,
    description='Une route est déclarée sans préfixe de version (v1/, v2/…). Sans version, tout changement de contrat '
                'casse les clients existants (frontend déployé séparément, intégrations, mobiles).',
    recommendation='Placer la route sous un préfixe versionné (path("v1/", include(...)) ou /api/v1/...). '
                   'Les routes d\'administration et de documentation sont exclues.',
    sample_path='backend/app/core/urls.py',
    fail_example="urlpatterns = [\n    path('auth/login', login_view),\n    path('users', users_view),\n]\n",
    pass_example="urlpatterns = [\n    path('v1/auth/login', login_view),\n    path('v1/', include(router.urls)),\n    path('api/', include('app.core.urls')),\n    path('admin/', admin.site.urls),\n]\n",
)
def unversioned_route(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and call_name(node) in ('path', 're_path', 'url')):
            continue
        route = _route_text(node)
        if route is None or len(node.args) < 2:
            continue
        target = node.args[1]
        if _is_include(target):
            continue  # simple préfixe : les routes incluses sont examinées dans leur propre fichier
        if VERSION_PREFIX.match(route) or route.startswith(NON_API_PREFIXES):
            continue
        yield Hit(node.lineno, f'Route « {route} » sans préfixe de version',
                  mask(line_text(file, node.lineno)), key=route)


@rule(
    id='RT-002', title='Aucune limitation de débit par défaut', severity=ERROR, category='api', globs=SETTINGS,
    description='REST_FRAMEWORK ne définit pas DEFAULT_THROTTLE_CLASSES : les routes qui ne déclarent pas leur propre '
                'limite (toute l\'API métier) peuvent être appelées sans restriction (force brute, scraping, déni de service).',
    recommendation='Définir DEFAULT_THROTTLE_CLASSES (AnonRateThrottle et UserRateThrottle) et les taux anon / user '
                   'dans DEFAULT_THROTTLE_RATES.',
    sample_path='backend/config/settings.py',
    fail_example="INSTALLED_APPS = []\nREST_FRAMEWORK = {'DEFAULT_PAGINATION_CLASS': 'x'}\n",
    pass_example="INSTALLED_APPS = []\nREST_FRAMEWORK = {\n    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle'],\n    'DEFAULT_THROTTLE_RATES': {'anon': '60/minute'},\n}\n",
)
def no_default_throttle(file: ScanFile):
    tree = parse(file)
    if not tree or not list(assigned(tree, 'INSTALLED_APPS')):
        return  # fichier de réglages partiel
    for node in assigned(tree, 'REST_FRAMEWORK'):
        if not isinstance(node.value, ast.Dict):
            continue
        keys = {k.value: v for k, v in zip(node.value.keys, node.value.values)
                if isinstance(k, ast.Constant)}
        classes = keys.get('DEFAULT_THROTTLE_CLASSES')
        if classes is None or (isinstance(classes, (ast.List, ast.Tuple)) and not classes.elts):
            yield Hit(node.lineno, 'DEFAULT_THROTTLE_CLASSES absent ou vide : pas de limite par défaut',
                      mask(line_text(file, node.lineno)), key='DEFAULT_THROTTLE_CLASSES')
        elif 'DEFAULT_THROTTLE_RATES' not in keys:
            yield Hit(node.lineno, 'DEFAULT_THROTTLE_RATES absent : les classes de limitation n\'ont pas de taux',
                      mask(line_text(file, node.lineno)), key='DEFAULT_THROTTLE_RATES')


# Vues SimpleJWT publiques par construction (permission_classes = ()) : à limiter comme les autres routes publiques
PUBLIC_BASES = ('TokenObtainPairView', 'TokenRefreshView', 'TokenVerifyView', 'TokenObtainSlidingView',
                'TokenRefreshSlidingView', 'TokenBlacklistView')


def _mentions(node: ast.AST, name: str) -> bool:
    return any(isinstance(sub, ast.Name) and sub.id == name
               or isinstance(sub, ast.Attribute) and sub.attr == name for sub in ast.walk(node))


def _is_empty_list(node: ast.AST) -> bool:
    return isinstance(node, (ast.List, ast.Tuple)) and not node.elts


@rule(
    id='RT-003', title='Route publique ou limitation désactivée sans limite propre', severity=WARNING, category='api',
    globs=PY,
    description='Une vue accessible sans authentification (AllowAny, vues SimpleJWT) ne déclare pas de throttle_classes propre, '
                'ou une vue désactive la limitation avec throttle_classes = []. Les routes publiques sont les plus attaquées.',
    recommendation='Déclarer throttle_classes avec un taux dédié (comme LoginThrottle) sur chaque route publique, '
                   'et ne jamais vider throttle_classes.',
    sample_path='backend/app/core/views/x.py',
    fail_example="@api_view(['GET'])\n@permission_classes([AllowAny])\ndef csrf_view(request):\n    pass\n"
                 "class V(APIView):\n    throttle_classes = []\n",
    pass_example="@api_view(['POST'])\n@permission_classes([AllowAny])\n@throttle_classes([LoginThrottle])\ndef login_view(request):\n    pass\n"
                 "class V(TokenVerifyView):\n    throttle_classes = [VerifyThrottle]\n",
)
def public_route_without_throttle(file: ScanFile):
    if not any(word in file.text for word in ('AllowAny', 'Token', 'throttle_classes')):
        return
    tree = parse(file)
    if not tree:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            decorators = node.decorator_list
            throttle = next((d for d in decorators if isinstance(d, ast.Call) and call_name(d) == 'throttle_classes'), None)
            if throttle is not None and throttle.args and _is_empty_list(throttle.args[0]):
                yield Hit(node.lineno, f'{node.name} : limitation désactivée (throttle_classes([]))',
                          mask(line_text(file, node.lineno)), key=f'{node.name}:disabled')
                continue
            public = any(isinstance(d, ast.Call) and call_name(d) == 'permission_classes'
                         and d.args and _mentions(d.args[0], 'AllowAny') for d in decorators)
            if public and throttle is None:
                yield Hit(node.lineno, f'{node.name} : route publique sans throttle_classes propre',
                          mask(line_text(file, node.lineno)), key=f'{node.name}:public')
        elif isinstance(node, ast.ClassDef):
            body = {}
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            body[target.id] = stmt.value
            throttle = body.get('throttle_classes')
            if throttle is not None and _is_empty_list(throttle):
                yield Hit(node.lineno, f'{node.name} : limitation désactivée (throttle_classes = [])',
                          mask(line_text(file, node.lineno)), key=f'{node.name}:disabled')
                continue
            base_names = [b.id if isinstance(b, ast.Name) else getattr(b, 'attr', '') for b in node.bases]
            public = ('permission_classes' in body and _mentions(body['permission_classes'], 'AllowAny')) \
                or any(name in PUBLIC_BASES for name in base_names)
            if public and throttle is None:
                yield Hit(node.lineno, f'{node.name} : route publique sans throttle_classes propre',
                          mask(line_text(file, node.lineno)), key=f'{node.name}:public')


# ----------------------------------------------------------------------------------------------------------------------
# Tags Swagger : la documentation de l'API est rangée par tag, il doit refléter la version et la ressource réelles.
# Convention du dépôt : « V<n> - <Ressource> » pour un ViewSet (ex. RoleViewSet monté sous v1/ -> « V1 - Role »),
# « Auth » pour les vues d'authentification (auth_views.py).
# ----------------------------------------------------------------------------------------------------------------------
VIEWS = ('*/views/*.py',)
STANDARD_ACTIONS = ('list', 'create', 'retrieve', 'update', 'partial_update', 'destroy')
HTTP_METHODS = ('get', 'post', 'put', 'patch', 'delete')
ROUTER_VERSION = re.compile(r"""path\(\s*['"]v(\d+)/['"]\s*,\s*include\(\s*router""")
AUTH_TAG = 'Auth'


def _decorator_call(node, names):
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and call_name(decorator) in names:
            return decorator
    return None


def _tags(swagger_call):
    """Liste des tags littéraux d'un @swagger_auto_schema, ou None si absente / non littérale."""
    for kw in swagger_call.keywords:
        if kw.arg == 'tags' and isinstance(kw.value, (ast.List, ast.Tuple)):
            values = [e.value for e in kw.value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            return values if len(values) == len(kw.value.elts) else None
    return None


def _router_version(file: ScanFile):
    """Version sous laquelle le router de l'application est monté, lue dans le urls.py voisin (ex. '1')."""
    if file.context is None or not hasattr(file.context, 'read'):
        return None
    app_dir = file.path.rsplit('/views/', 1)[0]
    match = ROUTER_VERSION.search(file.context.read(f'{app_dir}/urls.py'))
    return match.group(1) if match else None


class _Expected:
    """Tag attendu : exact (version connue) ou par motif (version inconnue : « V<n> - Ressource »)."""

    def __init__(self, label, pattern=None):
        self.label = label
        self.pattern = pattern

    def accepts(self, tags):
        if len(tags) != 1:
            return False
        return tags[0] == self.label if self.pattern is None else bool(self.pattern.match(tags[0]))


def _expected_tag(file: ScanFile, node: ast.ClassDef):
    """Tag attendu pour une classe de vue, ou None si la convention ne s'applique pas."""
    base_names = [b.id if isinstance(b, ast.Name) else getattr(b, 'attr', '') for b in node.bases]
    if any(name.endswith('ViewSet') for name in base_names):
        model = node.name[:-len('ViewSet')] if node.name.endswith('ViewSet') else node.name
        version = _router_version(file)
        if version:
            return _Expected(f'V{version} - {model}')
        return _Expected(f'V<n> - {model}', re.compile(rf'^V\d+ - {re.escape(model)}$'))
    if file.path.endswith('auth_views.py'):
        return _Expected(AUTH_TAG)
    return None


def _documented_views(file: ScanFile, tree):
    """Produit (nœud, nom, tag attendu ou None, décorateur swagger ou None) pour chaque action documentable."""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and _decorator_call(node, ('api_view',)):
            expected = _Expected(AUTH_TAG) if file.path.endswith('auth_views.py') else None
            yield node, node.name, expected, _decorator_call(node, ('swagger_auto_schema',)), True
        elif isinstance(node, ast.ClassDef):
            expected = _expected_tag(file, node)
            is_viewset = any((b.id if isinstance(b, ast.Name) else getattr(b, 'attr', '')).endswith('ViewSet')
                             for b in node.bases)
            for method in node.body:
                if not isinstance(method, ast.FunctionDef) or method.name.startswith('_'):
                    continue
                is_action = _decorator_call(method, ('action',)) is not None
                documentable = (method.name in STANDARD_ACTIONS or is_action) if is_viewset \
                    else (method.name in HTTP_METHODS and expected is not None)
                if documentable:
                    yield method, f'{node.name}.{method.name}', expected, _decorator_call(method, ('swagger_auto_schema',)), is_viewset or expected is not None


@rule(
    id='RT-004', title='Tag Swagger incorrect', severity=WARNING, category='api', globs=VIEWS,
    description='Le tag d\'une route Swagger ne suit pas la convention : « V<n> - <Ressource> » pour un ViewSet (version du router '
                'et nom de la ressource), « Auth » pour les vues d\'authentification. Un mauvais tag range la route dans le '
                'mauvais groupe de la documentation (copier-coller entre ressources, version obsolète).',
    recommendation='Corriger tags=[...] dans @swagger_auto_schema : par exemple RoleViewSet monté sous v1/ -> tags=["V1 - Role"].',
    sample_path='backend/app/core/views/role_viewset.py',
    fail_example="class RoleViewSet(viewsets.ModelViewSet):\n"
                 "    @swagger_auto_schema(tags=['V1 - User'])\n    def list(self, request):\n        pass\n",
    pass_example="class RoleViewSet(viewsets.ModelViewSet):\n"
                 "    @swagger_auto_schema(tags=['V1 - Role'])\n    def list(self, request):\n        pass\n",
)
def wrong_swagger_tag(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for node, name, expected, swagger, _ in _documented_views(file, tree):
        tags = _tags(swagger) if swagger is not None else None
        if tags is None:
            continue  # absence de tag : voir RT-005
        if expected is not None and not expected.accepts(tags):
            yield Hit(swagger.lineno, f'{name} : tag {tags} au lieu de [{expected.label!r}]',
                      mask(line_text(file, swagger.lineno)), key=f'{name}:{tags}')
        elif expected is None and (len(tags) != 1 or not tags[0].strip()):
            yield Hit(swagger.lineno, f'{name} : un seul tag non vide est attendu (reçu {tags})',
                      mask(line_text(file, swagger.lineno)), key=f'{name}:{tags}')


@rule(
    id='RT-005', title='Route sans tag Swagger', severity=WARNING, category='api', globs=VIEWS,
    description='Une action de ViewSet (list, create, retrieve, update, partial_update, destroy, @action) ou une vue d\'API '
                'n\'a pas de @swagger_auto_schema avec tags : drf-yasg la range dans un groupe par défaut, '
                'sans version ni nom de ressource.',
    recommendation='Ajouter @swagger_auto_schema(tags=["V1 - <Ressource>"]) (ou ["Auth"]) sur l\'action.',
    sample_path='backend/app/core/views/role_viewset.py',
    fail_example="class RoleViewSet(viewsets.ModelViewSet):\n    def list(self, request):\n        pass\n",
    pass_example="class RoleViewSet(viewsets.ModelViewSet):\n"
                 "    @swagger_auto_schema(tags=['V1 - Role'])\n    def list(self, request):\n        pass\n"
                 "    def _helper(self):\n        pass\n",
)
def missing_swagger_tag(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for node, name, _expected, swagger, _documentable in _documented_views(file, tree):
        if swagger is None or _tags(swagger) is None:
            line = node.lineno
            yield Hit(line, f'{name} : pas de @swagger_auto_schema avec tags', mask(line_text(file, line)), key=name)
