"""
Le code que produit le générateur respecte les règles du scanner : liste paginée avec recherche et tri contrôlés,
permissions sans erreur 500 pour un visiteur anonyme, aucune erreur interne renvoyée au client.
"""
import ast
from pathlib import Path

from django.test import SimpleTestCase

from scripts.generator.code_generator import ImprovedCodeGenerator
from scripts.generator.schema_validator import FieldConstraint, ModelDefinition


def make_model(fields):
    return ModelDefinition(model_name='Produit', app_name='metier', fields=fields,
                           meta={'resource_plural': 'produits'})


TEXT_AND_NUMBER = {
    'nom': FieldConstraint(name='nom', type='CharField', max_length=50),
    'note': FieldConstraint(name='note', type='TextField'),
    'prix': FieldConstraint(name='prix', type='DecimalField', max_digits=8, decimal_places=2),
}


class GeneratedTemplatesTests(SimpleTestCase):
    def setUp(self):
        self.generator = ImprovedCodeGenerator()

    def render(self, template, fields=None):
        model = make_model(fields or TEXT_AND_NUMBER)
        code = self.generator.env.get_template(template).render(model=model, resource_plural='produits')
        return code

    def test_every_backend_template_renders_valid_python(self):
        for template in ('repository.py.j2', 'service.py.j2', 'interface.py.j2', 'viewset.py.j2',
                         'permissions.py.j2', 'serializer.py.j2'):
            with self.subTest(template=template):
                ast.parse(self.render(template))

    def test_repository_declares_searchable_and_sortable_fields(self):
        code = self.render('repository.py.j2')
        self.assertIn("SEARCH_FIELDS = ('nom', 'note',)", code)
        self.assertIn("ORDERING_FIELDS = ('id', 'nom', 'note', 'prix', 'created_at', 'updated_at',)", code)

    def test_repository_without_text_fields_stays_valid(self):
        code = self.render('repository.py.j2', {'prix': TEXT_AND_NUMBER['prix']})
        ast.parse(code)
        self.assertIn('SEARCH_FIELDS = ()', code)

    def test_json_and_many_to_many_fields_are_not_sortable(self):
        fields = {'tags': FieldConstraint(name='tags', type='JSONField'),
                  'nom': FieldConstraint(name='nom', type='CharField', max_length=10)}
        code = self.render('repository.py.j2', fields)
        ordering = next(line for line in code.splitlines() if 'ORDERING_FIELDS =' in line)
        self.assertNotIn("'tags'", ordering)
        self.assertIn("'nom'", ordering)

    def test_repository_refuses_unknown_ordering(self):
        code = self.render('repository.py.j2')
        self.assertIn('raise ValueError', code)
        self.assertIn("return queryset.order_by('id')", code)  # tri par défaut stable pour la pagination

    def test_service_and_interface_share_the_new_signature(self):
        for template in ('service.py.j2', 'interface.py.j2'):
            code = self.render(template)
            self.assertIn('def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None)', code, template)

    def test_viewset_list_is_paginated(self):
        code = self.render('viewset.py.j2')
        self.assertIn('self.paginate_queryset(', code)
        self.assertIn('self.get_paginated_response(', code)
        self.assertIn("{'error': 'Tri invalide'}", code)

    def test_generated_code_passes_the_security_rules(self):
        """Le scanner lui-même ne trouve rien à redire au code généré (détail d'exception, pagination, __all__)."""
        from scripts.security_scan.models import ScanFile
        from scripts.security_scan.registry import RULES, all_rules
        all_rules()
        checks = {
            'viewset.py.j2': ('backend/app/metier/views/produit_viewset.py', ('API-001', 'API-003', 'RT-005', 'RT-004')),
            'serializer.py.j2': ('backend/app/metier/serializers.py', ('API-002',)),
        }
        for template, (path, rule_ids) in checks.items():
            code = self.render(template)
            for rule_id in rule_ids:
                with self.subTest(template=template, rule=rule_id):
                    self.assertEqual([h.message for h in RULES[rule_id].check(ScanFile(path, code, None))], [])

    def test_permissions_reject_anonymous_users_without_crashing(self):
        code = self.render('permissions.py.j2')
        self.assertEqual(code.count('request.user.is_authenticated'), 4)

    def test_generated_tests_expect_the_paginated_format(self):
        template = self.generator.env.loader.get_source(self.generator.env, 'tests.py.j2')[0]
        self.assertIn("self.assertIn('results', response.data)", template)
        self.assertNotIn('self.assertIsInstance(response.data, list)', template)


class GeneratedFrontendTemplatesTests(SimpleTestCase):
    """Les templates frontend du générateur produisent exactement le tableau paginé de référence."""

    def setUp(self):
        self.generator = ImprovedCodeGenerator()

    def test_data_table_template_matches_the_reference_table(self):
        rendered = self.generator.env.get_template('frontend/data-table.tsx.j2').render(
            model_name_plural_pascal='Elitests', model_name_pascal='Elitest', model_name_lower='elitest')
        reference = (Path(__file__).parent / 'fixtures/generated-data-table.tsx').read_text(encoding='utf-8')
        self.assertEqual(rendered.replace('\r\n', '\n').strip(), reference.replace('\r\n', '\n').strip())

    def test_data_table_template_is_server_driven(self):
        rendered = self.generator.env.get_template('frontend/data-table.tsx.j2').render(
            model_name_plural_pascal='Produits', model_name_pascal='Produit', model_name_lower='produit')
        for expected in ('manualPagination: true', 'manualSorting: true', 'manualFiltering: true', 'useGetProduitsQuery({'):
            self.assertIn(expected, rendered)
        for forbidden in ('getPaginationRowModel', 'getFilteredRowModel', 'getSortedRowModel'):
            self.assertNotIn(forbidden, rendered)

    def test_api_template_queries_the_paginated_endpoint(self):
        source = self.generator.env.loader.get_source(self.generator.env, 'frontend/api.ts.j2')[0]
        self.assertIn('Paginated<Get{{ model_name_pascal }}Schema>', source)
        self.assertIn('toQueryString(params)', source)
