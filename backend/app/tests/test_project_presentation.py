from io import BytesIO
from datetime import timedelta
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from app.devstreet_hub.models import AIAnalysis, ProjectImage
from app.devstreet_hub.services.analysis_worker import process_next
from app.devstreet_hub.services.errors import Conflict
from app.devstreet_hub.services.openai_client import validate_presentation
from app.tests.devstreet_hub_base import DevStreetHubAPITestCase


SOURCES = [{'source_id': 'src_01', 'path': 'index.html', 'content': '<h1>Hello World</h1>\n<p>Bonjour</p>'}]
RESULT = {'description': 'Une page de bienvenue en HTML.\n\nElle affiche un message de salutation.',
          'references': [{'source_id': 'src_01', 'line_start': 1, 'line_end': 2, 'reason': 'Page principale'}],
          'unknowns': []}


def picture(name='photo.png'):
    stream = BytesIO()
    Image.new('RGB', (24, 24), 'white').save(stream, 'PNG')
    return SimpleUploadedFile(name, stream.getvalue(), content_type='image/png')


@override_settings(DEVSTREET_HUB_AI_INLINE_WORKER=False, DEVSTREET_HUB_AI_PROJECT_DAILY_LIMIT=2, DEVSTREET_HUB_OPENAI_API_KEY='test-only-key', DEVSTREET_HUB_OPENAI_MODEL='model-test')
class PresentationRoutesTests(DevStreetHubAPITestCase):
    def setUp(self):
        super().setUp()
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        settings = override_settings(DEVSTREET_HUB_PRIVATE_IMAGE_ROOT=self.directory.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.item = self.project(status='draft')
        self.url = f'/api/v1/projects/{self.item.pk}/presentation'

    def body(self, **extra):
        self.item.refresh_from_db()
        return {'description': 'Texte libre\n\nAvec des paragraphes.', 'problem': '',
                'base_updated_at': self.item.updated_at.isoformat(), **extra}

    def test_text_only_and_owner_name_are_returned(self):
        response = self.client.put(self.url, self.body(), format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['description'], 'Texte libre\n\nAvec des paragraphes.')
        self.assertEqual(response.data['images'], [])
        self.assertTrue(response.data['owner_display_name'])

    def test_image_reencoded_and_private_access_checked(self):
        response = self.client.put(self.url, self.body(images=[picture()]), format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        image = ProjectImage.objects.get(project=self.item)
        self.assertTrue(image.file.name.endswith('.jpg'))
        self.assertNotIn('media/', response.data['images'][0]['url'])
        url = response.data['images'][0]['url']
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        list(response.streaming_content)
        self.login(self.moussa)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_public_image_visible_without_login_and_removed_after_save(self):
        self.item.status = 'published'
        self.item.save()
        response = self.client.put(self.url, self.body(images=[picture()]), format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        image = ProjectImage.objects.get()
        image_url = response.data['images'][0]['url']
        self.client.force_authenticate(None)
        response = self.client.get(image_url)
        self.assertEqual(response.status_code, 200)
        list(response.streaming_content)
        self.login(self.aicha)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(self.url, self.body(remove_image_ids=[image.pk]), format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(image.file.storage.exists(image.file.name))
        self.assertEqual(self.client.get(image_url).status_code, 404)

    def test_bad_image_does_not_save_text(self):
        invalid = SimpleUploadedFile('attack.svg', b'<svg onload="alert(1)"></svg>', content_type='image/svg+xml')
        response = self.client.put(self.url, self.body(images=[invalid]), format='multipart')
        self.assertEqual(response.status_code, 400)
        self.item.refresh_from_db()
        self.assertEqual(self.item.description, '')
        self.assertEqual(ProjectImage.objects.count(), 0)

    def test_four_images_maximum_across_existing_and_new(self):
        response = self.client.put(self.url, self.body(images=[picture() for _ in range(4)]), format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        response = self.client.put(self.url, self.body(images=[picture()]), format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ProjectImage.objects.count(), 4)

    def test_failed_transaction_removes_uploaded_files_and_preserves_text(self):
        from pathlib import Path

        with patch('app.devstreet_hub.services.presentation_service.record', side_effect=RuntimeError('audit unavailable')):
            with self.assertRaises(RuntimeError):
                self.client.put(self.url, self.body(images=[picture()]), format='multipart')
        self.assertEqual(ProjectImage.objects.count(), 0)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [])
        self.item.refresh_from_db()
        self.assertEqual(self.item.description, '')

    def test_another_projects_image_cannot_be_removed(self):
        response = self.client.put(self.url, self.body(remove_image_ids=[99999]), format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_stale_edit_is_rejected(self):
        body = self.body()
        self.item.description = 'Texte modifie ailleurs'
        with patch('django.utils.timezone.now', return_value=self.item.updated_at + timedelta(seconds=1)):
            self.item.save()
        response = self.client.put(self.url, body, format='multipart')
        self.assertEqual(response.status_code, 409)
        self.item.refresh_from_db()
        self.assertEqual(self.item.description, 'Texte modifie ailleurs')

    def test_non_owner_cannot_edit_even_with_iam(self):
        self.item.status = 'published'
        self.item.save()
        body = self.body()
        self.login(self.moussa)
        self.assertEqual(self.client.put(self.url, body, format='multipart').status_code, 403)

    def request_suggestion(self, text='Mon brouillon'):
        return self.client.post(self.url + '/suggestions', {'description': text, 'language': 'fr'}, format='json')

    def consent(self):
        self.item.ai_consent_at = timezone.now()
        self.item.save()

    def test_suggestion_requires_consent_and_preserves_description(self):
        self.assertEqual(self.request_suggestion().status_code, 409)
        self.consent()
        response = self.request_suggestion()
        self.assertEqual(response.status_code, 202, response.data)
        job = AIAnalysis.objects.get(pk=response.data['id'])
        self.assertEqual(job.prompt_version, 'presentation-v1')
        self.assertIn('Mon brouillon', job.objective)
        self.item.refresh_from_db()
        self.assertEqual(self.item.description, '')

    def test_worker_uses_sources_at_sha_and_never_saves_project_text(self):
        self.consent()
        response = self.request_suggestion()
        forge, ai = Mock(), Mock()
        forge.collect_sources.return_value = SOURCES
        ai.improve_presentation.return_value = (RESULT, 100, 50)
        job = process_next(forge=forge, ai=ai, job_id=response.data['id'])
        self.assertEqual(job.status, 'succeeded')
        self.assertEqual(job.result, RESULT)
        forge.collect_sources.assert_called_once_with(self.item.repository, 'a' * 40)
        ai.generate.assert_not_called()
        self.item.refresh_from_db()
        self.assertEqual(self.item.description, '')
        response = self.client.post(f'/api/v1/projects/{self.item.pk}/tasks/from-analysis', {'analysis_id': job.pk, 'suggestion_index': 0}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_cache_depends_on_draft_and_shares_quota(self):
        self.consent()
        first = self.request_suggestion()
        self.assertEqual(self.request_suggestion().data['id'], first.data['id'])
        self.assertEqual(self.request_suggestion('Autre brouillon').status_code, 202)
        self.assertEqual(self.request_suggestion('Troisieme brouillon').status_code, 429)

    def test_revoked_consent_prevents_worker_result(self):
        self.consent()
        response = self.request_suggestion()
        self.item.ai_consent_at = None
        self.item.save()
        ai = Mock()
        job = process_next(ai=ai, job_id=response.data['id'])
        self.assertEqual(job.status, 'failed')
        ai.improve_presentation.assert_not_called()


class PresentationValidationTests(SimpleTestCase):
    def test_false_citation_rejected(self):
        result = {**RESULT, 'references': [{**RESULT['references'][0], 'source_id': 'unknown'}]}
        with self.assertRaises(Conflict):
            validate_presentation(result, SOURCES)

    def test_forced_lists_and_html_rejected(self):
        for text in ('- Une liste', '<script>alert(1)</script>', '# Titre impose'):
            with self.subTest(text=text), self.assertRaises(Conflict):
                validate_presentation({**RESULT, 'description': text}, SOURCES)

    def test_plain_paragraphs_accepted(self):
        self.assertEqual(validate_presentation(RESULT, SOURCES), RESULT)
