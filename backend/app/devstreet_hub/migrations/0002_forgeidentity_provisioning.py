"""Étend ForgeIdentity : clé opaque, statut, gitea_user_id nullable."""

import uuid

from django.db import migrations, models


def backfill_forge_identities(apps, schema_editor):
    ForgeIdentity = apps.get_model("projects", "ForgeIdentity")
    for identity in ForgeIdentity.objects.all():
        if not identity.provisioning_key:
            identity.provisioning_key = uuid.uuid4()
        if not identity.status:
            identity.status = "linked"
        if identity.gitea_user_id and not identity.linked_at:
            identity.linked_at = identity.created_at
        identity.save(
            update_fields=["provisioning_key", "status", "linked_at"]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="forgeidentity",
            name="provisioning_key",
            field=models.UUIDField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name="forgeidentity",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "En attente de confirmation distante"),
                    ("linked", "Liée"),
                    ("conflict", "Conflit — réparation administrative"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="forgeidentity",
            name="conflict_reason",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="forgeidentity",
            name="linked_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="forgeidentity",
            name="gitea_user_id",
            field=models.BigIntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="forgeidentity",
            name="login",
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.RunPython(backfill_forge_identities, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="forgeidentity",
            name="provisioning_key",
            field=models.UUIDField(unique=True),
        ),
    ]
