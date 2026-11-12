"""
Relations (fk, o2o, m2m) entre deux modèles de deux applications différentes.
Le champ vit dans l'application source et référence « app_cible.Modèle » ; la partie inverse
de la sérialisation vit dans le serializers.py de l'application cible.
"""
import ast
import contextlib
import io
import os
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from scripts.generator.code_generator import ImprovedCodeGenerator
from scripts.generator.state_manager import ImprovedStateManager


def model_json(name, app_name):
    return {
        'model_name': name,
        'app_name': app_name,
        'fields': [{'name': 'titre', 'type': 'CharField', 'max_length': 100}],
        'meta': {'resource_plural': f'{name.lower()}s'},
    }


class CrossAppRelationTests(SimpleTestCase):
    """Produit (app metier) -> Categorie (app yango), dans un dossier temporaire sans migrations."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        for name in ('metier', 'yango'):
            app = self.root / name
            app.mkdir()
            (app / '__init__.py').write_text('', encoding='utf-8')
            (app / 'models.py').write_text('from django.db import models\n', encoding='utf-8')
            (app / 'serializers.py').write_text('from rest_framework import serializers\n', encoding='utf-8')
            (app / 'urls.py').write_text('from rest_framework import routers\n\nrouter = routers.DefaultRouter()\n\nurlpatterns = router.urls\n', encoding='utf-8')
        self.generator = ImprovedCodeGenerator(app_root=str(self.root), apply_migrations=False)
        self.generator.backup_dir = str(self.root / 'backups')
        os.makedirs(self.generator.backup_dir)
        self.quiet(lambda: self.assertTrue(self.generator.generate_api(model_json('Produit', 'metier'), 'zone_1')))
        self.quiet(lambda: self.assertTrue(self.generator.generate_api(model_json('Categorie', 'yango'), 'zone_1')))

    @staticmethod
    def quiet(call):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            result = call()
        return result, out.getvalue()

    def read(self, app, name):
        return (self.root / app / name).read_text(encoding='utf-8')

    def link(self, rel_type='fk', **extra):
        ok, output = self.quiet(lambda: self.generator.link_models(
            'Produit', 'Categorie', rel_type, app_label='metier', target_app_label='yango', **extra
        ))
        return ok, output

    # -- fk -------------------------------------------------------------------
    def test_fk_field_lives_in_the_source_app_and_references_the_target_app(self):
        ok, output = self.link('fk')
        self.assertTrue(ok, output)

        metier_models = self.read('metier', 'models.py')
        self.assertIn("categorie = models.ForeignKey('yango.Categorie'", metier_models)
        self.assertNotIn('ForeignKey', self.read('yango', 'models.py'))
        for app in ('metier', 'yango'):
            ast.parse(self.read(app, 'models.py'))
            ast.parse(self.read(app, 'serializers.py'))

    def test_source_serializer_gets_forward_part_and_the_target_import(self):
        self.assertTrue(self.link('fk')[0])
        source = self.read('metier', 'serializers.py')
        self.assertIn('from app.yango.models import Categorie', source)
        self.assertIn('# Ajouter les données de la relation categorie si elle existe', source)
        self.assertIn('# Conversion automatique categorie ID vers objet', source)
        self.assertIn("'categorie'", source)  # exposé dans fields
        self.assertNotIn('reverse FK', source)

    def test_target_serializer_gets_the_reverse_part_only(self):
        self.assertTrue(self.link('fk')[0])
        target = self.read('yango', 'serializers.py')
        self.assertIn('# Ajouter les données des relations produits (reverse FK)', target)
        self.assertNotIn('app.metier', target)  # la cible n'importe rien de la source
        self.assertNotIn('Conversion automatique', target)

    def test_relation_records_both_apps(self):
        self.assertTrue(self.link('fk')[0])
        relation = self.generator.last_relation
        self.assertEqual((relation['app_label'], relation['target_app_label']), ('metier', 'yango'))

    def test_linking_again_changes_nothing(self):
        """Relancer la même relation ne duplique ni champ, ni import, ni injection (stable dès le 2e appel)."""
        self.assertTrue(self.link('fk')[0])
        self.assertTrue(self.link('fk')[0])  # le 2e appel peut encore compléter depth = 1 (comportement existant)
        before = {(app, name): self.read(app, name) for app in ('metier', 'yango') for name in ('models.py', 'serializers.py')}
        self.assertTrue(self.link('fk')[0])
        after = {(app, name): self.read(app, name) for app in ('metier', 'yango') for name in ('models.py', 'serializers.py')}
        self.assertEqual(before, after)

    # -- o2o et m2m --------------------------------------------------------------
    def test_one_to_one_and_many_to_many_across_apps(self):
        ok, output = self.link('o2o', field_name='categorie_principale', related_name='produit_principal')
        self.assertTrue(ok, output)
        ok, output = self.link('m2m', field_name='categories', related_name='produits_lies')
        self.assertTrue(ok, output)

        metier_models = self.read('metier', 'models.py')
        self.assertIn("categorie_principale = models.OneToOneField('yango.Categorie'", metier_models)
        self.assertIn("categories = models.ManyToManyField('yango.Categorie'", metier_models)
        self.assertEqual(self.read('metier', 'serializers.py').count('from app.yango.models import Categorie'), 1)
        target = self.read('yango', 'serializers.py')
        self.assertIn('produit_principal', target)
        self.assertIn('produits_lies', target)

    # -- régénération ------------------------------------------------------------
    def test_regenerating_the_target_replays_the_reverse_part(self):
        self.assertTrue(self.link('fk')[0])
        relation = self.generator.last_relation
        ok, output = self.quiet(lambda: self.generator.generate_api(
            model_json('Categorie', 'yango'), 'zone_1', relations=[relation]
        ))
        self.assertTrue(ok, output)
        self.assertIn('# Ajouter les données des relations produits (reverse FK)', self.read('yango', 'serializers.py'))
        self.assertEqual(self.read('metier', 'models.py').count('categorie = models.ForeignKey'), 1)

    def test_regenerating_the_source_replays_the_field_and_the_import(self):
        self.assertTrue(self.link('fk')[0])
        relation = self.generator.last_relation
        ok, output = self.quiet(lambda: self.generator.generate_api(
            model_json('Produit', 'metier'), 'zone_1', relations=[relation]
        ))
        self.assertTrue(ok, output)
        self.assertIn("categorie = models.ForeignKey('yango.Categorie'", self.read('metier', 'models.py'))
        self.assertIn('from app.yango.models import Categorie', self.read('metier', 'serializers.py'))

    # -- échecs ------------------------------------------------------------------
    def test_unknown_target_model_is_refused_without_changes(self):
        before = self.read('metier', 'models.py')
        ok, output = self.quiet(lambda: self.generator.link_models(
            'Produit', 'Inconnu', 'fk', app_label='metier', target_app_label='yango'
        ))
        self.assertFalse(ok)
        self.assertIn("introuvable dans app/yango/models.py", output)
        self.assertEqual(self.read('metier', 'models.py'), before)

    def test_unknown_target_app_is_refused(self):
        ok, output = self.quiet(lambda: self.generator.link_models(
            'Produit', 'Categorie', 'fk', app_label='metier', target_app_label='absente'
        ))
        self.assertFalse(ok)
        self.assertIn('absente', output)

    def test_failure_on_the_target_side_rolls_back_the_source_side(self):
        before = {(app, name): self.read(app, name) for app in ('metier', 'yango') for name in ('models.py', 'serializers.py')}
        original = self.generator._update_serializers_for_relation

        def fail_on_target(*args, **kwargs):
            if kwargs.get('part') == 'target':
                return False
            return original(*args, **kwargs)

        with mock.patch.object(self.generator, '_update_serializers_for_relation', side_effect=fail_on_target):
            ok, output = self.link('fk')
        self.assertFalse(ok)
        self.assertIn('🔄 Rollback', output)
        after = {(app, name): self.read(app, name) for app in ('metier', 'yango') for name in ('models.py', 'serializers.py')}
        self.assertEqual(before, after)
        self.assertIsNone(self.generator.last_relation)


class RelationAppResolutionTests(SimpleTestCase):
    def test_apps_of_both_models_come_from_the_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = ImprovedStateManager(state_file=os.path.join(tmp, 'state.json'))
            state.state['generated_apis'] = {
                'Produit': {'model_name': 'Produit', 'app_name': 'metier'},
                'Categorie': {'model_name': 'Categorie', 'app_name': 'yango'},
                'Ancien': {'model_name': 'Ancien'},
            }
            from scripts.generate_api import resolve_relation_apps

            self.assertEqual(resolve_relation_apps(state, 'Produit', 'Categorie'), ('metier', 'yango'))
            self.assertEqual(resolve_relation_apps(state, 'Categorie', 'Ancien'), ('yango', 'metier'))
