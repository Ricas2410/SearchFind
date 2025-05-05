#!/usr/bin/env python
"""
Script to create all sample data for the SearchFind application.

This script creates:
1. Sample companies and job listings
2. Trusted companies with logos
3. Testimonials with profile images
4. Team members with photos

Usage:
    python scripts/create_all_sample_data.py
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

# Import the individual data creation functions
from scripts.create_sample_data import create_sample_data
from scripts.create_trusted_companies import create_trusted_companies
from scripts.create_testimonials import create_testimonials
from scripts.create_team_members import create_team_members

def create_all_sample_data():
    """Create all sample data for the SearchFind application."""
    print("=" * 80)
    print("Creating all sample data for SearchFind")
    print("=" * 80)
    
    # Create sample companies and job listings
    print("\n1. Creating sample companies and job listings...")
    create_sample_data()
    
    # Create trusted companies
    print("\n2. Creating trusted companies...")
    create_trusted_companies()
    
    # Create testimonials
    print("\n3. Creating testimonials...")
    create_testimonials()
    
    # Create team members
    print("\n4. Creating team members...")
    create_team_members()
    
    print("\n" + "=" * 80)
    print("All sample data created successfully!")
    print("=" * 80)

if __name__ == "__main__":
    create_all_sample_data()
