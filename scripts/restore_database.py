#!/usr/bin/env python
"""
Script to restore the database from a backup.
This script will load a JSON dump into the database.

Usage:
    python scripts/restore_database.py backup_file.json

Example:
    python scripts/restore_database.py backups/db_backup_20250505_010000.json
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
import django
django.setup()

def restore_database(backup_file):
    """Restore the database from a backup file."""
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"Error: Backup file not found: {backup_path}")
        return False
    
    print(f"Restoring database from: {backup_path}")
    
    try:
        # Use subprocess to run loaddata command
        subprocess.run([
            sys.executable,
            str(BASE_DIR / 'manage.py'),
            'loaddata',
            str(backup_path)
        ], check=True)
        
        print(f"Restore completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error restoring database: {e}")
        return False
    except Exception as e:
        print(f"Error restoring database: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide a backup file path")
        print("Usage: python scripts/restore_database.py backup_file.json")
        sys.exit(1)
    
    backup_file = sys.argv[1]
    restore_database(backup_file)
