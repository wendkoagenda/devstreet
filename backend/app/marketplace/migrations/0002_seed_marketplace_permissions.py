"""Crée les permissions des modèles de la marketplace et les attribue aux rôles Admin et Super Admin.

Les rôles sont créés plus tard par `init_data` sur une base neuve : s'ils n'existent pas encore au moment de la
migration, l'attribution est faite par `init_data` (voir `app.marketplace.permission_codes`). La migration ne crée
volontairement aucun rôle : `init_data` ignore un rôle déjà existant et ses permissions de base ne seraient pas posées.
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


def seed_permissions(apps, schema_editor):
    alias = schema_editor.connection.alias
    Permission = apps.get_model("core", "Permission")
    Role = apps.get_model("core", "Role")

    permissions = []
    for code in _codes():
        permission, _ = Permission.objects.using(alias).get_or_create(
            code=code, defaults={"description": f"Can {code.split('.')[1]} {code.split('.')[0]}"}
        )
        permissions.append(permission)

    for role in Role.objects.using(alias).filter(name__in=ROLE_NAMES):
        role.permissions.add(*permissions)


def unseed_permissions(apps, schema_editor):
    """Retire les permissions (les liens avec les rôles disparaissent avec elles)."""
    Permission = apps.get_model("core", "Permission")
    Permission.objects.using(schema_editor.connection.alias).filter(code__in=_codes()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0001_initial"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_permissions, unseed_permissions),
    ]
