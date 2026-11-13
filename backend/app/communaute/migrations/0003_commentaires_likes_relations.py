import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("communaute", "0002_publication_auteur_images"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="commentaire",
            name="auteur",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="commentaires",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="commentaire",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reponses",
                to="communaute.commentaire",
            ),
        ),
        migrations.AddField(
            model_name="commentaire",
            name="publication",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="commentaires",
                to="communaute.publication",
            ),
        ),
        migrations.AddField(
            model_name="likecommentaire",
            name="commentaire",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likes",
                to="communaute.commentaire",
            ),
        ),
        migrations.AddField(
            model_name="likecommentaire",
            name="membre",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likes_commentaire",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="likepublication",
            name="membre",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likes_publication",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="likepublication",
            name="publication",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likes",
                to="communaute.publication",
            ),
        ),
        migrations.AddConstraint(
            model_name="likecommentaire",
            constraint=models.UniqueConstraint(
                fields=("commentaire", "membre"),
                name="unique_like_commentaire_membre",
            ),
        ),
        migrations.AddConstraint(
            model_name="likepublication",
            constraint=models.UniqueConstraint(
                fields=("publication", "membre"),
                name="unique_like_publication_membre",
            ),
        ),
    ]
