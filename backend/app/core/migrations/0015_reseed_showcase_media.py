"""Reseed showcase : photos profil, images/vidéos publications, covers Hub.

Idempotent. force_forum=True pour attacher les médias aux pubs déjà présentes.
atomic=False : les seeds commitent elles-mêmes (même pattern que 0014).
"""

from django.core.management import call_command
from django.db import migrations


def reseed_showcase_media(apps, schema_editor):
    """Réapplique forum/marketplace/Hub avec médias (URLs externes + covers Hub)."""
    call_command(
        "seed_showcase",
        allow_non_debug=True,
        force_forum=True,
    )


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("core", "0014_reseed_showcase_resilient"),
    ]

    operations = [
        migrations.RunPython(reseed_showcase_media, migrations.RunPython.noop),
    ]
