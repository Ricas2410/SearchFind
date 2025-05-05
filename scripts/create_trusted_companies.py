#!/usr/bin/env python
"""
Script to create trusted companies for the homepage.

This script creates several trusted companies with their logos.

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

# List of trusted companies with their details
TRUSTED_COMPANIES = [
    {
        'name': 'MTN Ghana',
        'website': 'https://www.mtn.com.gh',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/MTN_Logo.svg/1200px-MTN_Logo.svg.png',
        'order': 1
    },
    {
        'name': 'Vodafone Ghana',
        'website': 'https://www.vodafone.com.gh',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Vodafone_icon.svg/1200px-Vodafone_icon.svg.png',
        'order': 2
    },
    {
        'name': 'Ecobank Ghana',
        'website': 'https://www.ecobank.com/gh/personal-banking',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/79/Ecobank.svg/1200px-Ecobank.svg.png',
        'order': 3
    },
    {
        'name': 'Unilever Ghana',
        'website': 'https://www.unilever-ewa.com/ghana',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Unilever_logo.svg/1200px-Unilever_logo.svg.png',
        'order': 4
    },
    {
        'name': 'Nestle Ghana',
        'website': 'https://www.nestle.com.gh',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Nestl%C3%A9.svg/1200px-Nestl%C3%A9.svg.png',
        'order': 5
    },
    {
        'name': 'Standard Chartered Ghana',
        'website': 'https://www.sc.com/gh',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Standard_Chartered_%282021%29.svg/1200px-Standard_Chartered_%282021%29.svg.png',
        'order': 6
    },
    {
        'name': 'Ghana Commercial Bank',
        'website': 'https://www.gcbbank.com.gh',
        'logo_url': 'https://www.gcbbank.com.gh/images/logo.png',
        'order': 7
    },
    {
        'name': 'Tullow Oil Ghana',
        'website': 'https://www.tullowoil.com/where-we-operate/africa/ghana',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Tullow_Oil_logo.svg/1200px-Tullow_Oil_logo.svg.png',
        'order': 8
    }
]

def download_image(url):
    """Download image from URL and return as ContentFile."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return ContentFile(response.content)
        else:
            print(f"Failed to download image from {url}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image from {url}: {str(e)}")
        return None

def create_trusted_companies():
    """Create trusted companies."""
    print("Creating trusted companies...")
    
    for company_data in TRUSTED_COMPANIES:
        # Check if company already exists
        company, created = TrustedCompany.objects.get_or_create(
            name=company_data['name'],
            defaults={
                'website': company_data['website'],
                'order': company_data['order'],
                'is_active': True
            }
        )
        
        if created:
            print(f"Created trusted company: {company.name}")
        else:
            print(f"Trusted company already exists: {company.name}")
            # Update existing company
            company.website = company_data['website']
            company.order = company_data['order']
            company.save()
        
        # Download and save logo if URL is provided
        if company_data['logo_url']:
            logo_content = download_image(company_data['logo_url'])
            if logo_content:
                # Generate a filename based on company name
                logo_filename = f"{company_data['name'].lower().replace(' ', '_')}.png"
                
                # Save the logo
                company.logo.save(logo_filename, logo_content, save=True)
                print(f"Added logo for {company.name}")

def main():
    """Main function to create trusted companies."""
    print("=" * 80)
    print("Creating trusted companies for the homepage")
    print("=" * 80)
    
    create_trusted_companies()
    
    print("\nTrusted companies creation completed!")
    print("=" * 80)
    
    # Print summary
    companies = TrustedCompany.objects.all()
    print(f"Total trusted companies: {companies.count()}")
    for company in companies:
        logo_status = "✓" if company.logo else "✗"
        print(f"{company.order}. {company.name} (Logo: {logo_status})")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
