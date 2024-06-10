"""Module defining the configuration for the 'competition_app' Django app."""
from django.apps import AppConfig


class CompetitionAppConfig(AppConfig):
    """Configuration class for the 'competition_app' Django app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'competition_app'
