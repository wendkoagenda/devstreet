import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0011_espace_photo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageGroupe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texte', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.IntegerField(help_text="ID de l'utilisateur créateur", verbose_name='Créé par')),
                ('updated_by', models.IntegerField(help_text="ID de l'utilisateur ayant modifié", verbose_name='Modifié par')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages_groupe', to=settings.AUTH_USER_MODEL)),
                ('espace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_groupe', to='communaute.espace')),
            ],
            options={
                'verbose_name': 'Message de groupe',
                'verbose_name_plural': 'Messages de groupe',
                'db_table': 'communaute_message_groupe',
                'ordering': ['sent_at', 'id'],
            },
        ),
    ]
