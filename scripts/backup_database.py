#!/usr/bin/env python
"""
Script to backup the database.
This script will create a JSON dump of the database.

Usage:
    python scripts/backup_database.py [output_dir]

Example:
    python scripts/backup_database.py backups
"""

import os
import sys
import json
import datetime
import subprocess
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
import django
django.setup()

def backup_database(output_dir=None):
    """Backup the database to a JSON file."""
    # Set default output directory if not provided
    if not output_dir:
        output_dir = BASE_DIR / 'backups'
    else:
        output_dir = Path(output_dir)
    
    # Create the output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Generate a timestamp for the backup file
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = output_dir / f"db_backup_{timestamp}.json"
    
    print(f"Backing up database to: {backup_file}")
    
    try:
        # Use subprocess to run dumpdata command
        subprocess.run([
            sys.executable,
            str(BASE_DIR / 'manage.py'),
            'dumpdata',
            '--exclude', 'contenttypes',
            '--exclude', 'auth.permission',
            '--exclude', 'sessions',
            '--indent', '2',
            '--output', str(backup_file)
        ], check=True, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        
        print(f"Backup completed successfully!")
        print(f"Backup file: {backup_file}")
        
        # Get the size of the backup file
        size_bytes = backup_file.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        if size_mb >= 1:
            print(f"Backup size: {size_mb:.2f} MB")
        else:
            print(f"Backup size: {size_kb:.2f} KB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error backing up database: {e}")
        
        # Try an alternative approach for specific apps
        print("Trying alternative approach...")
        
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
            print(f"Backing up {app}...")
            temp_file = output_dir / f"{app}_backup_{timestamp}.json"
            
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
                print(f"Error backing up {app}: {e}")
        
        # Write all data to the backup file
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"Backup completed with alternative approach!")
        print(f"Backup file: {backup_file}")
        
        # Get the size of the backup file
        size_bytes = backup_file.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        if size_mb >= 1:
            print(f"Backup size: {size_mb:.2f} MB")
        else:
            print(f"Backup size: {size_kb:.2f} KB")
        
        return True
    except Exception as e:
        print(f"Error backing up database: {e}")
        return False

if __name__ == "__main__":
    # Get output directory from command line argument if provided
    output_dir = sys.argv[1] if len(sys.argv) > 1 else None
    backup_database(output_dir)
