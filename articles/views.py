from itertools import chain
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import transaction, models
from django.db.models import Value, CharField
from django.core.exceptions import FieldDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.shortcuts import (
            render, redirect, get_object_or_404
            )
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import Truncator
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from .forms import UserRegistrationForm, ForgotUsernameForm, \
                    PasswordResetRequestForm, ArticleForm, \
                     NewsletterForm, UserProfileForm
from .utils import create_reset_token, build_reset_url, \
                        validate_and_consume_token, lookup_reset_token, \
                        consume_reset_token
from .models import Article, User, Publisher, Newsletter
from articles.functions.tweet import TwitterAPI
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string


class CustomLoginView(auth_views.LoginView):
    """
    Use Django's built-in login with our custom template.
    """
    template_name = "registration/login.html"


def register(request):
    """Register a new user and redirect to login on success."""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Account created successfully. Please log in."
            )
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})


# ---------- account utilities ----------


def forgot_username(request: HttpRequest) -> HttpResponse:
    """
    Email any usernames associated with the provided address.
    """
    message = ""
    if request.method == "POST":
        form = ForgotUsernameForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)
            if users.exists():
                username_list = ", ".join(u.username for u in users)
                send_mail(
                    "Your Username",
                    f"Your username(s): {username_list}",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                message = "Username sent to your email."
            else:
                message = "No account with that email."
    else:
        form = ForgotUsernameForm()
    return render(request, "registration/forgot_username.html", 
                  {"form": form, "message": message})


def send_password_reset(request):
    """
    Neutral response to prevent user enumeration.
    """
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = getattr(form, "user", None)  # your form should attach user if found
            if user and user.email:
                raw = create_reset_token(user)
                reset_url = build_reset_url(request, raw)

                subject = "Password Reset Request"
                text_body = f"Click the link below to reset your password:\n{reset_url}"
                from_email = settings.DEFAULT_FROM_EMAIL
                to = [user.email]

                email = EmailMultiAlternatives(subject, text_body, from_email, to)
                # (Optional) Add HTML template:
                # html_body = render_to_string("registration/reset_email.html", {"reset_url": reset_url, "user": user})
                # email.attach_alternative(html_body, "text/html")
                email.send()

            messages.success(request, "If that account exists, a reset link has been sent.")
            return redirect("login")
        messages.error(request, "Please correct the errors below.")
    return render(request, "registration/request_password_reset.html", {"form": form})



def reset_user_password(request, token: str):
    """
    GET: validate token and show form (no consumption).
    POST: on valid form, set password and consume token.
    """
    user, rt = lookup_reset_token(token)
    if not user:
        return render(
            request,
            "registration/password_reset_confirm.html",
            {"validlink": False},
        )

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                # consume only AFTER successfully setting the password
                consume_reset_token(rt)
            messages.success(request, "Your password has been reset. Please log in.")
            return redirect("login")
    else:
        form = SetPasswordForm(user)

    return render(
        request,
        "registration/reset_password_confirm_page.html",
        {"validlink": True, "form": form},
    )

# ---------- article feed ----------

def article_feed(request):
    """Redirect to newsfeed view for unified content display."""
    # Redirect to newsfeed instead of using separate article_feed.html
    return redirect(reverse("newsfeed"))

# ---------- newsfeed ----------

def newsfeed(request):
    """Unified feed for Articles + Newsletters, newest first."""
    # Figure out which field newsletters use for body text.
    try:
        Newsletter._meta.get_field("body")
        news_text_field = "body"
    except FieldDoesNotExist:
        news_text_field = "content"

    # Base querysets
    arts_base = Article.objects.select_related("author", "publisher")
    letters_base = Newsletter.objects.select_related("author", "publisher")
    
    # Apply filtering based on user role
    if request.user.is_authenticated and request.user.role == User.Roles.READER:
        # For readers: show independent articles from followed journalists AND articles from subscribed publishers
        followed_journalist_ids = request.user.subscriptions_journalists.values_list('id', flat=True)
        subscribed_publisher_ids = request.user.subscriptions_publishers.values_list('id', flat=True)
        
        arts = arts_base.filter(
            models.Q(
                publisher__isnull=True,  # Independent articles
                author_id__in=followed_journalist_ids  # From followed journalists
            ) | models.Q(
                publisher_id__in=subscribed_publisher_ids  # Articles from subscribed publishers
            )
        ).annotate(
            kind=models.Value("article", output_field=models.CharField()),
            text=models.F("body"),
        )
        
        letters = letters_base.filter(
            models.Q(
                publisher__isnull=True,  # Independent newsletters
                author_id__in=followed_journalist_ids  # From followed journalists
            ) | models.Q(
                publisher_id__in=subscribed_publisher_ids  # Newsletters from subscribed publishers
            )
        ).annotate(
            kind=models.Value("newsletter", output_field=models.CharField()),
            text=models.F(news_text_field),
        )
    else:
        # For editors and journalists: show all content (current behavior)
        arts = arts_base.annotate(
            kind=models.Value("article", output_field=models.CharField()),
            text=models.F("body"),
        )
        
        letters = letters_base.annotate(
            kind=models.Value("newsletter", output_field=models.CharField()),
            text=models.F(news_text_field),
        )

    items = sorted(
        chain(arts, letters),
        key=lambda o: o.created_at,
        reverse=True,
    )

    paginator = Paginator(items, 10)
    page = request.GET.get("page") or 1
    page_obj = paginator.get_page(page)

    can_create = (
        request.user.is_authenticated
        and (
            request.user.role == User.Roles.JOURNALIST
            or request.user.has_perm("articles.add_article")
            or request.user.has_perm("articles.add_newsletter")
        )
    )

    ctx = {"page_obj": page_obj, "can_create": can_create}
    return render(request, "articles/newsfeed.html", ctx)

# ---------- Browse All Content ----------

@login_required
def browse_all_news(request):
    """Display all approved articles and newsletters with search and filtering."""
    """Browse all approved articles and newsletters regardless of subscription."""
    if request.user.role != User.Roles.READER:
        # Non-readers should use the regular newsfeed
        return redirect(reverse("newsfeed"))
    
    # Get filter from URL parameter
    content_filter = request.GET.get('type', 'all')  # 'all', 'articles', 'newsletters'
    
    # Figure out which field newsletters use for body text
    try:
        Newsletter._meta.get_field("body")
        news_text_field = "body"
    except FieldDoesNotExist:
        news_text_field = "content"
    
    if content_filter == 'articles':
        # Show only articles
        articles = Article.objects.select_related("author", "publisher").filter(
            is_approved=True
        ).annotate(
            kind=models.Value("article", output_field=models.CharField()),
            text=models.F("body"),
        ).order_by('-created_at')
        
        items = list(articles)
        page_title = "All Articles"
        
    elif content_filter == 'newsletters':
        # Show only newsletters
        newsletters = Newsletter.objects.select_related("author", "publisher").annotate(
            kind=models.Value("newsletter", output_field=models.CharField()),
            text=models.F(news_text_field),
        ).order_by('-created_at')
        
        items = list(newsletters)
        page_title = "All Newsletters"
        
    else:
        # Show all content (default)
        articles = Article.objects.select_related("author", "publisher").filter(
            is_approved=True
        ).annotate(
            kind=models.Value("article", output_field=models.CharField()),
            text=models.F("body"),
        )
        
        newsletters = Newsletter.objects.select_related("author", "publisher").annotate(
            kind=models.Value("newsletter", output_field=models.CharField()),
            text=models.F(news_text_field),
        )
        
        # Combine and sort by creation date
        items = sorted(
            chain(articles, newsletters),
            key=lambda o: o.created_at,
            reverse=True,
        )
        page_title = "Browse All News"
    
    paginator = Paginator(items, 15)
    page = request.GET.get("page") or 1
    page_obj = paginator.get_page(page)
    
    ctx = {
        "page_obj": page_obj,
        "content_filter": content_filter,
        "page_title": page_title
    }
    return render(request, "articles/browse_all.html", ctx)


# ---------- Subscriptions ----------

@login_required
def subscriptions(request):
    """Display and manage user subscriptions to publishers and journalists."""
    """
    List publishers and journalists. Readers can subscribe/unsubscribe.
    Tab switch via ?tab=journalists|publishers.
    """
    is_reader = getattr(request.user, "role", None) == User.Roles.READER

    # Which tab is active?
    tab = (request.GET.get("tab")
           or request.POST.get("tab")
           or "journalists")
    if tab not in ("journalists", "publishers"):
        tab = "journalists"

    publishers = Publisher.objects.all().order_by("name")
    journalists = (
        User.objects.filter(role=User.Roles.JOURNALIST)
        .order_by("username")
    )

    if request.method == "POST" and is_reader:
        kind = request.POST.get("kind")
        obj_id = request.POST.get("id")
        action = request.POST.get("action")

        if kind == "publisher":
            obj = get_object_or_404(Publisher, pk=obj_id)
            m2m = request.user.subscriptions_publishers
        elif kind == "journalist":
            obj = get_object_or_404(
                User, pk=obj_id, role=User.Roles.JOURNALIST
            )
            m2m = request.user.subscriptions_journalists
        else:
            messages.error(request, "Invalid subscription type.")
            return redirect(f"{reverse('subscriptions')}?tab={tab}")

        if action == "subscribe":
            m2m.add(obj)
            messages.success(request, f"Subscribed to {obj}.")
        elif action == "unsubscribe":
            m2m.remove(obj)
            messages.info(request, f"Unsubscribed from {obj}.")
        else:
            messages.error(request, "Invalid action.")

        # Preserve current tab after POST
        return redirect(f"{reverse('subscriptions')}?tab={tab}")

    user_pub_ids = set(
        request.user.subscriptions_publishers.values_list("id", flat=True)
    ) if request.user.is_authenticated else set()

    user_jour_ids = set(
        request.user.subscriptions_journalists.values_list("id", flat=True)
    ) if request.user.is_authenticated else set()

    ctx = {
        "publishers": publishers,
        "journalists": journalists,
        "is_reader": is_reader,
        "user_pub_ids": user_pub_ids,
        "user_jour_ids": user_jour_ids,
        "tab": tab,
    }
    return render(request, "articles/subscriptions.html", ctx)

# ---------- Articles ----------

def _is_editor_or_journalist(user: User) -> bool:
    """Check if user is authenticated and has editor or journalist role."""
    return user.is_authenticated and user.role in (
        User.Roles.EDITOR, User.Roles.JOURNALIST
    )


def _is_editor(user: User) -> bool:
    """Check if user is authenticated and has editor role."""
    return user.is_authenticated and user.role == User.Roles.EDITOR


class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for creating new articles by editors and journalists."""
    
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"
    success_url = reverse_lazy("newsfeed")

    def test_func(self):
        return _is_editor_or_journalist(self.request.user)

    def form_valid(self, form):
        form.instance.author = self.request.user
        # Approval stays false by default; editors can approve via action.
        messages.success(self.request, "Article created.")
        return super().form_valid(form)


class ArticleDetailView(DetailView):
    """View for displaying article details."""
    
    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating existing articles by their authors."""
    
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"
    success_url = reverse_lazy("newsfeed")

    def test_func(self):
        obj = self.get_object()
        u = self.request.user
        return u.is_authenticated and (u == obj.author or _is_editor(u))

    def form_valid(self, form):
        messages.success(self.request, "Article updated.")
        return super().form_valid(form)


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting articles by their authors."""
    
    model = Article
    template_name = "articles/article_confirm_delete.html"
    success_url = reverse_lazy("newsfeed")

    def test_func(self):
        obj = self.get_object()
        u = self.request.user
        return u.is_authenticated and (u == obj.author or _is_editor(u))

    def delete(self, request, *args, **kwargs):
        messages.info(request, "Article deleted.")
        return super().delete(request, *args, **kwargs)
    
# ---------- Newsletters ----------

class NewsletterCreateView(
    LoginRequiredMixin, UserPassesTestMixin, CreateView
):
    """View for creating new newsletters by editors and journalists."""
    
    model = Newsletter
    form_class = NewsletterForm
    template_name = "articles/newsletter_form.html"
    success_url = reverse_lazy("newsfeed")

    def test_func(self):
        return _is_editor_or_journalist(self.request.user)

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Newsletter created.")
        return super().form_valid(form)
    

class NewsletterDetailView(DetailView):
    """View for displaying newsletter details."""
    
    model = Newsletter
    template_name = "articles/newsletter_detail.html"
    context_object_name = "newsletter"


class NewsletterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating existing newsletters by their authors."""
    
    model = Newsletter
    form_class = NewsletterForm
    template_name = "articles/newsletter_form.html"
    success_url = reverse_lazy("newsfeed")

    def test_func(self):
        obj = self.get_object()
        u = self.request.user
        return u.is_authenticated and (u == obj.author or _is_editor(u))

    def form_valid(self, form):
        messages.success(self.request, "Newsletter updated.")
        return super().form_valid(form)


class NewsletterDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting newsletters by their authors."""
    
    model = Newsletter
    template_name = "articles/newsletter_confirm_delete.html"
    success_url = reverse_lazy("newsfeed")

    def test_func(self):
        obj = self.get_object()
        u = self.request.user
        return u.is_authenticated and (u == obj.author or _is_editor(u))

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, "Newsletter deleted.")
        return super().delete(request, *args, **kwargs)


def _compose_tweet_for_article(a: Article) -> str:
    """Compose a Twitter-friendly text for an article with title and truncated body."""
    # Journalist display name
    who = a.author.get_full_name() or a.author.username
    # Build the tweet. Leave some headroom for safety (links, emojis, etc.)
    # X (Twitter) default limit is 280 chars; we’ll aim for ~270 max.
    header = f"📰 {who} — {a.title}\n\n"
    # Truncate the body smartly at word boundaries
    body = Truncator(a.body.strip()).chars(270 - len(header), truncate="…")
    return f"{header}{body}"


def _compose_tweet_for_newsletter(n: Newsletter) -> str:
    """Compose a Twitter-friendly text for a newsletter with subject and truncated content."""
    who = n.author.get_full_name() or n.author.username
    header = f"📣 {who} — {n.subject}\n\n"
    body = Truncator(n.content.strip()).chars(270 - len(header), truncate="…")
    return f"{header}{body}"


def _send_article_notification_email(article, publisher):
    """
    Send email notification to readers who subscribe to the publisher
    when an article is approved.
    """
    if not publisher:
        return  # No publisher, no subscribers to notify
    
    # Get all readers who subscribe to this publisher
    subscribers = User.objects.filter(
        role=User.Roles.READER,
        subscriptions_publishers=publisher
    ).distinct()
    
    if not subscribers.exists():
        return  # No subscribers to notify
    
    # Prepare email content
    subject = f"New Article from {publisher.name}: {article.title}"
    
    # Create HTML email content
    html_content = render_to_string('articles/email/article_notification.html', {
        'article': article,
        'publisher': publisher,
        'site_url': 'http://127.0.0.1:8000',  # You might want to make this configurable
    })
    
    # Create plain text version
    text_content = f"""
New Article from {publisher.name}

Title: {article.title}
Author: {article.author.username}
Published: {article.created_at.strftime('%B %d, %Y at %I:%M %p')}

{article.body[:200]}{'...' if len(article.body) > 200 else ''}

Read the full article: http://127.0.0.1:8000/articles/{article.pk}/

---
This email was sent because you subscribe to {publisher.name}.
You can manage your subscriptions at: http://127.0.0.1:8000/subscriptions/
"""
    
    # Send email to each subscriber
    for subscriber in subscribers:
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='newsapp@example.com',
                to=[subscriber.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            # Log the error but don't fail the approval process
            print(f"Failed to send email to {subscriber.email}: {e}")


def approve_and_publish(request, kind: str, pk: int):
    """Approve and publish an article or newsletter, with optional Twitter posting."""
    """
    Approves an Article OR publishes a Newsletter, then posts to Twitter.

    URL examples:
      path('publish/article/<int:pk>/', approve_and_publish, {'kind': 'article'}, name='publish_article')
      path('publish/newsletter/<int:pk>/', approve_and_publish, {'kind': 'newsletter'}, name='publish_newsletter')
    """
    # --- permissions ---
    if not _is_editor(request.user):
        messages.error(request, "Only editors can approve/publish.")
        return redirect(reverse("newsfeed"))  # adjust redirect as appropriate

    # --- pick model ---
    if kind == "article":
        obj = get_object_or_404(Article, pk=pk)
    elif kind == "newsletter":
        obj = get_object_or_404(Newsletter, pk=pk)
    else:
        messages.error(request, "Unknown content type.")
        return redirect(reverse("newsfeed"))

    # --- publisher affiliation check ---
    # Editors can only approve content published by their publisher
    if obj.publisher:
        if not request.user.affiliated_publisher:
            messages.error(request, "You must be affiliated with a publisher to approve content.")
            return redirect(reverse("newsfeed"))
        
        if request.user.affiliated_publisher != obj.publisher:
            messages.error(request, f"You can only approve content published by {request.user.affiliated_publisher.name}.")
            return redirect(reverse("newsfeed"))

    # --- process approval ---
    if kind == "article":
        # Avoid re-approving
        if not obj.is_approved:
            obj.is_approved = True
            obj.approved_by = request.user
            obj.save(update_fields=["is_approved", "approved_by"])
            
            # Send email notifications to subscribers
            _send_article_notification_email(obj, obj.publisher)
            
        tweet_text = _compose_tweet_for_article(obj)
        success_msg = "Article approved, emails sent to subscribers, and posted to Twitter."
    else:  # newsletter
        # No is_approved field on Newsletter; treat this as publish+tweet
        tweet_text = _compose_tweet_for_newsletter(obj)
        success_msg = "Newsletter published and posted to Twitter."

    # --- tweet ---
    from articles.integrations.twitter_views import is_twitter_connected
    
    if not is_twitter_connected():
        messages.warning(
            request,
            "Content approved/published, but Twitter is not connected. "
            "Please connect Twitter to enable automatic posting."
        )
        # Store the tweet text for manual posting later
        request.session["last_tweet_draft"] = tweet_text
    else:
        try:
            api = TwitterAPI()

            # Try to post the tweet
            if hasattr(api, "post_tweet"):
                api.post_tweet(tweet_text)
            elif hasattr(api, "create_tweet"):
                api.create_tweet(tweet_text)
            elif hasattr(api, "tweet"):
                api.tweet(tweet_text)
            else:
                raise AttributeError("TwitterAPI has no tweet-posting method")

            messages.success(request, success_msg)

        except AttributeError as e:
            # Developer wiring issue
            messages.warning(request, f"Approved, but could not post to Twitter: {e}")
        except Exception as e:
            # API error
            messages.warning(
                request,
                f"Content approved/published, but Twitter posting failed: {str(e)}. "
                "Please try again or contact support."
            )
            # Store the tweet text for manual posting later
            request.session["last_tweet_draft"] = tweet_text

    # --- redirect back somewhere useful (detail page if you have it) ---
    if kind == "article":
        try:
            return redirect(obj.get_absolute_url())
        except Exception:
            return redirect(reverse("newsfeed"))
    else:  # newsletter
        try:
            return redirect(obj.get_absolute_url())
        except Exception:
            return redirect(reverse("newsfeed"))


@login_required
@user_passes_test(_is_editor)
def article_unapprove(request, pk: int):
    """Unapprove an article, removing its approved status."""
    article = get_object_or_404(Article, pk=pk)
    
    # Publisher affiliation check
    if article.publisher:
        if not request.user.affiliated_publisher:
            messages.error(request, "You must be affiliated with a publisher to unapprove content.")
            return redirect("newsfeed")
        
        if request.user.affiliated_publisher != article.publisher:
            messages.error(request, f"You can only unapprove content published by {request.user.affiliated_publisher.name}.")
            return redirect("newsfeed")
    
    article.is_approved = False
    article.save(update_fields=["is_approved"])
    messages.info(request, "Article unapproved.")
    return redirect("newsfeed")


@login_required
def user_profile(request):
    """Display and handle user profile editing form."""
    """View for users to edit their profile details."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("user_profile")
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, "articles/user_profile.html", {
        "form": form,
        "user": request.user,
    })