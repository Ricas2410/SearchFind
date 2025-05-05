#!/usr/bin/env python
"""
Simple script to migrate data from SQLite to PostgreSQL.

This script:
1. Dumps data from SQLite database app by app
2. Creates a temporary JSON fixture for each app
3. Loads the fixtures into PostgreSQL

Usage:
    python scripts/migrate_to_postgres_simple.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')

import django
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.apps import apps

def main():
    """Main function to migrate data from SQLite to PostgreSQL."""
    print("=" * 80)
    print("Starting migration from SQLite to PostgreSQL...")
    print("=" * 80)
    
    # Create a temporary directory for fixtures
    fixtures_dir = BASE_DIR / 'fixtures_temp'
    fixtures_dir.mkdir(exist_ok=True)
    
    # Get all app labels
    app_labels = [app.label for app in apps.get_app_configs()]
    print(f"Found apps: {', '.join(app_labels)}")
    
    # Store original database config
    original_db_config = settings.DATABASES['default'].copy()
    
    # PostgreSQL connection parameters
    pg_params = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'defaultdb'),
        'USER': os.environ.get('DB_USER', 'avnadmin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'AVNS_XVJ0lm9nrWBSK1OYwSs'),
        'HOST': os.environ.get('DB_HOST', 'pg-b0522a0-search-searchfind.j.aivencloud.com'),
        'PORT': os.environ.get('DB_PORT', '19271'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
    
    try:
        # Dump data from SQLite app by app
        for app_label in app_labels:
            if app_label in ['contenttypes', 'admin', 'sessions']:
                print(f"Skipping {app_label}...")
                continue
                
            print(f"\nDumping data from {app_label}...")
            fixture_path = fixtures_dir / f"{app_label}.json"
            
            try:
                # Use subprocess to run the command with UTF-8 encoding
                cmd = [
                    sys.executable, 
                    'manage.py', 
                    'dumpdata', 
                    app_label,
                    '--indent=2'
                ]
                
                with open(fixture_path, 'w', encoding='utf-8') as f:
                    subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
                
                print(f"Successfully dumped {app_label} data")
            except subprocess.CalledProcessError as e:
                print(f"Error dumping {app_label}: {e}")
                print(f"Error output: {e.stderr.decode('utf-8', errors='replace')}")
                continue
        
        # Switch to PostgreSQL
        print("\nSwitching to PostgreSQL database...")
        settings.DATABASES['default'] = pg_params
        
        # Run migrations on PostgreSQL
        print("\nRunning migrations on PostgreSQL...")
        call_command('migrate')
        
        # Load data into PostgreSQL app by app
        for app_label in app_labels:
            if app_label in ['contenttypes', 'admin', 'sessions']:
                continue
                
            fixture_path = fixtures_dir / f"{app_label}.json"
            if fixture_path.exists() and fixture_path.stat().st_size > 0:
                print(f"\nLoading {app_label} data into PostgreSQL...")
                try:
                    call_command('loaddata', str(fixture_path))
                    print(f"Successfully loaded {app_label} data")
                except Exception as e:
                    print(f"Error loading {app_label}: {e}")
                    continue
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\nError during migration: {e}")
        print("\nMigration failed. Please check the error message above.")
        sys.exit(1)
        
    finally:
        # Clean up
        print("\nCleaning up...")
        for fixture_path in fixtures_dir.glob("*.json"):
            try:
                fixture_path.unlink()
            except:
                pass
        
        try:
            fixtures_dir.rmdir()
        except:
            pass
    
    print("\nNext steps:")
    print("1. Verify that all data has been migrated correctly")
    print("2. Update your settings to use PostgreSQL permanently")
    print("3. Consider creating a superuser if needed: python manage.py createsuperuser")
    print("4. Update your DJANGO_SETTINGS_MODULE to use searchfind.settings_prod")
    print("=" * 80)

if __name__ == "__main__":
    main()
