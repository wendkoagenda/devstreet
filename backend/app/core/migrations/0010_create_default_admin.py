"""Crée le compte admin par défaut une fois le schéma de User complet (idempotent)."""
from django.core.management import call_command
from django.db import migrations


def create_default_admin(apps, schema_editor):
    call_command('init_data', only_admin=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_user_account_type'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, migrations.RunPython.noop),
    ]
