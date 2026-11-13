import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def clear_orphan_choix_rows(apps, schema_editor):
    """Les seeds n'ont pas encore de liens métier."""
    AvisChoix = apps.get_model('communaute', 'AvisChoix')
    OptionPublication = apps.get_model('communaute', 'OptionPublication')
    AvisChoix.objects.all().delete()
    OptionPublication.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0004_entraide_relations'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(clear_orphan_choix_rows, migrations.RunPython.noop),
        migrations.AddField(
            model_name='optionpublication',
            name='publication',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='options',
                to='communaute.publication',
            ),
        ),
        migrations.AlterModelOptions(
            name='optionpublication',
            options={
                'ordering': ['position', 'id'],
                'verbose_name': 'Option de publication',
                'verbose_name_plural': 'Options de publication',
            },
        ),
        migrations.AddField(
            model_name='avischoix',
            name='membre',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='avis_choix',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='avischoix',
            name='option',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='avis',
                to='communaute.optionpublication',
            ),
        ),
        migrations.AddField(
            model_name='publication',
            name='option_retenue',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='publications_retenues',
                to='communaute.optionpublication',
            ),
        ),
    ]
