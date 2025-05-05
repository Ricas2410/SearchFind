#!/usr/bin/env python
"""
Script to help with the initial setup on PythonAnywhere.
This script will:
1. Create necessary directories
2. Run migrations
3. Create a superuser
4. Collect static files
5. Update the site domain

Usage:
    python scripts/setup_pythonanywhere.py [domain]

Example:
    python scripts/setup_pythonanywhere.py searchfind.pythonanywhere.com
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
import django
django.setup()

def run_command(command):
    """Run a shell command and print the output."""
    print(f"Running command: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(e.stdout)
        print(e.stderr)
        return False

def create_directories():
    """Create necessary directories."""
    print("\n=== Creating Directories ===")
    
    # Create media directory
    media_dir = BASE_DIR / 'media'
    media_dir.mkdir(exist_ok=True)
    print(f"Created media directory: {media_dir}")
    
    # Create staticfiles directory
    static_dir = BASE_DIR / 'staticfiles'
    static_dir.mkdir(exist_ok=True)
    print(f"Created staticfiles directory: {static_dir}")
    
    return True

def run_migrations():
    """Run database migrations."""
    print("\n=== Running Migrations ===")
    return run_command("python manage.py migrate")

def create_superuser():
    """Create a superuser."""
    print("\n=== Creating Superuser ===")
    return run_command("python scripts/create_superuser.py")

def collect_static_files():
    """Collect static files."""
    print("\n=== Collecting Static Files ===")
    return run_command("python manage.py collectstatic --noinput")

def update_site_domain(domain):
    """Update the site domain."""
    print("\n=== Updating Site Domain ===")
    return run_command(f"python scripts/update_site_domain.py {domain}")

def check_settings():
    """Check settings."""
    print("\n=== Checking Settings ===")
    return run_command("python scripts/check_settings.py")

def main():
    """Main function to set up PythonAnywhere."""
    print("=== Setting Up PythonAnywhere ===")
    
    # Get domain from command line argument if provided
    domain = sys.argv[1] if len(sys.argv) > 1 else "searchfind.pythonanywhere.com"
    
    # Create directories
    create_directories()
    
    # Run migrations
    run_migrations()
    
    # Create superuser
    create_superuser()
    
    # Collect static files
    collect_static_files()
    
    # Update site domain
    update_site_domain(domain)
    
    # Check settings
    check_settings()
    
    print("\n=== Setup Complete ===")
    print(f"Your site should now be accessible at: https://{domain}")
    print("Don't forget to configure your web app in the PythonAnywhere dashboard!")

if __name__ == "__main__":
    main()
