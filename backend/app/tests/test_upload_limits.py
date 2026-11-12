"""
Limites de téléversement : plafond de taille refusé avant lecture, extensions obligatoires, plafond par champ,
et générateur qui n'accepte pas un champ fichier sans liste d'extensions.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings

from app.metier.utils import file_field_utils
from scripts.generator import field_utils as generator_field_utils
from scripts.generator.schema_validator import SchemaValidator

MB = 1024 * 1024


class RequestSizeLimitTests(SimpleTestCase):
    def post(self, **extra):
        return self.client.post('/api/auth/csrf', data='{}', content_type='application/json', **extra)

    @override_settings(UPLOAD_MAX_SIZE_MB=2)
    def test_a_request_above_the_ceiling_is_refused_before_it_is_read(self):
        response = self.post(CONTENT_LENGTH=str(4 * MB))
        self.assertEqual(response.status_code, 413)
        self.assertIn('2 Mo', response.json()['error'])

    @override_settings(UPLOAD_MAX_SIZE_MB=2)
    def test_the_multipart_overhead_is_tolerated(self):
        self.assertNotEqual(self.post(CONTENT_LENGTH=str(2 * MB + 1024)).status_code, 413)

    def test_a_normal_request_goes_through(self):
        self.assertNotIn(self.post().status_code, (400, 413))

    def test_a_malformed_content_length_is_refused(self):
        response = self.post(CONTENT_LENGTH='douze')
        self.assertEqual(response.status_code, 400)

    def test_ceiling_is_the_same_in_the_application_and_in_the_generator(self):
        self.assertEqual(settings.UPLOAD_MAX_SIZE_MB, file_field_utils.MAX_UPLOAD_SIZE_MB)
        self.assertEqual(settings.UPLOAD_MAX_SIZE_MB, generator_field_utils.MAX_UPLOAD_SIZE_MB)


class UploadValidationTests(SimpleTestCase):
    def upload(self, name='doc.pdf', size=10):
        return SimpleUploadedFile(name, b'x' * size)

    def test_an_allowed_extension_is_accepted(self):
        file_field_utils._validate_upload(self.upload('doc.PDF'), ['.pdf'], 5)

    def test_another_extension_is_refused(self):
        with self.assertRaisesMessage(ValidationError, 'Extension non autorisée'):
            file_field_utils._validate_upload(self.upload('script.php'), ['.pdf'], 5)

    def test_a_file_without_extension_is_refused(self):
        with self.assertRaises(ValidationError):
            file_field_utils._validate_upload(self.upload('sans_extension'), ['.pdf'], 5)

    def test_no_configured_extension_means_nothing_is_accepted(self):
        with self.assertRaisesMessage(ValidationError, "Aucune extension de fichier n'est autorisée"):
            file_field_utils._validate_upload(self.upload(), [], 5)

    def test_the_field_size_limit_applies(self):
        with self.assertRaisesMessage(ValidationError, 'trop volumineux'):
            file_field_utils._validate_upload(self.upload(size=2 * MB), ['.pdf'], 1)

    def test_a_field_cannot_raise_the_absolute_ceiling(self):
        too_big = self.upload(size=(file_field_utils.MAX_UPLOAD_SIZE_MB + 1) * MB)
        with self.assertRaisesMessage(ValidationError, 'trop volumineux'):
            file_field_utils._validate_upload(too_big, ['.pdf'], 500)


class GeneratorUploadRulesTests(SimpleTestCase):
    def model(self, **file_field):
        return {'model_name': 'Document', 'app_name': 'metier', 'meta': {'resource_plural': 'documents'},
                'fields': [{'name': 'titre', 'type': 'CharField', 'max_length': 50},
                           {'name': 'fichier', 'type': 'FileField', **file_field}]}

    def test_a_file_field_needs_its_allowed_extensions(self):
        with self.assertRaisesMessage(ValueError, 'allowed_extensions est obligatoire'):
            SchemaValidator.validate_model(self.model())
        with self.assertRaisesMessage(ValueError, 'allowed_extensions est obligatoire'):
            SchemaValidator.validate_model(self.model(allowed_extensions=[]))

    def test_a_file_field_with_extensions_is_valid_and_gets_the_default_size(self):
        definition = SchemaValidator.validate_model(self.model(allowed_extensions=['pdf', '.PNG']))
        field = definition.fields['fichier']
        self.assertEqual(field.allowed_extensions, ['.pdf', '.png'])
        self.assertEqual(field.max_size_mb, 10)

    def test_a_size_above_the_ceiling_is_refused(self):
        with self.assertRaisesMessage(ValueError, 'dépasse le plafond'):
            SchemaValidator.validate_model(self.model(allowed_extensions=['.pdf'], max_size_mb=26))

    def test_the_ceiling_itself_is_allowed(self):
        SchemaValidator.validate_model(self.model(allowed_extensions=['.pdf'], max_size_mb=25))

    def test_models_of_the_repository_remain_valid(self):
        import json
        from pathlib import Path
        zones = Path(__file__).resolve().parents[2] / 'scripts' / 'models_zones'
        for path in zones.glob('*/*.json'):
            with self.subTest(model=path.name):
                SchemaValidator.validate_model(json.loads(path.read_text(encoding='utf-8')))
