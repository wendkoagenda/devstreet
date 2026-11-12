"""
Le générateur produit des serializers aux champs explicites (jamais fields = '__all__'),
et reste compatible avec les anciens serializers.
"""
import ast

from django.test import SimpleTestCase

from scripts.generator.code_generator import (
    SERIALIZER_FIELDS_PATTERN,
    ImprovedCodeGenerator,
    serializer_field_names,
)
from scripts.generator.schema_validator import FieldConstraint, ModelDefinition


def make_model(*names, extra=None):
    fields = {name: FieldConstraint(name=name, type='CharField', max_length=50) for name in names}
    fields.update(extra or {})
    return ModelDefinition(model_name='Produit', app_name='metier', fields=fields, meta={'resource_plural': 'produits'})


class SerializerFieldNamesTests(SimpleTestCase):
    def test_id_fields_and_system_fields_are_listed(self):
        names = serializer_field_names(make_model('nom', 'prix'))
        self.assertEqual(names, ['id', 'nom', 'prix', 'created_by', 'updated_by', 'created_at', 'updated_at'])

    def test_system_fields_declared_by_the_model_are_not_duplicated(self):
        names = serializer_field_names(make_model('nom', 'created_at'))
        self.assertEqual(names.count('created_at'), 1)
        self.assertEqual(names[:3], ['id', 'nom', 'created_at'])

    def test_id_is_never_duplicated(self):
        self.assertEqual(serializer_field_names(make_model('id', 'nom')).count('id'), 1)


class GeneratedSerializerTests(SimpleTestCase):
    def setUp(self):
        self.generator = ImprovedCodeGenerator()
        self.model = make_model('nom', 'prix')

    def test_generated_class_lists_its_fields_explicitly(self):
        code = self.generator.generate_serializer_class_only(self.model)
        self.assertNotIn("'__all__'", code)
        self.assertIn("fields = ['id', 'nom', 'prix', 'created_by', 'updated_by', 'created_at', 'updated_at']", code)
        ast.parse(code)  # le code généré est valide

    def test_template_lists_its_fields_explicitly(self):
        code = self.generator.env.get_template('serializer.py.j2').render(model=self.model)
        self.assertNotIn("'__all__'", code)
        self.assertIn("fields = ['id', 'nom', 'prix', 'created_by', 'updated_by', 'created_at', 'updated_at']", code)
        self.assertTrue(code.lstrip().startswith('"""'))  # pas de lignes vides parasites en tête
        ast.parse(code)

    def test_template_and_class_generation_agree(self):
        from_template = self.generator.env.get_template('serializer.py.j2').render(model=self.model)
        from_class = self.generator.generate_serializer_class_only(self.model)
        line = next(l for l in from_class.splitlines() if l.strip().startswith('fields ='))
        self.assertIn(line.strip(), from_template)

    def test_no_generator_template_exposes_all_fields(self):
        import pathlib
        templates = pathlib.Path(__file__).resolve().parents[2] / 'scripts' / 'generator' / 'templates'
        for path in templates.glob('*.j2'):
            self.assertNotIn("fields = '__all__'", path.read_text(encoding='utf-8'), path.name)


class SerializerAnchorTests(SimpleTestCase):
    """L'ancre « fields = ... » sert à insérer depth, create et update : elle doit reconnaître les deux formes."""

    def test_pattern_matches_the_legacy_form(self):
        self.assertIsNotNone(SERIALIZER_FIELDS_PATTERN.search("    class Meta:\n        fields = '__all__'\n"))

    def test_pattern_matches_the_explicit_list(self):
        match = SERIALIZER_FIELDS_PATTERN.search("    class Meta:\n        fields = ['id', 'nom']\n        depth = 1\n")
        self.assertEqual(match.group(0), "fields = ['id', 'nom']")

    def test_pattern_ignores_get_fields(self):
        self.assertIsNone(SERIALIZER_FIELDS_PATTERN.search("        fields = super().get_fields()\n"))
