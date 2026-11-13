import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def clear_orphan_messaging_rows(apps, schema_editor):
    """Les seeds générés n'ont pas encore de liens métier."""
    Message = apps.get_model('communaute', 'Message')
    Conversation = apps.get_model('communaute', 'Conversation')
    Message.objects.all().delete()
    Conversation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0006_commentaire_option'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(clear_orphan_messaging_rows, migrations.RunPython.noop),
        migrations.AddField(
            model_name='conversation',
            name='membre_1',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='conversations_comme_membre_1',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='conversation',
            name='membre_2',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='conversations_comme_membre_2',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name='conversation',
            options={
                'ordering': ['-updated_at', '-id'],
                'verbose_name': 'Conversation',
                'verbose_name_plural': 'Conversations',
            },
        ),
        migrations.AddConstraint(
            model_name='conversation',
            constraint=models.UniqueConstraint(
                fields=('membre_1', 'membre_2'),
                name='uniq_conversation_paire',
            ),
        ),
        migrations.AddConstraint(
            model_name='conversation',
            constraint=models.CheckConstraint(
                condition=models.Q(membre_1_id__lt=models.F('membre_2_id')),
                name='conversation_membre_1_lt_membre_2',
            ),
        ),
        migrations.AddField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='messages',
                to='communaute.conversation',
            ),
        ),
        migrations.AddField(
            model_name='message',
            name='auteur',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='messages_prives',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name='message',
            options={
                'ordering': ['sent_at', 'id'],
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
    ]
