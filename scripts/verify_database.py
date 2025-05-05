#!/usr/bin/env python
"""
Script to verify which database is being used.

This script:
1. Connects to the database
2. Prints the database engine being used

Usage:
    python scripts/verify_database.py
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

from django.conf import settings
from django.db import connection

def verify_database():
    """Verify which database is being used."""
    print("=" * 80)
    print("Verifying Database Configuration")
    print("=" * 80)
    
    # Print database engine
    db_engine = settings.DATABASES['default']['ENGINE']
    print(f"Database Engine: {db_engine}")
    
    # Check if it's PostgreSQL
    if 'postgresql' in db_engine:
        print("Using PostgreSQL database!")
        
        # Print PostgreSQL connection details
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']
        
        print(f"Database Name: {db_name}")
        print(f"Database User: {db_user}")
        print(f"Database Host: {db_host}")
        print(f"Database Port: {db_port}")
        
        # Check connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"Connected to: {version}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
    else:
        print(f"Not using PostgreSQL. Current engine: {db_engine}")
    
    print("=" * 80)

if __name__ == "__main__":
    verify_database()
