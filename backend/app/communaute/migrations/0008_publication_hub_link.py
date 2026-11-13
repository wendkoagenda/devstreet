from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0007_conversation_message_relations'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='hub_request_key',
            field=models.CharField(
                blank=True,
                help_text="Clé d'idempotence DevStreet Hub (ProjectDiscussionLink.request_key)",
                max_length=64,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name='publication',
            name='projet_id',
            field=models.IntegerField(
                blank=True,
                db_index=True,
                help_text='Projet Hub lié (dénormalisé depuis ProjectDiscussionLink)',
                null=True,
            ),
        ),
    ]
