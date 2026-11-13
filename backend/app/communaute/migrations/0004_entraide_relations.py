import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def clear_orphan_confirmations(apps, schema_editor):
    """Les confirmations seedées n'ont pas encore de cible métier."""
    ConfirmationAide = apps.get_model('communaute', 'ConfirmationAide')
    ConfirmationAide.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("communaute", "0003_commentaires_likes_relations"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(clear_orphan_confirmations, migrations.RunPython.noop),
        migrations.AddField(
            model_name="publication",
            name="reponse_acceptee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="publications_acceptees",
                to="communaute.commentaire",
            ),
        ),
        migrations.AddField(
            model_name="confirmationaide",
            name="commentaire",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="confirmations_aide",
                to="communaute.commentaire",
            ),
        ),
        migrations.AddField(
            model_name="confirmationaide",
            name="membre",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="confirmations_aide",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="confirmationaide",
            constraint=models.UniqueConstraint(
                fields=("commentaire", "membre"),
                name="unique_confirmation_aide_commentaire_membre",
            ),
        ),
    ]
