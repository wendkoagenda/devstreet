from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_user_banner'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('google', 'Google'), ('github', 'GitHub')], help_text='Fournisseur OAuth (google, github)', max_length=20)),
                ('provider_user_id', models.CharField(help_text='Identifiant stable chez le fournisseur', max_length=255)),
                ('email', models.EmailField(blank=True, default='', help_text='E-mail renvoyé par le fournisseur au moment de la liaison', max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(help_text='Utilisateur DevStreet lié à ce compte social', on_delete=django.db.models.deletion.CASCADE, related_name='social_accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'core_social_account',
                'ordering': ['provider', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='socialaccount',
            index=models.Index(fields=['user', 'provider'], name='core_social_user_id_5f0e0c_idx'),
        ),
        migrations.AddConstraint(
            model_name='socialaccount',
            constraint=models.UniqueConstraint(fields=('provider', 'provider_user_id'), name='core_social_provider_uid_uniq'),
        ),
    ]
