from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_user_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='banner',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Chemin relatif de la bannière de profil dans le stockage média',
                max_length=512,
            ),
        ),
    ]
