"""Peuple le showcase (forum + marketplace + Hub) après les schémas métier.

Idempotent : relancer migrate ne duplique pas les données curated.
Mot de passe des comptes showcase : test@123
"""

from django.core.management import call_command
from django.db import migrations


def run_seed_showcase(apps, schema_editor):
    """Données qualitatives Afrique de l'Ouest pour instance vide (prod incluse)."""
    call_command("seed_showcase", allow_non_debug=True)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_username_unique_insensible_casse"),
        ("communaute", "0020_seed_tag_aliases_catalog"),
        ("marketplace", "0008_profil_cv_settings"),
        ("projects", "0005_git_oauth_authorization"),
    ]

    operations = [
        migrations.RunPython(run_seed_showcase, migrations.RunPython.noop),
    ]
