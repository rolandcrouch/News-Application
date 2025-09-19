from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.utils import OperationalError, ProgrammingError


def ensure_groups_and_permissions():
    """
    Create role groups and assign model permissions.
    - Reader:     view Article, Newsletter
    - Editor:     view/change/delete Article, Newsletter
    - Journalist: add/view/change/delete Article, Newsletter
    """
    try:
        from .models import Article, Newsletter
    except Exception:
        # During early migrations, models may not be ready
        return

    try:
        article_ct = ContentType.objects.get_for_model(Article)
        newsletter_ct = ContentType.objects.get_for_model(
            Newsletter
        )
    except (OperationalError, ProgrammingError):
        # DB not ready (e.g., migrate not yet run)
        return

    perms_by_codename = Permission.objects.filter(
        content_type__in=[article_ct, newsletter_ct]
    )

    def get_perms(model_ct, codenames):
        """Return list of permissions by content type and codename."""
        return list(
            perms_by_codename.filter(
                content_type=model_ct,
                codename__in=codenames
            )
        )

    # Groups
    reader_group, _ = Group.objects.get_or_create(name="Reader")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    journalist_group, _ = Group.objects.get_or_create(
        name="Journalist"
    )

    # Permissions
    reader_perms = (
        get_perms(article_ct, ["view_article"]) +
        get_perms(newsletter_ct, ["view_newsletter"])
    )

    editor_perms = (
        get_perms(
            article_ct,
            ["view_article", "change_article", "delete_article"]
        ) +
        get_perms(
            newsletter_ct,
            ["view_newsletter", "change_newsletter",
             "delete_newsletter"]
        )
    )

    journalist_perms = (
        get_perms(
            article_ct,
            ["add_article", "view_article", "change_article",
             "delete_article"]
        ) +
        get_perms(
            newsletter_ct,
            ["add_newsletter", "view_newsletter", "change_newsletter",
             "delete_newsletter"]
        )
    )

    reader_group.permissions.set(reader_perms)
    editor_group.permissions.set(editor_perms)
    journalist_group.permissions.set(journalist_perms)