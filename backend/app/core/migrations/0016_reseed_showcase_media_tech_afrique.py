"""Reseed showcase : portraits afro + visuels / vidéos tech (corrige picsum/randomuser).

force_forum=True pour réécrire les médias des publications.
atomic=False : seeds commitent elles-mêmes.
"""

from django.core.management import call_command
from django.db import migrations


def reseed_showcase_media_tech(apps, schema_editor):
    """Remplace médias hors-thème par portraits africains et images tech."""
    call_command(
        "seed_showcase",
        allow_non_debug=True,
        force_forum=True,
    )


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("core", "0015_reseed_showcase_media"),
    ]

    operations = [
        migrations.RunPython(reseed_showcase_media_tech, migrations.RunPython.noop),
    ]
