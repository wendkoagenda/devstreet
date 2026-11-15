"""Reseed showcase : pose account_type (sinon le front force /onboarding).

La 0012 a pu tourner avant le fix seed → comptes @showcase sans type = UI vide.
Idempotent : seed_showcase met à jour les users existants.
"""

from django.core.management import call_command
from django.db import migrations


def reseed_showcase(apps, schema_editor):
    """Réapplique le showcase (forum + marketplace + Hub) avec account_type."""
    call_command("seed_showcase", allow_non_debug=True)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_seed_showcase"),
        ("marketplace", "0009_backfill_account_types"),
    ]

    operations = [
        migrations.RunPython(reseed_showcase, migrations.RunPython.noop),
    ]
