#!/usr/bin/env python
"""
Script to check PostgreSQL configuration.

This script:
1. Connects to PostgreSQL
2. Checks if tables exist
3. Prints database statistics

Usage:
    python scripts/check_postgres_config.py
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

from django.db import connection
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()

def check_database():
    """Check PostgreSQL database configuration."""
    print("=" * 80)
    print("Checking PostgreSQL Database Configuration")
    print("=" * 80)
    
    # Check connection
    print("\nChecking database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"Connected to: {version}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Check tables
    print("\nChecking database tables...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"Found {len(tables)} tables:")
            for i, (table,) in enumerate(tables, 1):
                print(f"  {i}. {table}")
        else:
            print("No tables found in the database.")
    
    # Check user count
    print("\nChecking user data...")
    try:
        user_count = User.objects.count()
        print(f"Total users: {user_count}")
        
        if user_count > 0:
            print("Sample users:")
            for user in User.objects.all()[:5]:
                print(f"  - {user.username} ({user.email})")
    except Exception as e:
        print(f"Error checking users: {e}")
    
    # Check model counts
    print("\nChecking model data...")
    try:
        for app_config in apps.get_app_configs():
            if app_config.name in ['jobs', 'accounts', 'messaging', 'subscriptions']:
                print(f"\n{app_config.verbose_name} app:")
                for model in app_config.get_models():
                    try:
                        count = model.objects.count()
                        print(f"  - {model.__name__}: {count} records")
                    except Exception as e:
                        print(f"  - {model.__name__}: Error - {e}")
    except Exception as e:
        print(f"Error checking models: {e}")
    
    print("\nDatabase check completed!")
    print("=" * 80)

if __name__ == "__main__":
    check_database()
