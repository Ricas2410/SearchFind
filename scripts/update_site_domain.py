#!/usr/bin/env python
"""
Script to update the site domain in the database.
This is useful when deploying to production.

Usage:
    python scripts/update_site_domain.py [domain]

Example:
    python scripts/update_site_domain.py searchfind.pythonanywhere.com
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

from django.contrib.sites.models import Site
from django.conf import settings

def update_site_domain(domain=None):
    """Update the site domain in the database."""
    if not domain:
        # If no domain is provided, use the one from settings or default to localhost
        domain = getattr(settings, 'SITE_DOMAIN', 'searchfind.pythonanywhere.com')
    
    print(f"Updating site domain to: {domain}")
    
    try:
        # Get the current site
        site = Site.objects.get(id=settings.SITE_ID)
        
        # Update the domain and name
        old_domain = site.domain
        site.domain = domain
        site.name = 'SearchFind'
        site.save()
        
        print(f"Site domain updated from '{old_domain}' to '{domain}'")
    except Site.DoesNotExist:
        # Create a new site if it doesn't exist
        site = Site.objects.create(
            id=settings.SITE_ID,
            domain=domain,
            name='SearchFind'
        )
        print(f"Created new site with domain '{domain}'")
    except Exception as e:
        print(f"Error updating site domain: {e}")

if __name__ == "__main__":
    # Get domain from command line argument if provided
    domain = sys.argv[1] if len(sys.argv) > 1 else None
    update_site_domain(domain)
