"""
Exposition de l'API : fuite de détails d'erreur, sérialiseurs trop larges, listes sans pagination, téléversements.
"""
import ast
import re

from ..models import ERROR, WARNING, Hit, ScanFile, mask
from ..registry import rule
from .helpers import assigned, call_name, line_text, parse

PY = ('*.py',)
SETTINGS = ('*/settings.py', '*/settings/*.py')
VIEWS = ('*/views/*.py', '*/views.py')
SERIALIZERS = ('*serializers*.py', '*/serializers/*.py')

RESPONSE_CALLS = ('Response', 'JsonResponse', 'HttpResponse', 'HttpResponseBadRequest', 'HttpResponseServerError')


def _names_in(node: ast.AST):
    return {sub.id for sub in ast.walk(node) if isinstance(sub, ast.Name)}


# ---------------------------------------------------------------------------------------------- API-001
@rule(
    id='API-001', title='Détail d\'exception renvoyé au client', severity=ERROR, category='exposure', globs=PY,
    description='Une réponse HTTP contient le message d\'une exception interne (str(e), e.args, traceback) : chemins, noms de tables, '
                'requêtes SQL ou détails de configuration deviennent visibles par l\'appelant. Les erreurs de validation '
                '(*ValidationError), faites pour être lues par l\'utilisateur, sont exclues.',
    recommendation='Journaliser l\'exception côté serveur (logger.exception) et renvoyer un message générique et stable '
                   '(« Opération impossible »), avec un code d\'erreur si le client doit réagir.',
    sample_path='backend/app/core/views/x.py',
    fail_example="def vue(request):\n    try:\n        run()\n    except Exception as e:\n        return Response({'error': str(e)}, status=400)\n",
    pass_example="def vue(request):\n    try:\n        run()\n    except Exception:\n        logger.exception('echec')\n        return Response({'error': 'Operation impossible'}, status=400)\n"
                 "    except ValidationError as e:\n        return Response({'error': str(e)}, status=400)\n",
)
def exception_detail_in_response(file: ScanFile):
    if 'except' not in file.text:
        return
    tree = parse(file)
    if not tree:
        return
    for handler in ast.walk(tree):
        if not isinstance(handler, ast.ExceptHandler) or not handler.name:
            continue
        caught = ast.unparse(handler.type) if handler.type is not None else ''
        if caught.endswith('ValidationError'):
            continue
        for stmt in handler.body:
            for call in ast.walk(stmt):
                if isinstance(call, ast.Call) and call_name(call).split('.')[-1] in RESPONSE_CALLS:
                    exposed = any(handler.name in _names_in(arg) for arg in [*call.args, *[k.value for k in call.keywords]])
                    traced = any(isinstance(sub, ast.Call) and call_name(sub).startswith('traceback.') for sub in ast.walk(call))
                    if exposed or traced:
                        yield Hit(call.lineno, f'Réponse HTTP contenant le détail de l\'exception ({caught or "toutes"})',
                                  mask(line_text(file, call.lineno)), key=f'{call.lineno}:{caught}')


# ---------------------------------------------------------------------------------------------- API-002
@rule(
    id='API-002', title='Sérialiseur trop large (fields = "__all__" ou exclude)', severity=WARNING, category='exposure',
    globs=SERIALIZERS,
    description='fields = "__all__" ou exclude exposent automatiquement tout nouveau champ du modèle (mot de passe haché, '
                'champs internes, données personnelles) et l\'acceptent en écriture (assignation en masse).',
    recommendation='Lister explicitement les champs exposés (fields = [...]) et déclarer read_only_fields.',
    sample_path='backend/app/metier/serializers.py',
    fail_example="class A(serializers.ModelSerializer):\n    class Meta:\n        model = M\n        fields = '__all__'\n"
                 "class B(serializers.ModelSerializer):\n    class Meta:\n        model = M\n        exclude = ('password',)\n",
    pass_example="class A(serializers.ModelSerializer):\n    class Meta:\n        model = M\n        fields = ['id', 'name']\n",
)
def broad_serializer(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    for meta in ast.walk(tree):
        if not (isinstance(meta, ast.ClassDef) and meta.name == 'Meta'):
            continue
        for stmt in meta.body:
            if not (isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) for t in stmt.targets)):
                continue
            name = next(t.id for t in stmt.targets if isinstance(t, ast.Name))
            if name == 'fields' and isinstance(stmt.value, ast.Constant) and stmt.value.value == '__all__':
                yield Hit(stmt.lineno, 'fields = "__all__" : tous les champs du modèle sont exposés',
                          mask(line_text(file, stmt.lineno)), key='fields:__all__')
            elif name == 'exclude':
                yield Hit(stmt.lineno, 'exclude : tout nouveau champ du modèle sera exposé automatiquement',
                          mask(line_text(file, stmt.lineno)), key='exclude')


# ---------------------------------------------------------------------------------------------- API-003
MAX_PAGE_SIZE = 100
PAGINATION_CALLS = ('paginate_queryset', 'get_paginated_response', 'paginator')


def _is_viewset(node: ast.ClassDef) -> bool:
    return any((b.id if isinstance(b, ast.Name) else getattr(b, 'attr', '')).endswith('ViewSet') for b in node.bases)


def _many_true(call: ast.Call) -> bool:
    return any(kw.arg == 'many' and isinstance(kw.value, ast.Constant) and kw.value.value is True for kw in call.keywords)


@rule(
    id='API-003', title='Liste sans pagination', severity=WARNING, category='exposure', globs=PY,
    description='Une route renvoie une collection entière : pagination désactivée (pagination_class = None), absente des réglages, '
                'taille de page excessive, ou action de ViewSet qui sérialise une liste (many=True) sans paginer. '
                'Une table volumineuse devient un déni de service (mémoire, temps de réponse) et une fuite en masse.',
    recommendation='Définir DEFAULT_PAGINATION_CLASS et un PAGE_SIZE raisonnable (100 au plus), et dans chaque action de liste '
                   'appeler self.paginate_queryset(...) puis self.get_paginated_response(...).',
    sample_path='backend/app/core/views/role_viewset.py',
    fail_example="class RoleViewSet(viewsets.ModelViewSet):\n    pagination_class = None\n"
                 "    def list(self, request):\n        serializer = self.get_serializer(self.get_queryset(), many=True)\n"
                 "        return Response(serializer.data)\n",
    pass_example="class RoleViewSet(viewsets.ModelViewSet):\n"
                 "    def list(self, request):\n        page = self.paginate_queryset(self.get_queryset())\n"
                 "        serializer = self.get_serializer(page, many=True)\n        return self.get_paginated_response(serializer.data)\n",
)
def unpaginated_list(file: ScanFile):
    tree = parse(file)
    if not tree:
        return
    # 1. Réglages : pagination absente ou page trop grande
    if list(assigned(tree, 'INSTALLED_APPS')):
        for node in assigned(tree, 'REST_FRAMEWORK'):
            if not isinstance(node.value, ast.Dict):
                continue
            keys = {k.value: v for k, v in zip(node.value.keys, node.value.values) if isinstance(k, ast.Constant)}
            if 'DEFAULT_PAGINATION_CLASS' not in keys:
                yield Hit(node.lineno, 'DEFAULT_PAGINATION_CLASS absent : aucune pagination par défaut',
                          mask(line_text(file, node.lineno)), key='no-pagination')
            size = keys.get('PAGE_SIZE')
            if size is None:
                yield Hit(node.lineno, 'PAGE_SIZE absent', mask(line_text(file, node.lineno)), key='no-page-size')
            elif isinstance(size, ast.Constant) and isinstance(size.value, int) and size.value > MAX_PAGE_SIZE:
                yield Hit(node.lineno, f'PAGE_SIZE = {size.value} (maximum recommandé : {MAX_PAGE_SIZE})',
                          mask(line_text(file, node.lineno)), key='page-size')
    # 2. Vues : pagination désactivée, ou liste sérialisée sans paginer
    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef):
            continue
        for stmt in cls.body:
            if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'pagination_class' for t in stmt.targets) \
                    and isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                yield Hit(stmt.lineno, f'{cls.name} : pagination_class = None',
                          mask(line_text(file, stmt.lineno)), key=f'{cls.name}:none')
        if not _is_viewset(cls):
            continue
        for method in cls.body:
            if not isinstance(method, ast.FunctionDef):
                continue
            body_nodes = [sub for stmt in method.body for sub in ast.walk(stmt)]
            lists = [n for n in body_nodes if isinstance(n, ast.Call) and _many_true(n)]
            paginated = any(isinstance(n, ast.Call) and call_name(n).split('.')[-1] in PAGINATION_CALLS for n in body_nodes) \
                or any(isinstance(n, ast.Attribute) and n.attr == 'paginator' for n in body_nodes)
            if lists and not paginated:
                yield Hit(lists[0].lineno, f'{cls.name}.{method.name} : liste sérialisée sans pagination',
                          mask(line_text(file, lists[0].lineno)), key=f'{cls.name}.{method.name}')


# ---------------------------------------------------------------------------------------------- API-004
UPLOAD_MARKERS = re.compile(r'request\.FILES|UploadedFile|serializers\.(?:File|Image)Field\(')
SIZE_CHECK = re.compile(r'\.size\b|max_size|MAX_UPLOAD|MAX_SIZE|DATA_UPLOAD_MAX|FILE_UPLOAD_MAX')
TYPE_CHECK = re.compile(r'splitext|content_type|allowed_extensions|FileExtensionValidator|python-magic|import magic|imghdr')


@rule(
    id='API-004', title='Téléversement sans contrôle de taille ou de type', severity=WARNING, category='exposure', globs=PY,
    description='Un fichier qui traite des téléversements (request.FILES, UploadedFile, FileField de sérialiseur) ne contrôle pas '
                'sa taille ou son type : saturation du disque, fichiers exécutables ou HTML servis depuis votre domaine (XSS stocké).',
    recommendation='Vérifier la taille maximale ET une liste blanche d\'extensions/types avant d\'enregistrer le fichier '
                   '(voir app/metier/utils/file_field_utils.py), et limiter la taille du corps de requête au proxy.',
    sample_path='backend/app/metier/views/x.py',
    fail_example="def upload(request):\n    f = request.FILES['doc']\n    storage.save(f.name, f)\n",
    pass_example="def upload(request):\n    f = request.FILES['doc']\n    if f.size > MAX_SIZE:\n        raise ValueError('trop gros')\n"
                 "    if os.path.splitext(f.name)[1] not in allowed_extensions:\n        raise ValueError('type')\n    storage.save(f.name, f)\n",
)
def unchecked_upload(file: ScanFile):
    match = UPLOAD_MARKERS.search(file.text)
    if not match:
        return
    missing = []
    if not SIZE_CHECK.search(file.text):
        missing.append('taille')
    if not TYPE_CHECK.search(file.text):
        missing.append('type')
    if missing:
        number = file.text.count('\n', 0, match.start()) + 1
        yield Hit(number, f'Téléversement sans contrôle de {" ni de ".join(missing)} dans ce fichier',
                  mask(file.lines[number - 1]), key=','.join(missing))
