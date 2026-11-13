from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Chemin relatif de la photo de profil dans le stockage média',
                max_length=512,
            ),
        ),
    ]
