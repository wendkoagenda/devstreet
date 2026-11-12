from django.apps import AppConfig


class DevStreetHubConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.devstreet_hub"

    # Label historique conservé : les tables et migrations sont déjà appliquées.
    label = "projects"
    verbose_name = "DevStreet Hub"
