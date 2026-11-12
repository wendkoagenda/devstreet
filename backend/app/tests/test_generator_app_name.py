"""
Le générateur CRUD génère dans l'application déclarée par « app_name » du JSON (défaut : metier),
au lieu d'écrire « metier » en dur.
"""
import ast
import contextlib
import io
import os
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from scripts.generator.app_creator import AppCreator
from scripts.generator.code_generator import ImprovedCodeGenerator
from scripts.generator.schema_validator import FieldConstraint, ModelDefinition, SchemaValidator
from scripts.generator.state_manager import ImprovedStateManager


def model_json(name='Yangotest', app_name=None, **meta):
    data = {
        'model_name': name,
        'fields': [{'name': 'titre', 'type': 'CharField', 'max_length': 200}],
        'meta': {'resource_plural': f'{name.lower()}s', **meta},
    }
    if app_name is not None:
        data['app_name'] = app_name
    return data


def make_model(name='Yangotest', app_name='yango', **meta):
    return ModelDefinition(
        model_name=name,
        app_name=app_name,
        fields={'titre': FieldConstraint(name='titre', type='CharField', max_length=200)},
        meta={'resource_plural': f'{name.lower()}s', **meta},
    )


class AppNameValidationTests(SimpleTestCase):
    def test_default_app_is_metier(self):
        self.assertEqual(SchemaValidator.validate_model(model_json()).app_name, 'metier')

    def test_default_app_is_metier_for_the_legacy_format(self):
        legacy = {
            'model': 'Produit',
            'attributes': {'nom': {'type': 'CharField', 'max_length': 50}},
            'meta': {'resource_plural': 'produits'},
        }
        self.assertEqual(SchemaValidator.validate_model(legacy).app_name, 'metier')

    def test_declared_app_is_kept(self):
        self.assertEqual(SchemaValidator.validate_model(model_json(app_name='yango')).app_name, 'yango')

    def test_invalid_app_names_are_rejected(self):
        for bad in ('Yango', '../core', 'a-b', 'app.yango', '', '1abc', 12):
            with self.subTest(app_name=bad):
                with self.assertRaises(ValueError):
                    SchemaValidator.validate_model(model_json(app_name=bad))


class GeneratedCodeTargetsTheAppTests(SimpleTestCase):
    def setUp(self):
        self.generator = ImprovedCodeGenerator()

    def test_templates_import_from_the_target_app(self):
        model = make_model(app_name='yango')
        for template in ('interface', 'repository', 'seeds', 'serializer', 'service', 'tests', 'viewset'):
            with self.subTest(template=template):
                code = self.generator.env.get_template(f'{template}.py.j2').render(model=model)
                self.assertNotIn('app.metier.models', code)
                self.assertNotIn('app.metier.serializers', code)
                self.assertNotIn('app.metier.services.yangotest', code)
                self.assertNotIn('app.metier.repositories', code)
                self.assertNotIn('app.metier.permissions', code)
                ast.parse(code)

    def test_viewset_imports_its_own_app_modules(self):
        code = self.generator.env.get_template('viewset.py.j2').render(model=make_model(app_name='yango'))
        self.assertIn('from app.yango.models import Yangotest', code)
        self.assertIn('from app.yango.serializers import YangotestSerializer', code)
        self.assertIn('from app.yango.services.yangotest_service import YangotestService', code)

    def test_shared_utils_stay_in_metier(self):
        """Les utilitaires de fichiers n'existent que dans metier : ils ne suivent pas l'application cible."""
        model = make_model(app_name='yango')
        model.fields['document'] = FieldConstraint(
            name='document', type='FileField', upload_folder='yangotests/document',
            allowed_extensions=['.pdf'], max_size_mb=5,
        )
        context = self.generator._template_context(model)
        service = self.generator.env.get_template('service.py.j2').render(**context)
        self.assertIn('from app.yango.models import Yangotest', service)
        self.assertIn('from app.metier.utils.file_field_utils import', service)

    def test_metier_output_is_unchanged(self):
        code = self.generator.env.get_template('viewset.py.j2').render(model=make_model(app_name='metier'))
        self.assertIn('from app.metier.models import Yangotest', code)

    def test_model_table_and_url_follow_the_app(self):
        code = self.generator.generate_model_class_only(make_model(app_name='yango'))
        self.assertIn("db_table = 'yango_yangotests'", code)
        self.assertIn('/yango/yangotests/', code)

    def test_explicit_db_table_is_kept(self):
        code = self.generator.generate_model_class_only(make_model(app_name='yango', db_table='custom_table'))
        self.assertIn("db_table = 'custom_table'", code)

    def test_model_template_follows_the_app(self):
        code = self.generator.env.get_template('model.py.j2').render(model=make_model(app_name='yango'))
        self.assertIn("db_table = 'yango_yangotests'", code)

    def test_serializer_imports_target_the_app(self):
        content = 'from rest_framework import serializers\n'
        updated = self.generator.update_imports_in_serializers(content, make_model(app_name='yango'))
        self.assertIn('from app.yango.models import Yangotest', updated)
        self.assertNotIn('app.metier.models', updated)


class GenerateApiTests(SimpleTestCase):
    """generate_api de bout en bout dans un dossier temporaire (sans migrations)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        for name in ('metier', 'yango'):
            self.make_app(name)
        self.generator = ImprovedCodeGenerator(app_root=str(self.root), apply_migrations=False)
        self.generator.backup_dir = str(self.root / 'backups')
        os.makedirs(self.generator.backup_dir)

    def make_app(self, name):
        app = self.root / name
        app.mkdir()
        (app / '__init__.py').write_text('', encoding='utf-8')
        (app / 'models.py').write_text('from django.db import models\n', encoding='utf-8')
        (app / 'serializers.py').write_text('from rest_framework import serializers\n', encoding='utf-8')
        (app / 'urls.py').write_text(
            'from rest_framework import routers\n\nrouter = routers.DefaultRouter()\n\nurlpatterns = router.urls\n',
            encoding='utf-8',
        )

    def generate(self, data):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            ok = self.generator.generate_api(data, 'zone_1')
        return ok, out.getvalue()

    def test_code_is_generated_in_the_declared_app_only(self):
        ok, output = self.generate(model_json(app_name='yango'))
        self.assertTrue(ok, output)

        yango = self.root / 'yango'
        for relative in (
            'views/yangotest_viewset.py',
            'services/yangotest_service.py',
            'repositories/yangotest_repository.py',
            'interfaces/yangotest_repository_interface.py',
            'permissions/yangotest_permissions.py',
            'management/commands/seed_yangotest.py',
        ):
            self.assertTrue((yango / relative).exists(), relative)
        self.assertFalse((self.root / 'metier' / 'views').exists())
        self.assertEqual((self.root / 'metier' / 'models.py').read_text(encoding='utf-8'), 'from django.db import models\n')

        self.assertIn('class Yangotest(models.Model):', (yango / 'models.py').read_text(encoding='utf-8'))
        self.assertIn('from app.yango.models import Yangotest', (yango / 'serializers.py').read_text(encoding='utf-8'))
        urls = (yango / 'urls.py').read_text(encoding='utf-8')
        self.assertIn('from app.yango.views.yangotest_viewset import YangotestViewSet', urls)
        self.assertIn("app_name = 'yango'", urls)
        self.assertNotIn('metier', urls)
        self.assertTrue((self.root / 'tests' / 'test_yangotest.py').exists())

    def test_default_app_is_still_metier(self):
        ok, output = self.generate(model_json('Produit'))
        self.assertTrue(ok, output)
        self.assertTrue((self.root / 'metier' / 'views' / 'produit_viewset.py').exists())
        self.assertIn("app_name = 'metier'", (self.root / 'metier' / 'urls.py').read_text(encoding='utf-8'))
        self.assertFalse((self.root / 'yango' / 'views').exists())

    def test_regeneration_is_idempotent(self):
        self.assertTrue(self.generate(model_json(app_name='yango'))[0])
        first = (self.root / 'yango' / 'urls.py').read_text(encoding='utf-8')
        self.assertTrue(self.generate(model_json(app_name='yango'))[0])
        self.assertEqual((self.root / 'yango' / 'urls.py').read_text(encoding='utf-8'), first)
        self.assertEqual(first.count('router.register('), 1)

    def test_missing_app_is_refused_without_writing_anything(self):
        ok, output = self.generate(model_json(app_name='inconnue'))
        self.assertFalse(ok)
        self.assertIn('inconnue', output)
        self.assertFalse((self.root / 'inconnue').exists())

    def test_model_already_in_another_app_is_refused(self):
        self.assertTrue(self.generate(model_json('Produit', app_name='metier'))[0])
        ok, output = self.generate(model_json('Produit', app_name='yango'))
        self.assertFalse(ok)
        self.assertIn("existe déjà dans l'application « metier »", output)

    def test_same_table_in_the_same_app_is_refused(self):
        self.assertTrue(self.generate(model_json('Fusion', db_table='metier_fusion'))[0])
        ok, output = self.generate(model_json('Yangotest', db_table='metier_fusion'))
        self.assertFalse(ok)
        self.assertIn('metier_fusion', output)

    def test_same_route_in_another_app_is_refused(self):
        self.assertTrue(self.generate(model_json('Fusion', resource_plural='fusions'))[0])
        ok, output = self.generate(model_json('Yangotest', app_name='yango', resource_plural='fusions'))
        self.assertFalse(ok)
        self.assertIn('fusions', output)

    def test_same_route_with_another_viewset_in_the_same_app_is_refused(self):
        self.assertTrue(self.generate(model_json('Fusion', resource_plural='fusions'))[0])
        ok, output = self.generate(model_json('Yangotest', resource_plural='fusions'))
        self.assertFalse(ok)
        self.assertIn('fusions', output)
        urls = (self.root / 'metier' / 'urls.py').read_text(encoding='utf-8')
        self.assertNotIn('YangotestViewSet', urls)  # le refus ne laisse pas de route à moitié écrite


class AppCreatorUrlsTests(SimpleTestCase):
    URLS = (
        "schema_view = get_schema_view(\n"
        "    patterns=[\n"
        "        path('api/', include('app.core.urls')),\n"
        "        path('api/', include('app.metier.urls')),\n"
        "    ],\n"
        ")\n\n"
        "urlpatterns = [\n"
        "    path('api/', include('app.core.urls')),\n"
        "    path('api/', include('app.metier.urls')),\n"
        "]\n"
    )

    def patch(self, creator, app_name):
        with contextlib.redirect_stdout(io.StringIO()):
            creator.patch_urls(app_name)

    def test_include_is_added_once_per_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            creator = AppCreator()
            creator.urls_file = Path(tmp) / 'urls.py'
            creator.urls_file.write_text(self.URLS, encoding='utf-8')

            self.patch(creator, 'yango')
            content = creator.urls_file.read_text(encoding='utf-8')

            self.assertEqual(content.count("include('app.yango.urls')"), 2)  # schema_view + urlpatterns
            self.assertIn("        path('api/', include('app.yango.urls')),\n    ],", content)
            self.assertIn("    path('api/', include('app.yango.urls')),\n]", content)
            ast.parse(content.replace('schema_view = get_schema_view(', 'schema_view = dict('))

    def test_second_call_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            creator = AppCreator()
            creator.urls_file = Path(tmp) / 'urls.py'
            creator.urls_file.write_text(self.URLS, encoding='utf-8')

            self.patch(creator, 'yango')
            once = creator.urls_file.read_text(encoding='utf-8')
            self.patch(creator, 'yango')

            self.assertEqual(creator.urls_file.read_text(encoding='utf-8'), once)


class StateManagerAppTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        for name in ('metier', 'yango'):
            (self.root / name / 'views').mkdir(parents=True)
            (self.root / name / 'models.py').write_text('from django.db import models\n', encoding='utf-8')
        self.state = ImprovedStateManager(state_file=str(self.root / 'state.json'))
        self.state.app_root = str(self.root)
        self.state.app_dir = str(self.root / 'metier')

    def test_api_records_its_app_and_checksums_are_prefixed_outside_metier(self):
        (self.root / 'yango' / 'views' / 'yangotest_viewset.py').write_text('x = 1\n', encoding='utf-8')
        self.state.add_generated_api('Yangotest', 'zone_1', 'yangotest.json', resource_plural='yangotests', app_name='yango')

        self.assertEqual(self.state.get_api_app_name('Yangotest'), 'yango')
        self.assertIn('yango::models.py', self.state.state['file_checksums'])
        self.assertIn('yango::views/yangotest_viewset.py', self.state.state['file_checksums'])
        self.assertNotIn('views/yangotest_viewset.py', self.state.state['file_checksums'])

    def test_legacy_entries_default_to_metier(self):
        self.state.state['generated_apis']['Vieux'] = {'model_name': 'Vieux'}
        self.assertEqual(self.state.get_api_app_name('Vieux'), 'metier')

    def test_checksum_keys_resolve_to_the_right_file(self):
        self.assertEqual(self.state.checksum_key('metier', 'models.py'), 'models.py')
        self.assertEqual(
            os.path.normpath(self.state.checksum_key_to_path('models.py')),
            str(self.root / 'metier' / 'models.py'),
        )
        self.assertEqual(
            os.path.normpath(self.state.checksum_key_to_path('yango::views/a_viewset.py')),
            str(self.root / 'yango' / 'views' / 'a_viewset.py'),
        )

    def test_integrity_check_follows_the_app_of_each_api(self):
        for folder, file_name in (('services', 'yangotest_service.py'), ('repositories', 'yangotest_repository.py')):
            (self.root / 'yango' / folder).mkdir()
            (self.root / 'yango' / folder / file_name).write_text('', encoding='utf-8')
        (self.root / 'yango' / 'views' / 'yangotest_viewset.py').write_text('x = 1\n', encoding='utf-8')
        self.state.add_generated_api('Yangotest', 'zone_1', 'yangotest.json', resource_plural='yangotests', app_name='yango')

        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(self.state.validate_state_integrity())


CORE_MODELS = (
    'from django.contrib.auth.models import AbstractUser\n'
    'from django.db import models\n\n\n'
    'class User(AbstractUser):\n'
    '    pass\n'
)

CORE_URLS = '''"""URLs de core."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.core.views.auth_views import login_view
from app.core.views.user_viewset import UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/login', login_view, name='login'),
    path('v1/', include(router.urls)),
]

app_name = 'core'
'''


class GenerateInHandWrittenAppTests(SimpleTestCase):
    """Générer dans core : application écrite à la main, avec son propre User et un urls.py personnalisé."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        core = self.root / 'core'
        core.mkdir()
        (core / '__init__.py').write_text('', encoding='utf-8')
        (core / 'models.py').write_text(CORE_MODELS, encoding='utf-8')
        (core / 'serializers.py').write_text(
            'from rest_framework import serializers\nfrom app.core.models import User\n', encoding='utf-8'
        )
        (core / 'urls.py').write_text(CORE_URLS, encoding='utf-8')
        self.generator = ImprovedCodeGenerator(app_root=str(self.root), apply_migrations=False)
        self.generator.backup_dir = str(self.root / 'backups')
        os.makedirs(self.generator.backup_dir)

    def generate(self, data):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            ok = self.generator.generate_api(data, 'zone_1')
        return ok, out.getvalue()

    def test_existing_routes_are_kept_and_the_new_one_is_added(self):
        ok, output = self.generate(model_json('Societe', app_name='core'))
        self.assertTrue(ok, output)

        urls = (self.root / 'core' / 'urls.py').read_text(encoding='utf-8')
        ast.parse(urls)
        for original in CORE_URLS.splitlines():
            self.assertIn(original, urls.splitlines())  # rien n'a été supprimé ni modifié
        self.assertIn('from app.core.views.societe_viewset import SocieteViewSet', urls)
        self.assertIn("router.register(r'societes', SocieteViewSet, basename='societes')", urls)
        self.assertLess(urls.index("router.register(r'users'"), urls.index("router.register(r'societes'"))
        self.assertLess(urls.index('from app.core.views.user_viewset'), urls.index('SocieteViewSet\n'))

    def test_regeneration_does_not_duplicate_the_route(self):
        self.assertTrue(self.generate(model_json('Societe', app_name='core'))[0])
        first = (self.root / 'core' / 'urls.py').read_text(encoding='utf-8')
        self.assertTrue(self.generate(model_json('Societe', app_name='core'))[0])
        self.assertEqual((self.root / 'core' / 'urls.py').read_text(encoding='utf-8'), first)

    def test_models_file_does_not_call_get_user_model(self):
        """core/models.py définit User : get_user_model() à l'import empêcherait Django de démarrer."""
        self.assertTrue(self.generate(model_json('Societe', app_name='core'))[0])
        models_py = (self.root / 'core' / 'models.py').read_text(encoding='utf-8')
        self.assertNotIn('get_user_model', models_py)
        self.assertIn('class Societe(models.Model):', models_py)
        self.assertIn('class User(AbstractUser):', models_py)

    def test_route_already_taken_by_another_viewset_is_refused_and_urls_untouched(self):
        ok, output = self.generate(model_json('Utilisateur', app_name='core', resource_plural='users'))
        self.assertFalse(ok)
        self.assertIn('users', output)
        self.assertEqual((self.root / 'core' / 'urls.py').read_text(encoding='utf-8'), CORE_URLS)

    def test_state_does_not_mistake_hand_written_models_for_generated_apis(self):
        state = ImprovedStateManager(state_file=str(self.root / 'state.json'))
        state.app_root = str(self.root)
        with contextlib.redirect_stdout(io.StringIO()):
            state.sync_models_with_state(['User'], app_name='core')
        self.assertEqual(state.state['generated_apis'], {})
