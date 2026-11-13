from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0010_lien_invitation_espace_admins'),
    ]

    operations = [
        migrations.AddField(
            model_name='espace',
            name='photo',
            field=models.CharField(
                blank=True,
                default='',
                help_text='URL ou chemin de la photo de profil de l’espace',
                max_length=500,
            ),
        ),
    ]
