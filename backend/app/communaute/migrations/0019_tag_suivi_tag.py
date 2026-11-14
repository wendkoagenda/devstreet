from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


DEFAULT_TAGS = (
    ('TypeScript', 'typescript'),
    ('Rust', 'rust'),
    ('Python', 'python'),
    ('React', 'react'),
    ('Go', 'go'),
    ('AI Infra', 'ai-infra'),
    ('Kubernetes', 'kubernetes'),
    ('Svelte', 'svelte'),
)


def seed_tags(apps, schema_editor):
    Tag = apps.get_model('communaute', 'Tag')
    for label, slug in DEFAULT_TAGS:
        Tag.objects.get_or_create(
            slug=slug,
            defaults={
                'label': label,
                'created_by': 0,
                'updated_by': 0,
            },
        )


def unseed_tags(apps, schema_editor):
    Tag = apps.get_model('communaute', 'Tag')
    Tag.objects.filter(slug__in=[slug for _, slug in DEFAULT_TAGS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communaute', '0018_media_video_audio'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=48)),
                ('slug', models.SlugField(max_length=64, unique=True)),
                ('created_by', models.IntegerField(default=0, help_text="ID de l'utilisateur créateur", verbose_name='Créé par')),
                ('updated_by', models.IntegerField(default=0, help_text="ID de l'utilisateur ayant modifié", verbose_name='Modifié par')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
                'db_table': 'communaute_tag',
                'ordering': ['label'],
            },
        ),
        migrations.CreateModel(
            name='SuiviTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.IntegerField(help_text="ID de l'utilisateur créateur", verbose_name='Créé par')),
                ('updated_by', models.IntegerField(help_text="ID de l'utilisateur ayant modifié", verbose_name='Modifié par')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags_suivis', to=settings.AUTH_USER_MODEL)),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suivis', to='communaute.tag')),
            ],
            options={
                'verbose_name': 'Suivi de tag',
                'verbose_name_plural': 'Suivis de tag',
                'db_table': 'communaute_suivi_tag',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='publication',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='publications', to='communaute.tag'),
        ),
        migrations.AddConstraint(
            model_name='suivitag',
            constraint=models.UniqueConstraint(fields=('tag', 'membre'), name='unique_suivi_tag_membre'),
        ),
        migrations.RunPython(seed_tags, unseed_tags),
    ]
