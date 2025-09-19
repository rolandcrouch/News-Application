from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from articles.functions.tweet import TwitterAPI
from requests_oauthlib import OAuth2Session
from django.conf import settings
import os

# Disable HTTPS requirement for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@login_required
def start_auth(request):
    """Start Twitter OAuth authentication flow."""
    try:
        print(f"DEBUG: Starting Twitter OAuth for user {request.user}")
        print(f"DEBUG: TWITTER_CLIENT_ID = {settings.TWITTER_CLIENT_ID}")
        print(f"DEBUG: TWITTER_CLIENT_SECRET = {settings.TWITTER_CLIENT_SECRET[:10]}...")
        print(f"DEBUG: TWITTER_REDIRECT_URI = {settings.TWITTER_REDIRECT_URI}")
        
        api = TwitterAPI()
        auth_url = api.begin_oauth()
        
        print(f"DEBUG: Generated auth URL: {auth_url}")
        print(f"DEBUG: Code verifier: {api.code_verifier[:20]}...")
        print(f"DEBUG: State: {getattr(api, '_state', 'None')}")

        # Persist PKCE + state for the callback request
        request.session["tw_code_verifier"] = api.code_verifier
        request.session["tw_state"] = getattr(api, "_state", None)

        return redirect(auth_url)
    except Exception as e:
        print(f"ERROR: Failed to start Twitter auth: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"Failed to start Twitter authentication: {type(e).__name__}: {e}")
        return redirect(reverse("newsfeed"))


@login_required
def callback(request):
    """Handle Twitter OAuth callback."""
    print(f"DEBUG: Twitter callback received for user {request.user}")
    print(f"DEBUG: Full callback URL: {request.build_absolute_uri()}")
    print(f"DEBUG: GET parameters: {dict(request.GET)}")
    
    # Provider error returned?
    if request.GET.get("error"):
        error_msg = request.GET.get("error_description") or request.GET.get("error")
        print(f"ERROR: Twitter returned error: {request.GET.get('error')} - {error_msg}")
        messages.error(request, f"Twitter OAuth Error: {request.GET.get('error')} - {error_msg}")
        return redirect(reverse("newsfeed"))

    try:
        api = TwitterAPI()
        
        # Restore PKCE verifier + expected state
        code_verifier = request.session.pop("tw_code_verifier", None)
        expected_state = request.session.pop("tw_state", None)
        
        print(f"DEBUG: Retrieved code_verifier: {code_verifier[:20] if code_verifier else 'None'}...")
        print(f"DEBUG: Expected state: {expected_state}")
        print(f"DEBUG: Received state: {request.GET.get('state')}")
        
        api.code_verifier = code_verifier

        # Rebuild OAuth2Session on this fresh instance
        if api.session is None:
            print("DEBUG: Rebuilding OAuth2Session")
            api.session = OAuth2Session(
                client_id=settings.TWITTER_CLIENT_ID,
                redirect_uri=settings.TWITTER_REDIRECT_URI,
                scope=settings.TWITTER_SCOPES,
            )

        print("DEBUG: Attempting to finish OAuth flow...")
        print(f"DEBUG: Full callback URL being passed to finish_oauth: {request.build_absolute_uri()}")
        
        try:
            api.finish_oauth(request.build_absolute_uri(), expected_state=expected_state)
            print("DEBUG: OAuth completed successfully!")
            messages.success(request, "Twitter connected successfully!")
            return redirect(reverse("newsfeed"))
        except Exception as oauth_error:
            print(f"ERROR: OAuth finish_oauth failed: {type(oauth_error).__name__}: {oauth_error}")
            raise oauth_error
    except Exception as e:
        print(f"ERROR: Failed to complete Twitter auth: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"Failed to complete Twitter authentication: {type(e).__name__}: {e}")
        return redirect(reverse("newsfeed"))


def is_twitter_connected():
    """Check if Twitter is connected by verifying token file exists and is valid."""
    try:
        api = TwitterAPI()
        return api.token is not None and api.session is not None
    except Exception:
        return False


def get_twitter_status():
    """Get Twitter connection status for template context."""
    return {
        'is_connected': is_twitter_connected(),
        'has_credentials': bool(
            getattr(settings, 'TWITTER_CLIENT_ID', None) and 
            getattr(settings, 'TWITTER_CLIENT_SECRET', None)
        )
    }


@login_required
def disconnect_twitter(request):
    """Disconnect Twitter by removing stored tokens."""
    try:
        if os.path.exists(settings.TWITTER_TOKEN_PATH):
            os.remove(settings.TWITTER_TOKEN_PATH)
        messages.success(request, "Twitter disconnected successfully.")
    except Exception as e:
        messages.error(request, f"Failed to disconnect Twitter: {e}")
    
    return redirect(reverse("newsfeed"))


@login_required
def twitter_debug(request):
    """Debug view to check Twitter status"""
    status = get_twitter_status()
    
    debug_info = {
        'twitter_status': status,
        'client_id': getattr(settings, 'TWITTER_CLIENT_ID', 'NOT SET'),
        'client_secret': getattr(settings, 'TWITTER_CLIENT_SECRET', 'NOT SET'),
        'redirect_uri': getattr(settings, 'TWITTER_REDIRECT_URI', 'NOT SET'),
        'token_path': getattr(settings, 'TWITTER_TOKEN_PATH', 'NOT SET'),
    }
    
    return HttpResponse(f"<pre>{debug_info}</pre>")