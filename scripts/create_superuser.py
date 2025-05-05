#!/usr/bin/env python
"""
Script to create a superuser non-interactively.

Usage:
    python scripts/create_superuser.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def create_superuser():
    """Create a superuser non-interactively."""
    email = 'admin@searchfind.com'
    password = 'admin123'

    try:
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            print(f"Superuser created successfully!")
            print(f"Email: {email}")
            print(f"Password: {password}")
            print("\nPlease change the password after first login.")
        else:
            print(f"Superuser with email '{email}' already exists.")
            print("Updating password...")

            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            print(f"Password updated for user with email '{email}'")
    except Exception as e:
        print(f"Error creating superuser: {e}")

if __name__ == "__main__":
    create_superuser()
