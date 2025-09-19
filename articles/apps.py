from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "articles"

    def ready(self):
        # Ensure signals and group/permission bootstrapping are registered
        from . import signals 
        from .bootstrap import ensure_groups_and_permissions 
        ensure_groups_and_permissions()