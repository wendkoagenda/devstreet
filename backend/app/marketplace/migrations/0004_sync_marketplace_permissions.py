"""Rattrape les permissions de la marketplace qui manqueraient dans une base : création puis attribution aux rôles.

La migration 0002 a déjà créé ces permissions. Celle-ci est un filet de sécurité idempotent, rejouable sans effet de bord :
elle sert aux bases où une permission a été supprimée, ou où un rôle Admin / Super Admin a été créé après la 0002.
Elle ne crée volontairement aucun rôle (`init_data` ignore un rôle déjà existant et ses permissions de base ne seraient
pas posées) et ne retire rien au retour arrière (la 0002 s'en charge).

Seules les permissions CRUD de l'administration existent : les écrans utilisateur de la marketplace (profil, offres,
candidatures, swipe, calendrier, CV, tableau de bord) ne demandent aucune permission RBAC, chacun n'y gérant que ses données.
"""
from django.db import migrations

# Liste figée : une migration ne doit pas dépendre du code applicatif, qui peut évoluer.
RESOURCES = [
    "companies",
    "skills",
    "profils",
    "offers",
    "candidatures",
    "profil-skills",
    "experiences",
    "prestations",
    "profil-histories",
    "availabilities",
    "reviews",
    "swipes",
    "connections",
]
ACTIONS = ["view", "create", "update", "delete"]
ROLE_NAMES = ["Admin", "Super Admin"]


def _codes():
    return [f"{resource}.{action}" for resource in RESOURCES for action in ACTIONS]


def sync_permissions(apps, schema_editor):
    alias = schema_editor.connection.alias
    Permission = apps.get_model("core", "Permission")
    Role = apps.get_model("core", "Role")

    permissions = []
    for code in _codes():
        resource, action = code.split(".")
        permission, _ = Permission.objects.using(alias).get_or_create(
            code=code, defaults={"description": f"Can {action} {resource}"}
        )
        permissions.append(permission)

    for role in Role.objects.using(alias).filter(name__in=ROLE_NAMES):
        role.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0003_seed_base_skills"),
        ("core", "0001_initial"),
    ]

    operations = [
        # Retour arrière sans effet : les permissions appartiennent à la migration 0002
        migrations.RunPython(sync_permissions, migrations.RunPython.noop),
    ]
