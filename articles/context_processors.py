from .integrations.twitter_views import get_twitter_status


def twitter_context(request):
    """Add Twitter status to all template contexts."""
    return {
        'twitter_status': get_twitter_status()
    }

