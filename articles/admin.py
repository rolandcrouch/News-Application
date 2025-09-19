"""Admin setup for User, Publisher, Article, Newsletter."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Publisher, Article, Newsletter


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Custom admin for the project's User model."""

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role & Reader Fields", {
            "fields": (
                "role",
                "subscriptions_publishers",
                "subscriptions_journalists",
            )
        }),
        ("Editor Fields", {
            "fields": (
                "affiliated_publisher",
            )
        }),
    )

    list_display = (
        "username",
        "email",
        "role",
        "affiliated_publisher",
        "is_staff",
        "is_active",
        "get_independent_articles_count",
        "get_independent_newsletters_count",
    )

    @admin.display(description="Independent Articles")
    def get_independent_articles_count(self, obj):
        """Display count of independent articles for journalists."""
        if obj.role == obj.Roles.JOURNALIST:
            return obj.get_independent_articles().count()
        return "-"

    @admin.display(description="Independent Newsletters")
    def get_independent_newsletters_count(self, obj):
        """Display count of independent newsletters for journalists."""
        if obj.role == obj.Roles.JOURNALIST:
            return obj.get_independent_newsletters().count()
        return "-"

    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )

    search_fields = ("username", "email")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin for publishers with editors and journalists."""

    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("editors", "journalists")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin for articles, including approval fields."""

    list_display = (
        "title",
        "author",
        "publisher",
        "is_approved",
        "approved_by",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "publisher",
        "author",
        "approved_by",
        "created_at",
    )

    search_fields = (
        "title",
        "author__username",
        "publisher__name",
    )

    autocomplete_fields = ("author", "publisher", "approved_by")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin for newsletters."""

    list_display = (
        "subject",
        "author",
        "publisher",
        "created_at",
    )

    list_filter = ("publisher", "author", "created_at")

    search_fields = (
        "subject",
        "author__username",
        "publisher__name",
    )

    autocomplete_fields = ("author", "publisher")