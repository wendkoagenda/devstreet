from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0014_suivi_utilisateur_relations'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='membre_1_lu_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='membre_2_lu_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participationespace',
            name='lu_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Dernière visite (chat communauté ou fil chaîne)',
                null=True,
            ),
        ),
    ]
