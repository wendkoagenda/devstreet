from django.db import migrations


EXTRA_TAGS = (
    ('AI', 'ai'),
    ('Embeddings', 'embeddings'),
    ('Models', 'models'),
    ('Machine Learning', 'machine-learning'),
    ('LLM', 'llm'),
    ('JavaScript', 'javascript'),
)


def seed_extra_tags(apps, schema_editor):
    Tag = apps.get_model('communaute', 'Tag')
    for label, slug in EXTRA_TAGS:
        Tag.objects.get_or_create(
            slug=slug,
            defaults={
                'label': label,
                'created_by': 0,
                'updated_by': 0,
            },
        )


def unseed_extra_tags(apps, schema_editor):
    Tag = apps.get_model('communaute', 'Tag')
    Tag.objects.filter(slug__in=[slug for _, slug in EXTRA_TAGS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0019_tag_suivi_tag'),
    ]

    operations = [
        migrations.RunPython(seed_extra_tags, unseed_extra_tags),
    ]
