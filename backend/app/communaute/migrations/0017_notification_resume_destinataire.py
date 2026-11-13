import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def purge_orphan_resumes(apps, schema_editor):
    NotificationResume = apps.get_model('communaute', 'NotificationResume')
    NotificationResume.objects.filter(destinataire__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0016_favori_publication'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationresume',
            name='destinataire',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications_resume',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(purge_orphan_resumes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='notificationresume',
            name='destinataire',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications_resume',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='notificationresume',
            constraint=models.UniqueConstraint(
                fields=('destinataire', 'periode_debut'),
                name='uniq_notification_resume_destinataire_jour',
            ),
        ),
    ]
