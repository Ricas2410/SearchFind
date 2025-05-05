#!/usr/bin/env python
"""
Script to migrate specific models from SQLite to PostgreSQL.

This script:
1. Dumps data from SQLite database model by model
2. Creates a temporary JSON fixture for each model
3. Loads the fixtures into PostgreSQL

Usage:
    python scripts/migrate_models_individually.py
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
    print("Starting targeted migration from SQLite to PostgreSQL...")
    print("=" * 80)
    
    # Create a temporary directory for fixtures
    fixtures_dir = BASE_DIR / 'fixtures_temp'
    fixtures_dir.mkdir(exist_ok=True)
    
    # Define models to migrate in order (considering dependencies)
    models_to_migrate = [
        # Auth models
        'auth.group',
        'auth.user',
        
        # Jobs models
        'jobs.jobcategory',
        'jobs.company',
        'jobs.joblisting',
        'jobs.jobapplication',
        'jobs.savedjob',
        'jobs.notification',
        'jobs.applicationmessage',
        'jobs.blockeduser',
        'jobs.newsletter',
        'jobs.testimonial',
        'jobs.teammember',
        'jobs.trustedcompany',
        'jobs.jobpackage',
        'jobs.jobrenewal',
        'jobs.jobanalytics',
        'jobs.legalpage',
        'jobs.companyconnection',
        'jobs.companyfollower',
        
        # Accounts models
        'accounts.customuser',
        
        # Messaging models
        'messaging.conversation',
        'messaging.message',
        
        # Subscription models
        'subscriptions.subscriptionplan',
        'subscriptions.usersubscription',
        'subscriptions.paystackconfig',
        'subscriptions.resumeanalysis',
        'subscriptions.jobmatchscore',
        'subscriptions.companymatchscore',
        'subscriptions.resumebuilder',
    ]
    
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
        # Dump data from SQLite model by model
        for model in models_to_migrate:
            print(f"\nDumping data from {model}...")
            fixture_path = fixtures_dir / f"{model.replace('.', '_')}.json"
            
            try:
                # Use subprocess to run the command with UTF-8 encoding
                cmd = [
                    sys.executable, 
                    'manage.py', 
                    'dumpdata', 
                    model,
                    '--indent=2'
                ]
                
                with open(fixture_path, 'w', encoding='utf-8') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
                
                if result.returncode == 0:
                    print(f"Successfully dumped {model} data")
                else:
                    print(f"Error dumping {model}: {result.stderr}")
                    continue
            except Exception as e:
                print(f"Exception dumping {model}: {e}")
                continue
        
        # Switch to PostgreSQL
        print("\nSwitching to PostgreSQL database...")
        settings.DATABASES['default'] = pg_params
        
        # Run migrations on PostgreSQL
        print("\nRunning migrations on PostgreSQL...")
        call_command('migrate')
        
        # Load data into PostgreSQL model by model
        for model in models_to_migrate:
            model_file = model.replace('.', '_')
            fixture_path = fixtures_dir / f"{model_file}.json"
            
            if fixture_path.exists() and fixture_path.stat().st_size > 0:
                print(f"\nLoading {model} data into PostgreSQL...")
                try:
                    # Use subprocess for better error handling
                    cmd = [
                        sys.executable, 
                        'manage.py', 
                        'loaddata', 
                        str(fixture_path)
                    ]
                    
                    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
                    
                    if result.returncode == 0:
                        print(f"Successfully loaded {model} data")
                    else:
                        print(f"Error loading {model}: {result.stderr}")
                except Exception as e:
                    print(f"Exception loading {model}: {e}")
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
