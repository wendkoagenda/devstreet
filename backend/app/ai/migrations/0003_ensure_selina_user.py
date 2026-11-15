from django.db import migrations


def forwards(apps, schema_editor):
    from app.ai.selina_user import ensure_selina_user

    ensure_selina_user()


def backwards(apps, schema_editor):
    User = apps.get_model("core", "User")
    User.objects.filter(username__iexact="selina").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0002_aiconversation_consumer_selina"),
        ("core", "0009_user_account_type"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
