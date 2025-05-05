#!/usr/bin/env python
"""
Script to check if the PostgreSQL connection is working.
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
django.setup()

def check_postgres_connection():
    """Check if the PostgreSQL connection is working."""
    from django.db import connections
    from django.db.utils import OperationalError
    
    print("Checking PostgreSQL connection...")
    
    try:
        # Try to get a cursor from the default database
        connection = connections['default']
        connection.cursor()
        
        # Get database info
        db_name = connection.settings_dict['NAME']
        db_user = connection.settings_dict['USER']
        db_host = connection.settings_dict['HOST']
        db_port = connection.settings_dict['PORT']
        
        print("✅ Connection successful!")
        print(f"Database: {db_name}")
        print(f"User: {db_user}")
        print(f"Host: {db_host}")
        print(f"Port: {db_port}")
        
        # Check if we can execute a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"PostgreSQL version: {version}")
        
        return True
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

if __name__ == "__main__":
    check_postgres_connection()
