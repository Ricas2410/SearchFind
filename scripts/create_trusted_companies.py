#!/usr/bin/env python
"""
Script to create trusted companies for the homepage.

This script creates sample trusted companies with logos.

Usage:
    python scripts/create_trusted_companies.py
"""

import os
import sys
import requests
from pathlib import Path
from django.core.files.base import ContentFile

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
import django
django.setup()

from jobs.models import TrustedCompany

def create_trusted_companies():
    """Create sample trusted companies with logos."""
    print("Creating trusted companies...")

    # Sample company data with logo URLs
    trusted_companies_data = [
        {
            'name': "Microsoft",
            'website': "https://microsoft.com",
            'order': 1,
            'logo_url': "https://logo.clearbit.com/microsoft.com"
        },
        {
            'name': "Google",
            'website': "https://google.com",
            'order': 2,
            'logo_url': "https://logo.clearbit.com/google.com"
        },
        {
            'name': "Amazon",
            'website': "https://amazon.com",
            'order': 3,
            'logo_url': "https://logo.clearbit.com/amazon.com"
        },
        {
            'name': "Apple",
            'website': "https://apple.com",
            'order': 4,
            'logo_url': "https://logo.clearbit.com/apple.com"
        },
        {
            'name': "Netflix",
            'website': "https://netflix.com",
            'order': 5,
            'logo_url': "https://logo.clearbit.com/netflix.com"
        },
        {
            'name': "Adobe",
            'website': "https://adobe.com",
            'order': 6,
            'logo_url': "https://logo.clearbit.com/adobe.com"
        },
        {
            'name': "Salesforce",
            'website': "https://salesforce.com",
            'order': 7,
            'logo_url': "https://logo.clearbit.com/salesforce.com"
        },
        {
            'name': "IBM",
            'website': "https://ibm.com",
            'order': 8,
            'logo_url': "https://logo.clearbit.com/ibm.com"
        },
        # Add Ghanaian companies
        {
            'name': "MTN Ghana",
            'website': "https://mtn.com.gh",
            'order': 9,
            'logo_url': "https://logo.clearbit.com/mtn.com.gh"
        },
        {
            'name': "Vodafone Ghana",
            'website': "https://vodafone.com.gh",
            'order': 10,
            'logo_url': "https://logo.clearbit.com/vodafone.com.gh"
        },
        {
            'name': "Ghana Commercial Bank",
            'website': "https://gcbbank.com.gh",
            'order': 11,
            'logo_url': "https://logo.clearbit.com/gcbbank.com.gh"
        },
        {
            'name': "Ecobank Ghana",
            'website': "https://ecobank.com/gh",
            'order': 12,
            'logo_url': "https://logo.clearbit.com/ecobank.com"
        }
    ]

    companies_created = 0
    companies_updated = 0

    for data in trusted_companies_data:
        # Check if company already exists
        company, created = TrustedCompany.objects.get_or_create(
            name=data['name'],
            defaults={
                'website': data['website'],
                'order': data['order'],
                'is_active': True
            }
        )

        if created:
            companies_created += 1
        else:
            companies_updated += 1

        # Download and save company logo
        if data['logo_url']:
            try:
                response = requests.get(data['logo_url'])
                if response.status_code == 200:
                    logo_name = f"{data['name'].lower().replace(' ', '_')}.png"
                    company.logo.save(
                        logo_name,
                        ContentFile(response.content),
                        save=True
                    )
                    print(f"Downloaded logo for {data['name']}")
                else:
                    print(f"Failed to download logo for {data['name']}: HTTP {response.status_code}")
                    
                    # Try alternative logo URL for Ghanaian companies
                    if "ghana" in data['name'].lower() or ".gh" in data['website']:
                        alt_logo_url = f"https://logo.clearbit.com/{data['name'].lower().replace(' ', '')}.com"
                        try:
                            alt_response = requests.get(alt_logo_url)
                            if alt_response.status_code == 200:
                                logo_name = f"{data['name'].lower().replace(' ', '_')}.png"
                                company.logo.save(
                                    logo_name,
                                    ContentFile(alt_response.content),
                                    save=True
                                )
                                print(f"Downloaded alternative logo for {data['name']}")
                        except Exception as e:
                            print(f"Error downloading alternative logo for {data['name']}: {str(e)}")
            except Exception as e:
                print(f"Error downloading logo for {data['name']}: {str(e)}")

    print(f"Created {companies_created} new trusted companies")
    print(f"Updated {companies_updated} existing trusted companies")
    print(f"Total: {len(trusted_companies_data)} trusted companies")

if __name__ == "__main__":
    create_trusted_companies()
