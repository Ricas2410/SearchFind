import os
import sys
import django
from pathlib import Path
from django.core.files import File

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
django.setup()

from jobs.models import SiteSettings

def initialize_site_settings():
    """Initialize site settings with default values."""
    print("Initializing site settings...")
    
    # Check if settings already exist
    if SiteSettings.objects.exists():
        settings = SiteSettings.objects.first()
        print("Site settings already exist. Updating...")
    else:
        settings = SiteSettings()
        print("Creating new site settings...")
    
    # Set default values
    settings.site_name = "SearchFind"
    settings.primary_color = "#3B82F6"
    settings.secondary_color = "#1E40AF"
    settings.contact_email = "contact@searchfind.com"
    settings.support_email = "support@searchfind.com"
    
    # Save to get an ID if it's a new object
    settings.save()
    
    # Add logo if it doesn't exist
    if not settings.site_logo:
        logo_path = BASE_DIR / 'static' / 'img' / 'searchfind-logo.svg'
        if logo_path.exists():
            with open(logo_path, 'rb') as f:
                settings.site_logo.save('searchfind-logo.svg', File(f), save=True)
            print("Logo added successfully.")
        else:
            print(f"Logo file not found at {logo_path}")
    
    print("Site settings initialized successfully.")
    return settings

if __name__ == "__main__":
    initialize_site_settings()
