"""Rattrapage des comptes existants : type de compte et rôles selon les profils déjà créés.

- Un membre avec un profil dev et/ou entreprise reçoit le type correspondant et les rôles « Membre Dev » /
  « Membre Entreprise », et perd l'ancien rôle unique.
- Un membre sans aucun profil perd l'ancien rôle et passera par l'assistant à sa prochaine connexion.
- Les comptes d'administration (superutilisateurs, rôles IAM de base) ne sont pas touchés.
"""
from django.db import migrations

from app.core.account_types import (
    ADMIN_ROLE_NAMES,
    LEGACY_MEMBER_ROLE,
    ROLE_DESCRIPTIONS,
    TYPE_DEV,
    TYPE_ENTREPRISE,
    join_types,
    permission_codes_for_role,
    role_names_for,
)


def _ensure_role(apps, role_name):
    Role = apps.get_model('core', 'Role')
    Permission = apps.get_model('core', 'Permission')
    role, _ = Role.objects.get_or_create(
        name=role_name, defaults={'description': ROLE_DESCRIPTIONS.get(role_name, '')}
    )
    for code in sorted(permission_codes_for_role(role_name)):
        perm, _ = Permission.objects.get_or_create(code=code, defaults={'description': f'Permission {code}'})
        role.permissions.add(perm)
    return role


def backfill_account_types(apps, schema_editor):
    User = apps.get_model('core', 'User')
    Role = apps.get_model('core', 'Role')
    Profil = apps.get_model('marketplace', 'Profil')

    legacy = Role.objects.filter(name=LEGACY_MEMBER_ROLE).first()
    members = User.objects.filter(is_superuser=False).exclude(roles__name__in=ADMIN_ROLE_NAMES).distinct()
    for user in members:
        types = set(
            Profil.objects.filter(user_id=user.id, type__in=[TYPE_DEV, TYPE_ENTREPRISE]).values_list('type', flat=True)
        )
        account_type = join_types(types)
        if legacy is not None:
            user.roles.remove(legacy)
        if account_type:
            user.account_type = account_type
            user.save(update_fields=['account_type'])
            for role_name in role_names_for(account_type):
                user.roles.add(_ensure_role(apps, role_name))


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_user_account_type'),
        ('marketplace', '0008_profil_cv_settings'),
    ]

    operations = [
        # Pas de retour arrière des rôles : l'ancien rôle unique n'est volontairement pas restauré.
        migrations.RunPython(backfill_account_types, migrations.RunPython.noop),
    ]
