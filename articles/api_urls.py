"""
API URL configuration for the articles app.

Defines REST API endpoints for articles, newsletters, publishers,
journalists, subscriptions, and authentication.
"""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

# API URL patterns
urlpatterns = [
    # Authentication
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Articles
    path('articles/', api_views.ArticleListView.as_view(), name='api_article_list'),
    path('articles/<int:pk>/', api_views.ArticleDetailView.as_view(), name='api_article_detail'),
    
    # Newsletters
    path('newsletters/', api_views.NewsletterListView.as_view(), name='api_newsletter_list'),
    path('newsletters/<int:pk>/', api_views.NewsletterDetailView.as_view(), name='api_newsletter_detail'),
    
    # Publishers
    path('publishers/', api_views.PublisherListView.as_view(), name='api_publisher_list'),
    path('publishers/<int:pk>/', api_views.PublisherDetailView.as_view(), name='api_publisher_detail'),
    
    # Journalists
    path('journalists/', api_views.JournalistListView.as_view(), name='api_journalist_list'),
    
    # Subscriptions
    path('subscriptions/', api_views.UserSubscriptionsView.as_view(), name='api_subscriptions'),
    
    # Combined feed
    path('feed/', api_views.user_feed, name='api_feed'),
    
    # API information
    path('info/', api_views.api_info, name='api_info'),
]
