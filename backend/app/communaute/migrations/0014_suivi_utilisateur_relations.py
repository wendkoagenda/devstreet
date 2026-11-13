import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def purge_orphan_suivis(apps, schema_editor):
    """Supprime les stubs générés sans suiveur/suivi avant de rendre les FK obligatoires."""
    SuiviUtilisateur = apps.get_model('communaute', 'SuiviUtilisateur')
    SuiviUtilisateur.objects.filter(
        models.Q(suiveur__isnull=True) | models.Q(suivi__isnull=True)
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0013_message_groupe_reply_reactions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='suiviutilisateur',
            name='suivi',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='suivis_recus',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='suiviutilisateur',
            name='suiveur',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='suivis_emis',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(purge_orphan_suivis, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='suiviutilisateur',
            name='suivi',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='suivis_recus',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='suiviutilisateur',
            name='suiveur',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='suivis_emis',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='suiviutilisateur',
            constraint=models.UniqueConstraint(
                fields=('suiveur', 'suivi'),
                name='uniq_suivi_suiveur_suivi',
            ),
        ),
    ]
