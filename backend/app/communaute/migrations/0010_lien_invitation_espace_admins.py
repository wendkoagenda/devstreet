import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def clear_orphan_liens(apps, schema_editor):
    LienInvitation = apps.get_model('communaute', 'LienInvitation')
    LienInvitation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('communaute', '0009_espace_participation_publication'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(clear_orphan_liens, migrations.RunPython.noop),
        migrations.AddField(
            model_name='lieninvitation',
            name='espace',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='liens_invitation',
                to='communaute.espace',
            ),
        ),
        migrations.AddField(
            model_name='lieninvitation',
            name='cree_par',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='liens_invitation_crees',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
