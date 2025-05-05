#!/usr/bin/env python
"""
Script to check the database connection and settings.
This is useful for verifying the configuration before deployment.

Usage:
    python scripts/check_settings.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
import django
django.setup()

from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.contrib.sites.models import Site

def check_database_connection():
    """Check if the database connection is working."""
    print("\n=== Database Connection ===")
    
    try:
        # Try to get a cursor from the default database
        connection = connections['default']
        connection.cursor()
        
        # Get database info
        db_name = connection.settings_dict['NAME']
        db_user = connection.settings_dict['USER']
        db_host = connection.settings_dict['HOST']
        db_port = connection.settings_dict['PORT']
        db_engine = connection.settings_dict['ENGINE']
        
        print("✅ Connection successful!")
        print(f"Engine: {db_engine}")
        print(f"Database: {db_name}")
        print(f"User: {db_user}")
        print(f"Host: {db_host}")
        print(f"Port: {db_port}")
        
        # Check if we can execute a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"Database version: {version}")
        
        return True
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

def check_site_settings():
    """Check the site settings."""
    print("\n=== Site Settings ===")
    
    try:
        # Get the current site
        site = Site.objects.get(id=settings.SITE_ID)
        print(f"Site ID: {site.id}")
        print(f"Domain: {site.domain}")
        print(f"Name: {site.name}")
        
        # Check if the domain matches the ALLOWED_HOSTS
        if site.domain not in settings.ALLOWED_HOSTS and site.domain != 'example.com':
            print(f"⚠️ Warning: Site domain '{site.domain}' is not in ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        else:
            print("✅ Site domain is in ALLOWED_HOSTS")
        
        return True
    except Site.DoesNotExist:
        print("❌ Site does not exist")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

def check_email_settings():
    """Check the email settings."""
    print("\n=== Email Settings ===")
    
    try:
        print(f"Email backend: {settings.EMAIL_BACKEND}")
        print(f"Email host: {settings.EMAIL_HOST}")
        print(f"Email port: {settings.EMAIL_PORT}")
        print(f"Email user: {settings.EMAIL_HOST_USER}")
        print(f"Email TLS: {settings.EMAIL_USE_TLS}")
        print(f"Default from email: {settings.DEFAULT_FROM_EMAIL}")
        
        return True
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

def check_static_settings():
    """Check the static files settings."""
    print("\n=== Static Files Settings ===")
    
    try:
        print(f"Static URL: {settings.STATIC_URL}")
        print(f"Static root: {settings.STATIC_ROOT}")
        print(f"Media URL: {settings.MEDIA_URL}")
        print(f"Media root: {settings.MEDIA_ROOT}")
        
        # Check if the static root directory exists
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            static_root = Path(settings.STATIC_ROOT)
            if static_root.exists():
                print(f"✅ Static root directory exists: {static_root}")
            else:
                print(f"⚠️ Warning: Static root directory does not exist: {static_root}")
        
        # Check if the media root directory exists
        if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
            media_root = Path(settings.MEDIA_ROOT)
            if media_root.exists():
                print(f"✅ Media root directory exists: {media_root}")
            else:
                print(f"⚠️ Warning: Media root directory does not exist: {media_root}")
        
        return True
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

def check_debug_settings():
    """Check the debug settings."""
    print("\n=== Debug Settings ===")
    
    try:
        print(f"Debug: {settings.DEBUG}")
        print(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
        
        if settings.DEBUG:
            print("⚠️ Warning: Debug mode is enabled. This should be disabled in production.")
        else:
            print("✅ Debug mode is disabled")
        
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            print("⚠️ Warning: ALLOWED_HOSTS is not properly configured")
        else:
            print("✅ ALLOWED_HOSTS is properly configured")
        
        return True
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

def main():
    """Main function to check settings."""
    print("=== Checking Settings ===")
    
    # Check database connection
    db_ok = check_database_connection()
    
    # Check site settings
    site_ok = check_site_settings()
    
    # Check email settings
    email_ok = check_email_settings()
    
    # Check static settings
    static_ok = check_static_settings()
    
    # Check debug settings
    debug_ok = check_debug_settings()
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Database connection: {'✅' if db_ok else '❌'}")
    print(f"Site settings: {'✅' if site_ok else '❌'}")
    print(f"Email settings: {'✅' if email_ok else '❌'}")
    print(f"Static settings: {'✅' if static_ok else '❌'}")
    print(f"Debug settings: {'✅' if debug_ok else '❌'}")
    
    if all([db_ok, site_ok, email_ok, static_ok, debug_ok]):
        print("\n✅ All settings are properly configured!")
    else:
        print("\n⚠️ Some settings need attention. Please check the warnings above.")

if __name__ == "__main__":
    main()
