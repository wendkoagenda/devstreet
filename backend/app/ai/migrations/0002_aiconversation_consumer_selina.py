from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aiconversation",
            name="consumer",
            field=models.CharField(
                choices=[
                    ("hub", "DevStreet Hub"),
                    ("generic", "Générique"),
                    ("selina", "Selina"),
                ],
                default="generic",
                max_length=32,
            ),
        ),
    ]
