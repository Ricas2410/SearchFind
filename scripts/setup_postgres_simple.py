#!/usr/bin/env python
"""
Simple script to set up PostgreSQL database for SearchFind.

This script:
1. Connects to PostgreSQL
2. Runs all migrations
3. Creates a superuser

Usage:
    python scripts/setup_postgres_simple.py
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
from django.db import IntegrityError

User = get_user_model()

def setup_database():
    """Set up the PostgreSQL database."""
    print("=" * 80)
    print("Setting up PostgreSQL database for SearchFind")
    print("=" * 80)

    # Create superuser
    print("\nCreating superuser...")
    try:
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            user_type='admin'  # Explicitly set user_type to admin
        )
        print("Superuser 'admin' created successfully!")
    except IntegrityError:
        print("Superuser already exists. Updating password and user type...")
        try:
            user = User.objects.get(username='admin')
            user.set_password('adminpassword')
            user.user_type = 'admin'  # Ensure user_type is set to admin
            user.save()
            print("Password and user type updated for user 'admin'")
        except User.DoesNotExist:
            print("Could not find user 'admin'")

    # Run migrations
    print("\nRunning migrations...")
    try:
        call_command('migrate')
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error during migrations: {e}")
        print("Some migrations may have failed, but the database should be usable.")

    print("\nDatabase setup completed!")
    print("\nYou can now run the server with:")
    print("set DJANGO_SETTINGS_MODULE=searchfind.settings_prod")
    print("python manage.py runserver")
    print("=" * 80)

if __name__ == "__main__":
    setup_database()
