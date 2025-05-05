#!/usr/bin/env python
"""
Script to help with the deployment process.
This script will:
1. Backup the database
2. Run migrations
3. Collect static files
4. Update the site domain

Usage:
    python scripts/deploy.py [domain]

Example:
    python scripts/deploy.py searchfind.pythonanywhere.com
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

def backup_database():
    """Backup the database."""
    print("\n=== Backing Up Database ===")
    return run_command("python scripts/backup_database.py")

def run_migrations():
    """Run database migrations."""
    print("\n=== Running Migrations ===")
    return run_command("python manage.py migrate")

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
    """Main function to deploy the application."""
    print("=== Deploying Application ===")
    
    # Get domain from command line argument if provided
    domain = sys.argv[1] if len(sys.argv) > 1 else "searchfind.pythonanywhere.com"
    
    # Backup the database
    backup_database()
    
    # Run migrations
    run_migrations()
    
    # Collect static files
    collect_static_files()
    
    # Update site domain
    update_site_domain(domain)
    
    # Check settings
    check_settings()
    
    print("\n=== Deployment Complete ===")
    print(f"Your site should now be accessible at: https://{domain}")
    print("Don't forget to reload your web app in the PythonAnywhere dashboard!")

if __name__ == "__main__":
    main()
