#!/usr/bin/env python
"""
Robust script to migrate data from SQLite to PostgreSQL.

This script:
1. Verifies database connections
2. Dumps data from SQLite database
3. Creates a temporary JSON fixture
4. Loads the fixture into PostgreSQL
5. Handles errors gracefully

Usage:
    python scripts/migrate_to_postgres_robust.py

Requirements:
    - Django settings configured for both SQLite and PostgreSQL
    - PostgreSQL database already created and configured
    - Environment variables set for PostgreSQL connection
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')

try:
    import django
    django.setup()

    from django.conf import settings
    from django.core.management import call_command
    from django.db import connections, OperationalError

except ImportError as e:
    print(f"Error importing Django: {e}")
    sys.exit(1)

def check_connection(db_alias='default'):
    """Check if database connection is working."""
    try:
        conn = connections[db_alias]
        conn.cursor()
        return True
    except OperationalError:
        return False

def backup_sqlite_db():
    """Create a backup of the SQLite database."""
    sqlite_path = settings.DATABASES['default']['NAME']
    backup_path = f"{sqlite_path}.bak.{int(time.time())}"

    try:
        import shutil
        shutil.copy2(sqlite_path, backup_path)
        print(f"SQLite database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"Warning: Failed to backup SQLite database: {e}")
        return False

def get_postgres_config():
    """Get PostgreSQL configuration from environment variables."""
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return None

    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }

def main():
    """Main function to migrate data from SQLite to PostgreSQL."""
    print("=" * 80)
    print("Starting migration from SQLite to PostgreSQL...")
    print("=" * 80)

    # Step 1: Verify SQLite connection
    print("\nVerifying SQLite connection...")
    if not check_connection():
        print("Error: Cannot connect to SQLite database.")
        sys.exit(1)
    print("SQLite connection successful.")

    # Step 2: Backup SQLite database
    print("\nCreating backup of SQLite database...")
    backup_sqlite_db()

    # Step 3: Get PostgreSQL configuration
    print("\nGetting PostgreSQL configuration...")
    pg_config = get_postgres_config()
    if not pg_config:
        sys.exit(1)

    # Step 4: Create a temporary directory for fixtures
    fixtures_dir = BASE_DIR / 'fixtures_temp'
    fixtures_dir.mkdir(exist_ok=True)
    fixture_path = fixtures_dir / 'data.json'

    try:
        # Step 5: Dump data from SQLite
        print("\nDumping data from SQLite...")

        # Set UTF-8 encoding for the process to handle Unicode characters
        if sys.platform == 'win32':
            import subprocess

            # Use subprocess to run the command with UTF-8 encoding
            cmd = [
                sys.executable,
                'manage.py',
                'dumpdata',
                '--exclude=contenttypes',
                '--exclude=auth.permission',
                '--exclude=sessions',
                '--indent=2'
            ]

            print("Running command with UTF-8 encoding...")
            with open(fixture_path, 'w', encoding='utf-8') as f:
                subprocess.run(cmd, stdout=f, check=True)
        else:
            # For non-Windows platforms, use call_command
            call_command('dumpdata',
                        exclude=['contenttypes', 'auth.permission', 'sessions'],
                        output=str(fixture_path),
                        indent=2)

        if not fixture_path.exists() or fixture_path.stat().st_size == 0:
            print("Error: Failed to dump data or fixture is empty.")
            sys.exit(1)

        print(f"Data dumped successfully to {fixture_path} ({fixture_path.stat().st_size} bytes)")

        # Step 6: Store original database config
        original_db_config = settings.DATABASES['default'].copy()

        # Step 7: Modify the settings to use PostgreSQL
        print("\nSwitching to PostgreSQL database...")
        settings.DATABASES['default'] = pg_config

        # Step 8: Verify PostgreSQL connection
        print("Verifying PostgreSQL connection...")
        if not check_connection():
            print("Error: Cannot connect to PostgreSQL database.")
            print("Please check your PostgreSQL connection settings.")
            settings.DATABASES['default'] = original_db_config
            sys.exit(1)
        print("PostgreSQL connection successful.")

        # Step 9: Run migrations on PostgreSQL
        print("\nRunning migrations on PostgreSQL...")
        call_command('migrate')

        # Step 10: Load data into PostgreSQL
        print("\nLoading data into PostgreSQL...")
        call_command('loaddata', str(fixture_path))

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"\nError during migration: {e}")
        print(traceback.format_exc())
        print("\nMigration failed. Please check the error message above.")
        sys.exit(1)

    finally:
        # Step 11: Clean up
        print("\nCleaning up...")
        if fixture_path.exists():
            fixture_path.unlink()
        if fixtures_dir.exists():
            try:
                fixtures_dir.rmdir()
            except OSError:
                print(f"Warning: Could not remove directory {fixtures_dir}. It may not be empty.")

    print("\nNext steps:")
    print("1. Verify that all data has been migrated correctly")
    print("2. Update your settings to use PostgreSQL permanently")
    print("3. Consider creating a superuser if needed: python manage.py createsuperuser")
    print("4. Update your DJANGO_SETTINGS_MODULE to use searchfind.settings_prod")
    print("=" * 80)

if __name__ == "__main__":
    main()
