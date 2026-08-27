"""App configuration for the newsapp Django application."""
from django.apps import AppConfig


class NewsappConfig(AppConfig):
    """Configuration for the ``newsapp`` app.

    Connects the app's signal handlers on startup via :meth:`ready`.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newsapp'

    def ready(self):
        """Import the signals module so its receivers get registered."""
        import newsapp.signals  # noqa
