import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def clear_orphan_espace_rows(apps, schema_editor):
    """Les seeds générés n'ont pas encore de liens métier."""
    ParticipationEspace = apps.get_model('communaute', 'ParticipationEspace')
    ParticipationEspace.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0008_publication_hub_link'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(clear_orphan_espace_rows, migrations.RunPython.noop),
        migrations.AddField(
            model_name='participationespace',
            name='espace',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='participations',
                to='communaute.espace',
            ),
        ),
        migrations.AddField(
            model_name='participationespace',
            name='membre',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='participations_espace',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='participationespace',
            constraint=models.UniqueConstraint(
                fields=('espace', 'membre'),
                name='uniq_participation_espace_membre',
            ),
        ),
        migrations.AddField(
            model_name='publication',
            name='espace',
            field=models.ForeignKey(
                blank=True,
                help_text='Espace (communauté/chaîne) ; null = fil général',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='publications',
                to='communaute.espace',
            ),
        ),
    ]
