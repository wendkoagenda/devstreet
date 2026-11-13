import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0015_unread_cursors'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriPublication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.IntegerField(help_text="ID de l'utilisateur créateur", verbose_name='Créé par')),
                ('updated_by', models.IntegerField(help_text="ID de l'utilisateur ayant modifié", verbose_name='Modifié par')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoris_publication', to=settings.AUTH_USER_MODEL)),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoris', to='communaute.publication')),
            ],
            options={
                'verbose_name': 'Favori de publication',
                'verbose_name_plural': 'Favoris de publication',
                'db_table': 'communaute_favori_publication',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='favoripublication',
            constraint=models.UniqueConstraint(
                fields=('publication', 'membre'),
                name='unique_favori_publication_membre',
            ),
        ),
    ]
