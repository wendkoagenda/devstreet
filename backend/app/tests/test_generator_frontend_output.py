"""
Le générateur frontend affiche ses résultats comme le backend : ✅ succès, ❌ erreur, 🔄 rollback, ℹ️ déjà à jour.
La génération tourne sur une copie temporaire des fichiers frontend existants : le dépôt n'est pas modifié.
"""
import contextlib
import io
import shutil
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from scripts.generator.frontend_generator import FrontendCodeGenerator

MODEL = {
    'model_name': 'Yangotest',
    'fields': [{'name': 'titre', 'type': 'CharField', 'max_length': 200}],
    'meta': {'resource_plural': 'yangotests'},
}


class FrontendGenerationOutputTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = Path(self._tmp.name)
        self.generator = FrontendCodeGenerator()
        real_src = self.generator.frontend_src_dir
        self.src = tmp / 'frontend' / 'src'
        for path in self.generator._existing_files().values():
            target = self.src / path.relative_to(real_src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        self.generator.frontend_dir = tmp / 'frontend'
        self.generator.frontend_src_dir = self.src

    def generate(self, data=MODEL):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            ok = self.generator.generate_frontend_interface(data, 'zone_1')
        return ok, out.getvalue()

    def test_success_is_reported_with_icons(self):
        ok, output = self.generate()
        self.assertTrue(ok, output)
        self.assertIn('🚀 Génération frontend pour Yangotest', output)
        self.assertIn('✅ frontend/src/models/yangotest/api.ts généré', output)
        self.assertIn('✅ frontend/src/redux/store.ts mis à jour', output)
        self.assertIn('✅ Vérification réussie', output)
        self.assertIn('✅ Interface frontend générée pour Yangotest !', output)
        self.assertNotIn('❌', output)
        self.assertNotIn('  OK ', output)  # l'ancien format sans icône a disparu

    def test_second_run_reports_files_already_up_to_date(self):
        self.assertTrue(self.generate()[0])
        ok, output = self.generate()
        self.assertTrue(ok, output)
        self.assertIn('ℹ️  frontend/src/redux/store.ts déjà à jour', output)
        self.assertNotIn('store.ts mis à jour', output)

    def test_failure_is_reported_and_rolled_back(self):
        (self.src / 'redux' / 'store.ts').write_text('export const x = 1;\n', encoding='utf-8')
        ok, output = self.generate()
        self.assertFalse(ok)
        self.assertIn('❌ Erreur pendant la génération frontend', output)
        self.assertIn('Repère introuvable dans store.ts', output)
        self.assertIn('🔄 Rollback', output)
        self.assertFalse((self.src / 'models' / 'yangotest').exists())
        self.assertEqual((self.src / 'redux' / 'store.ts').read_text(encoding='utf-8'), 'export const x = 1;\n')

    def test_invalid_model_is_reported_with_an_error_icon(self):
        ok, output = self.generate({'model_name': 'Yangotest'})
        self.assertFalse(ok)
        self.assertIn('❌ Erreur pendant la génération frontend', output)
