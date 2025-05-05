from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def get_social_auth_status():
    """
    Check if social authentication is properly configured.

    Returns:
        dict: Status of each social auth provider
    """
    status = {
        'google': {
            'configured': False,
            'message': _('Google authentication is not available. Please use your email and password to sign up.'),
            'admin_url': '/my-admin/social-applications/'
        },
        'linkedin': {
            'configured': False,
            'message': _('LinkedIn authentication is not available. Please use your email and password to sign up.'),
            'admin_url': '/my-admin/social-applications/'
        }
    }

    # Check if Google is configured
    try:
        google_app = SocialApp.objects.filter(provider='google').first()
        if google_app and google_app.client_id and google_app.secret:
            # Check if the app is associated with at least one site
            if google_app.sites.exists():
                status['google']['configured'] = True
                status['google']['message'] = _('Google authentication is properly configured.')
            else:
                status['google']['message'] = _('Google authentication is not fully configured. The app is not associated with any site.')
    except Exception as e:
        status['google']['message'] = _('Error checking Google authentication: {}').format(str(e))

    # Check if LinkedIn is configured
    try:
        linkedin_app = SocialApp.objects.filter(provider='linkedin_oauth2').first()
        if linkedin_app and linkedin_app.client_id and linkedin_app.secret:
            # Check if the app is associated with at least one site
            if linkedin_app.sites.exists():
                status['linkedin']['configured'] = True
                status['linkedin']['message'] = _('LinkedIn authentication is properly configured.')
            else:
                status['linkedin']['message'] = _('LinkedIn authentication is not fully configured. The app is not associated with any site.')
    except Exception as e:
        status['linkedin']['message'] = _('Error checking LinkedIn authentication: {}').format(str(e))

    return status

def ensure_site_exists():
    """
    Ensure that at least one site exists in the database.
    This is required for social authentication to work.
    """
    # Make sure the site with SITE_ID exists
    site, _ = Site.objects.get_or_create(
        id=settings.SITE_ID,
        defaults={
            'domain': '127.0.0.1:8000',
            'name': 'SearchFind'
        }
    )

    # If no sites exist, create the default site
    if not Site.objects.exists():
        site = Site.objects.create(
            id=settings.SITE_ID,
            domain='127.0.0.1:8000',
            name='SearchFind'
        )

    return site
