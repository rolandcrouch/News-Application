from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user with roles and role-specific fields.
    """

    class Roles(models.TextChoices):
        READER = "reader", _("Reader")
        EDITOR = "editor", _("Editor")
        JOURNALIST = "journalist", _("Journalist")

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.READER,
        help_text=_("Determines permissions and group assignment."),
    )

    # Reader-only fields
    subscriptions_publishers = models.ManyToManyField(
        "Publisher",
        related_name="subscribers",
        blank=True,
        help_text=_("Publishers this user follows (Reader role)."),
    )
    subscriptions_journalists = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
        limit_choices_to={"role": Roles.JOURNALIST},
        help_text=_("Journalists this user follows (Reader role)."),
    )

    # Editor-only fields
    affiliated_publisher = models.ForeignKey(
        "Publisher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliated_users",
        help_text=_("Publisher this user is affiliated with (Editor role only)."),
    )

    # Journalist-only fields (these are reverse relationships from Article/Newsletter models)
    # No direct fields needed - accessed via related_name on Article/Newsletter models

    def clean(self):
        """Ensure users don't set invalid role-specific fields."""
        # Validate publisher affiliation for all roles (even new users)
        if self.role == self.Roles.READER and self.affiliated_publisher:
            raise ValidationError(
                _("Readers cannot be affiliated with a publisher.")
            )
        elif self.role == self.Roles.JOURNALIST and self.affiliated_publisher:
            raise ValidationError(
                _("Journalists cannot be affiliated with a publisher.")
            )
        
        # Skip M2M checks until the user has a primary key
        if not self.pk or getattr(self._state, "adding", False):
            return

        if self.role == self.Roles.EDITOR:
            # Note: affiliated_publisher validation is now handled by the form
            # to allow for manual publisher creation during profile updates
            if (self.subscriptions_publishers.exists()
                    or self.subscriptions_journalists.exists()):
                raise ValidationError(
                    _("Editors cannot have reader subscription fields set.")
                )
        elif self.role == self.Roles.JOURNALIST:
            if (self.subscriptions_publishers.exists()
                    or self.subscriptions_journalists.exists()):
                raise ValidationError(
                    _("Journalists cannot have reader subscription "
                      "fields set.")
                )
        elif self.role == self.Roles.READER:
            # Readers cannot have journalist publication fields
            # This is enforced by the Article/Newsletter models' limit_choices_to
            pass


    def save(self, *args, **kwargs):
        """Normalize fields based on role when saving."""
        # Call full_clean to enforce validation rules BEFORE modifying fields
        self.full_clean()
        
        # Set affiliated_publisher to None for non-editors
        if self.role != self.Roles.EDITOR:
            self.affiliated_publisher = None
        
        # Save the user first
        super().save(*args, **kwargs)
        
        # Clear M2M fields after the user has an ID
        if self.role == self.Roles.EDITOR:
            self.subscriptions_publishers.clear()
            self.subscriptions_journalists.clear()
        elif self.role == self.Roles.JOURNALIST:
            self.subscriptions_publishers.clear()
            self.subscriptions_journalists.clear()
        elif self.role == self.Roles.READER:
            # Readers don't have journalist publication fields to clear
            pass

    def get_independent_articles(self):
        """Get articles published independently by this journalist (no publisher)."""
        if self.role != self.Roles.JOURNALIST:
            return Article.objects.none()
        return self.articles.filter(publisher__isnull=True)
    
    def get_independent_newsletters(self):
        """Get newsletters published independently by this journalist (no publisher)."""
        if self.role != self.Roles.JOURNALIST:
            return Newsletter.objects.none()
        return self.newsletters.filter(publisher__isnull=True)
    
    def get_subscribed_publishers(self):
        """Get publishers this reader is subscribed to."""
        if self.role != self.Roles.READER:
            return Publisher.objects.none()
        return self.subscriptions_publishers.all()
    
    def get_subscribed_journalists(self):
        """Get journalists this reader is subscribed to."""
        if self.role != self.Roles.READER:
            return User.objects.none()
        return self.subscriptions_journalists.all()


class Publisher(models.Model):
    """A publisher with editors and journalists."""

    name = models.CharField(max_length=255, unique=True)
    editors = models.ManyToManyField(
        User,
        related_name="editing_publishers",
        blank=True,
        limit_choices_to={"role": User.Roles.EDITOR},
    )
    journalists = models.ManyToManyField(
        User,
        related_name="journalist_publishers",
        blank=True,
        limit_choices_to={"role": User.Roles.JOURNALIST},
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    An article written by a journalist, with optional publisher.
    """

    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="articles",
        limit_choices_to={"role": User.Roles.JOURNALIST},
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        help_text=_("Optional. If empty, counts as independent."),
    )
    is_approved = models.BooleanField(
        default=False,
        help_text=_("True if approved by an editor."),
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_articles",
        limit_choices_to={"role": User.Roles.EDITOR},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
    def get_is_approved_display(self):
        """Return human-readable approval status"""
        return "Approved" if self.is_approved else "Pending Approval"


class Newsletter(models.Model):
    """
    A newsletter written by a journalist, with optional publisher.
    """

    subject = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="newsletters",
        limit_choices_to={"role": User.Roles.JOURNALIST},
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletters",
        help_text=_("Optional. If empty, counts as independent."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject
    


class ResetToken(models.Model):
    """
    One-time password reset token for a user.

    Stores a hashed token string with an expiry and usage timestamp.
    """

    # The user this token belongs to
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reset_tokens",
    )

    # Hashed token string (e.g. SHA-256 hex), unique and indexed
    token_hash = models.CharField(
        max_length=64,
        db_index=True,
        unique=True,
    )

    # Time when the token was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Expiry timestamp; after this the token is invalid
    expires_at = models.DateTimeField()

    # Timestamp of when the token was consumed (nullable)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Composite index for efficient lookups
        indexes = [
            models.Index(fields=["user", "expires_at"]),
        ]

    def is_expired(self) -> bool:
        """Return True if the token has passed its expiry time."""
        return timezone.now() >= self.expires_at

    def is_used(self) -> bool:
        """Return True if the token has already been consumed."""
        return self.used_at is not None