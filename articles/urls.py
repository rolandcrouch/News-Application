from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CustomLoginView,
    register,
    forgot_username,
    send_password_reset,
    reset_user_password,
    article_feed, 
    newsfeed,
    browse_all_news,
    subscriptions,
    ArticleCreateView, ArticleDetailView,
    ArticleUpdateView, ArticleDeleteView,
    NewsletterCreateView, NewsletterDetailView, 
    NewsletterUpdateView, NewsletterDeleteView,
    approve_and_publish, article_unapprove, user_profile,
)
from .integrations.twitter_views import start_auth, callback, disconnect_twitter, twitter_debug

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/",
         auth_views.LogoutView.as_view(next_page="login"),
         name="logout"),
    path("register/", register, name="register"),

    # account utilities
    path("forgot-username/", forgot_username, name="forgot_username"),
    path("account/reset/", send_password_reset, name="send_password_reset"),
    path("account/reset/<str:token>/",
         reset_user_password, name="reset_user_password"),

    # articles
    path("articles/", article_feed, name="articles_list"),

    # unified feed
    path("news/", newsfeed, name="newsfeed"),
    
    # browse all content (readers only)
    path("browse/", browse_all_news, name="browse_all_news"),

    # subscriptions
    path("subscriptions/", subscriptions, name="subscriptions"),
    
    # user profile
    path("profile/", user_profile, name="user_profile"),
    
    # article CRUD
    path("articles/new/", ArticleCreateView.as_view(), name="article_create"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(),
         name="article_detail"),
    path("articles/<int:pk>/edit/", ArticleUpdateView.as_view(),
         name="article_update"),
    path("articles/<int:pk>/delete/", ArticleDeleteView.as_view(),
         name="article_delete"),
    

    # newsletter CRUD
    path("newsletters/new/", NewsletterCreateView.as_view(),
         name="newsletter_create"),
    path("newsletters/<int:pk>/", NewsletterDetailView.as_view(),
         name="newsletter_detail"),
    path("newsletters/<int:pk>/edit/", NewsletterUpdateView.as_view(),
         name="newsletter_update"),
    path("newsletters/<int:pk>/delete/", NewsletterDeleteView.as_view(),
         name="newsletter_delete"),

    # approval (editors only)
    path("articles/<int:pk>/approve/", approve_and_publish, {"kind": "article"}, name="article_approve"),
    path("articles/<int:pk>/unapprove/", article_unapprove,
         name="article_unapprove"),

    path("publish/article/<int:pk>/", approve_and_publish, {"kind": "article"}, name="publish_article"),
    path("publish/newsletter/<int:pk>/", approve_and_publish, {"kind": "newsletter"}, name="publish_newsletter"),
    
    # Twitter integration
    path("twitter/connect/", start_auth, name="twitter_connect"),
    path("twitter/callback/", callback, name="twitter_callback"),
    path("twitter/disconnect/", disconnect_twitter, name="twitter_disconnect"),
    path("twitter/debug/", twitter_debug, name="twitter_debug"),

]