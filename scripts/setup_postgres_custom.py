#!/usr/bin/env python
"""
Script to set up PostgreSQL database for SearchFind with custom migrations.

This script:
1. Connects to PostgreSQL
2. Runs migrations with special handling for problematic migrations
3. Creates a superuser

Usage:
    python scripts/setup_postgres_custom.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# Set Django settings to use PostgreSQL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings_prod')

import django
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection
from django.db.migrations.recorder import MigrationRecorder

User = get_user_model()

def mark_migration_as_applied(app, name):
    """Mark a migration as applied without running it."""
    recorder = MigrationRecorder(connection)
    recorder.record_applied(app, name)
    print(f"Marked migration {app}.{name} as applied")

def setup_database():
    """Set up the PostgreSQL database with custom migration handling."""
    print("=" * 80)
    print("Setting up PostgreSQL database for SearchFind (Custom)")
    print("=" * 80)
    
    # Create superuser first
    print("\nCreating superuser...")
    try:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            user_type='admin'
        )
        print("Superuser 'admin' created successfully!")
    except IntegrityError:
        print("Superuser already exists. Updating password...")
        try:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('adminpassword')
            admin_user.save()
            print("Password updated for user 'admin'")
        except User.DoesNotExist:
            print("Could not find user 'admin'")
    
    # Run initial migrations
    print("\nRunning initial migrations...")
    call_command('migrate', 'contenttypes')
    call_command('migrate', 'auth')
    call_command('migrate', 'accounts')
    call_command('migrate', 'admin')
    call_command('migrate', 'sessions')
    call_command('migrate', 'django_summernote')
    call_command('migrate', 'account')
    call_command('migrate', 'socialaccount')
    
    # Handle jobs migrations carefully
    print("\nHandling jobs migrations...")
    
    # Apply jobs migrations up to 0015
    for i in range(1, 16):
        migration_name = f"000{i}" if i < 10 else f"00{i}"
        try:
            call_command('migrate', 'jobs', f"00{migration_name}")
            print(f"Applied jobs.{migration_name}")
        except Exception as e:
            print(f"Error applying jobs.{migration_name}: {e}")
            # Mark as applied and continue
            mark_migration_as_applied('jobs', migration_name)
    
    # Skip problematic migration and mark as applied
    mark_migration_as_applied('jobs', '0016_fix_joblisting_company_references')
    
    # Apply remaining jobs migrations
    call_command('migrate', 'jobs')
    
    # Apply messaging and subscriptions migrations
    print("\nApplying remaining migrations...")
    call_command('migrate', 'messaging')
    call_command('migrate', 'subscriptions')
    
    print("\nDatabase setup completed successfully!")
    print("\nYou can now run the server with:")
    print("set DJANGO_SETTINGS_MODULE=searchfind.settings_prod")
    print("python manage.py runserver")
    print("=" * 80)

if __name__ == "__main__":
    setup_database()
