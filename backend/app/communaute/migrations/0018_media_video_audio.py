from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0017_notification_resume_destinataire'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentaire',
            name='texte',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='imagepublication',
            name='kind',
            field=models.CharField(
                choices=[('IMAGE', 'Image'), ('VIDEO', 'Vidéo')],
                default='IMAGE',
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name='MediaCommentaire',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'kind',
                    models.CharField(
                        choices=[
                            ('IMAGE', 'Image'),
                            ('VIDEO', 'Vidéo'),
                            ('AUDIO', 'Audio'),
                        ],
                        max_length=10,
                    ),
                ),
                ('url', models.URLField()),
                (
                    'texte_alternatif',
                    models.CharField(blank=True, default='', max_length=200),
                ),
                ('position', models.PositiveIntegerField(default=0)),
                (
                    'created_by',
                    models.IntegerField(
                        help_text="ID de l'utilisateur créateur",
                        verbose_name='Créé par',
                    ),
                ),
                (
                    'updated_by',
                    models.IntegerField(
                        help_text="ID de l'utilisateur ayant modifié",
                        verbose_name='Modifié par',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='Date de création'
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True, verbose_name='Date de modification'
                    ),
                ),
                (
                    'commentaire',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='medias',
                        to='communaute.commentaire',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Média de commentaire',
                'verbose_name_plural': 'Médias de commentaire',
                'db_table': 'communaute_media_commentaire',
                'ordering': ['position', 'id'],
            },
        ),
    ]
