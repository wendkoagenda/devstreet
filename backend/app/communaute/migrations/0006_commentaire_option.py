from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0005_choix_relations'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentaire',
            name='option',
            field=models.ForeignKey(
                blank=True,
                help_text='Option de débat concernée (publications CHOIX uniquement)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='commentaires',
                to='communaute.optionpublication',
            ),
        ),
    ]
