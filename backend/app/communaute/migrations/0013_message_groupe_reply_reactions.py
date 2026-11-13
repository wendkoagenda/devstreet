import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0012_message_groupe'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='messagegroupe',
            name='reply_to',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reponses',
                to='communaute.messagegroupe',
            ),
        ),
        migrations.AddField(
            model_name='messagegroupe',
            name='supprime_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='ReactionMessageGroupe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emoji', models.CharField(max_length=8)),
                ('created_by', models.IntegerField(help_text="ID de l'utilisateur créateur", verbose_name='Créé par')),
                ('updated_by', models.IntegerField(help_text="ID de l'utilisateur ayant modifié", verbose_name='Modifié par')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions_message_groupe', to=settings.AUTH_USER_MODEL)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='communaute.messagegroupe')),
            ],
            options={
                'verbose_name': 'Réaction message de groupe',
                'verbose_name_plural': 'Réactions messages de groupe',
                'db_table': 'communaute_reaction_message_groupe',
            },
        ),
        migrations.AddConstraint(
            model_name='reactionmessagegroupe',
            constraint=models.UniqueConstraint(
                fields=('message', 'membre'),
                name='unique_reaction_message_groupe_membre',
            ),
        ),
    ]
