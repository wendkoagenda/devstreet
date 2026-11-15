"""Reseed showcase resilient : le forum ne doit plus etre annule si Hub echoue.

Sur prod, 0012/0013 ont pu rollback (transaction) → 0 compte showcase.
atomic=False + seed_showcase tolerant aux echecs Hub/marketplace.
"""

from django.core.management import call_command
from django.db import migrations


def reseed_showcase(apps, schema_editor):
    """Peuple forum (+ marketplace/Hub best-effort) avec account_type."""
    call_command("seed_showcase", allow_non_debug=True)


class Migration(migrations.Migration):

    # Les commandes seed commitent elles-memes : ne pas tout annuler si Hub plante.
    atomic = False

    dependencies = [
        ("core", "0013_reseed_showcase_account_types"),
    ]

    operations = [
        migrations.RunPython(reseed_showcase, migrations.RunPython.noop),
    ]
