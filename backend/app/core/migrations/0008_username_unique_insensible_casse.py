"""Nom d'utilisateur unique sans tenir compte de la casse (adresse /profil/<nom>)."""
from collections import defaultdict

from django.db import migrations, models
from django.db.models.functions import Lower

from app.core.username_rules import RESERVED_USERNAMES


def verifier_noms_utilisateur(apps, schema_editor):
    """
    Refuse la migration, avec un rapport lisible, s'il existe des noms en doublon
    à la casse près ou des noms réservés : ils doivent être corrigés à la main.
    """
    User = apps.get_model('core', 'User')

    groupes = defaultdict(list)
    reserves = []
    for pk, username in User.objects.values_list('pk', 'username'):
        cle = (username or '').strip().lower()
        groupes[cle].append((pk, username))
        if cle in RESERVED_USERNAMES:
            reserves.append((pk, username))

    doublons = {cle: comptes for cle, comptes in groupes.items() if len(comptes) > 1}
    if not doublons and not reserves:
        return

    lignes = ["Migration refusée : des noms d'utilisateur doivent être corrigés avant."]
    for cle, comptes in sorted(doublons.items()):
        details = ', '.join(f'#{pk} « {nom} »' for pk, nom in comptes)
        lignes.append(f'- Doublon à la casse près ({cle}) : {details}')
    for pk, nom in reserves:
        lignes.append(f'- Nom réservé : #{pk} « {nom} »')
    raise RuntimeError('\n'.join(lignes))


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_merge_0006_init_data_0006_socialaccount'),
    ]

    operations = [
        migrations.RunPython(verifier_noms_utilisateur, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(
                Lower('username'), name='core_user_username_ci_unique'
            ),
        ),
    ]
