"""Tests normalisation / canonisation des tags forum."""
from django.contrib.auth import get_user_model
from django.test import TestCase

from app.communaute.models import SuiviTag, Tag
from app.communaute.services.tag_service import TagService

User = get_user_model()


class TagServiceNormalizationTests(TestCase):
    def setUp(self):
        self.service = TagService()
        Tag.objects.get_or_create(
            slug='ai-infra',
            defaults={'label': 'AI Infra', 'created_by': 0, 'updated_by': 0},
        )
        Tag.objects.get_or_create(
            slug='ai',
            defaults={'label': 'AI', 'created_by': 0, 'updated_by': 0},
        )
        Tag.objects.get_or_create(
            slug='embeddings',
            defaults={'label': 'Embeddings', 'created_by': 0, 'updated_by': 0},
        )

    def test_spaces_and_hash_collapse_to_same_slug(self):
        a = self.service.get_or_create('# ia')
        b = self.service.get_or_create('AI')
        c = self.service.get_or_create('  #AI  ')
        self.assertEqual(a.slug, 'ai')
        self.assertEqual(a.id, b.id)
        self.assertEqual(b.id, c.id)

    def test_hyphen_compact_matches_existing(self):
        tag = self.service.get_or_create('ai infra')
        self.assertEqual(tag.slug, 'ai-infra')

    def test_alias_embedding_to_embeddings(self):
        tag = self.service.get_or_create('#embedding')
        self.assertEqual(tag.slug, 'embeddings')

    def test_resolve_dedupes_variants(self):
        tags = self.service.resolve_labels(['# ia', 'AI', 'embedding'])
        slugs = sorted(t.slug for t in tags)
        self.assertEqual(slugs, ['ai', 'embeddings'])

    def test_suivi_is_persisted_per_user(self):
        user = User.objects.create_user(
            username='tagger',
            email='tagger@example.com',
            password='x',
        )
        tag = self.service.get_or_create('rust')
        self.service.ensure_suivi(membre=user, tag=tag)
        self.service.ensure_suivi(membre=user, tag=tag)
        self.assertEqual(
            SuiviTag.objects.filter(membre=user, tag=tag).count(),
            1,
        )
        suivis = self.service.list_suivis(user)
        self.assertEqual([t.slug for t in suivis], [tag.slug])
