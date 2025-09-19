"""
Django app configuration for the articles application.
"""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration for the articles app with signal and permission setup."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "articles"

    def ready(self):
        """Initialize signals and bootstrap groups/permissions when app is ready."""
        # Ensure signals and group/permission bootstrapping are registered
        from . import signals 
        from .bootstrap import ensure_groups_and_permissions 
        ensure_groups_and_permissions()