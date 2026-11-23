import os

def google_login_status(request):
    return {
        'google_login_enabled': bool(os.getenv('GOOGLE_OAUTH_CLIENT_ID') and os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'))
    }
