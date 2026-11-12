# Generated manually for Git device auth (CLI ↔ DevStreet).

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0002_forgeidentity_provisioning"),
    ]

    operations = [
        migrations.CreateModel(
            name="GitConnectedComputer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=120)),
                ("forge_login", models.CharField(max_length=40)),
                ("gitea_token_id", models.BigIntegerField()),
                ("token_last_eight", models.CharField(max_length=8)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Actif"), ("revoked", "Révoqué")],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="git_connected_computers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "projects_git_connected_computer",
            },
        ),
        migrations.CreateModel(
            name="GitDeviceAuthRequest",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("computer_name", models.CharField(max_length=120)),
                ("hub_base_url", models.URLField(max_length=400)),
                ("code_challenge", models.CharField(max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "En attente"),
                            ("authorized", "Autorisée"),
                            ("denied", "Refusée"),
                            ("expired", "Expirée"),
                            ("consumed", "Consommée"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("grant_payload", models.TextField(blank=True, default="")),
                ("poll_count", models.PositiveIntegerField(default=0)),
                ("last_poll_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                (
                    "connected_computer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="auth_requests",
                        to="projects.gitconnectedcomputer",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="git_device_auth_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "projects_git_device_auth_request",
            },
        ),
        migrations.AddIndex(
            model_name="gitconnectedcomputer",
            index=models.Index(
                fields=["user", "status"], name="projects_gi_user_id_7f2a1c_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="gitconnectedcomputer",
            constraint=models.UniqueConstraint(
                fields=("user", "gitea_token_id"), name="unique_user_gitea_token"
            ),
        ),
        migrations.AddIndex(
            model_name="gitdeviceauthrequest",
            index=models.Index(
                fields=["status", "expires_at"],
                name="projects_gi_status_3c8e2b_idx",
            ),
        ),
    ]
