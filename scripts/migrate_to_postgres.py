#!/usr/bin/env python
"""
Script to migrate data from SQLite to PostgreSQL.

This script:
1. Dumps data from SQLite database
2. Creates a temporary JSON fixture
3. Loads the fixture into PostgreSQL

Usage:
    python scripts/migrate_to_postgres.py

Requirements:
    - Django settings configured for both SQLite and PostgreSQL
    - PostgreSQL database already created and configured
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
import django
django.setup()

from django.conf import settings
from django.core.management import call_command

def main():
    """Main function to migrate data from SQLite to PostgreSQL."""
    print("Starting migration from SQLite to PostgreSQL...")

    # Step 1: Create a temporary directory for fixtures
    fixtures_dir = BASE_DIR / 'fixtures_temp'
    fixtures_dir.mkdir(exist_ok=True)
    fixture_path = fixtures_dir / 'data.json'

    # Step 2: Dump data from SQLite using subprocess to handle encoding issues
    print("Dumping data from SQLite...")
    try:
        subprocess.run([
            sys.executable,
            str(BASE_DIR / 'manage.py'),
            'dumpdata',
            '--exclude', 'contenttypes',
            '--exclude', 'auth.permission',
            '--exclude', 'sessions',
            '--indent', '2',
            '--output', str(fixture_path)
        ], check=True, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    except subprocess.CalledProcessError as e:
        print(f"Error dumping data: {e}")
        print("Trying alternative approach...")

        # Alternative approach: dump each app separately
        apps = [
            'accounts',
            'jobs',
            'custom_admin',
            'messaging',
            'subscriptions'
        ]

        # Create an empty list to store all data
        all_data = []

        for app in apps:
            print(f"Dumping data for {app}...")
            temp_file = fixtures_dir / f"{app}_data.json"

            try:
                subprocess.run([
                    sys.executable,
                    str(BASE_DIR / 'manage.py'),
                    'dumpdata',
                    app,
                    '--indent', '2',
                    '--output', str(temp_file)
                ], check=True, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})

                # Read the data from the temp file
                if temp_file.exists() and temp_file.stat().st_size > 0:
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        app_data = json.load(f)
                        all_data.extend(app_data)

                    # Remove the temp file
                    temp_file.unlink()
            except Exception as e:
                print(f"Error dumping data for {app}: {e}")

        # Write all data to the fixture file
        with open(fixture_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

    # Step 3: Modify the settings to use PostgreSQL
    print("Switching to PostgreSQL database...")

    # PostgreSQL connection parameters from DATABASE_URL
    import environ
    env = environ.Env()
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

    pg_params = env.db('DATABASE_URL')

    # Temporarily modify settings to use PostgreSQL
    settings.DATABASES['default'] = pg_params

    # Step 4: Run migrations on PostgreSQL
    print("Running migrations on PostgreSQL...")
    call_command('migrate')

    # Step 5: Load data into PostgreSQL
    print("Loading data into PostgreSQL...")
    call_command('loaddata', str(fixture_path))

    # Step 6: Clean up
    print("Cleaning up...")
    if fixture_path.exists():
        fixture_path.unlink()
    fixtures_dir.rmdir()

    print("Migration completed successfully!")
    print("\nNotes:")
    print("1. Verify that all data has been migrated correctly")
    print("2. Update your settings to use PostgreSQL permanently")
    print("3. Consider creating a superuser if needed: python manage.py createsuperuser")

if __name__ == "__main__":
    main()
