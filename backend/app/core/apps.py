"""
Django app configuration for the core application.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration for the core application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.core'
    verbose_name = 'Core'

    def ready(self):
        """
        Perform initialization tasks when the app is ready.
        """
        # Import signal handlers if any
        pass