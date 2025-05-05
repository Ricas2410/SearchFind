#!/usr/bin/env python
"""
Script to populate PostgreSQL database with initial data.

This script:
1. Creates job categories
2. Creates a default company
3. Creates subscription plans
4. Creates legal pages

Usage:
    python scripts/populate_initial_data.py
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

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()

def create_job_categories():
    """Create job categories."""
    from jobs.models import JobCategory

    categories = [
        "Technology",
        "Healthcare",
        "Finance",
        "Education",
        "Marketing",
        "Sales",
        "Customer Service",
        "Human Resources",
        "Engineering",
        "Design",
        "Legal",
        "Administrative",
    ]

    print("Creating job categories...")
    created_count = 0

    for category in categories:
        _, created = JobCategory.objects.get_or_create(
            name=category,
            defaults={
                'slug': slugify(category),
                'description': f"{category} jobs and career opportunities."
            }
        )
        if created:
            created_count += 1

    print(f"Created {created_count} job categories.")

def create_default_company():
    """Create a default company."""
    from jobs.models import Company

    print("Creating default company...")

    # Get admin user
    try:
        admin = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("Admin user not found. Creating a default company requires an admin user.")
        return

    # Create default company
    try:
        company, created = Company.objects.get_or_create(
            name="Default Company",
            defaults={
                'slug': 'default-company',
                'owner': admin,
                'description': 'Default company for the system.',
                'industry': 'technology',
                'company_size': '1-10',
                'company_location': 'Default Location',
                'status': 'approved',
                'created_at': timezone.now(),
                'updated_at': timezone.now(),
            }
        )
    except Exception as e:
        print(f"Error creating default company: {e}")
        print("Trying with minimal fields...")
        try:
            company, created = Company.objects.get_or_create(
                name="Default Company",
                defaults={
                    'slug': 'default-company',
                    'owner': admin,
                    'description': 'Default company for the system.',
                    'status': 'approved',
                }
            )
        except Exception as e:
            print(f"Error creating default company with minimal fields: {e}")
            return

    if created:
        print("Default company created successfully.")
    else:
        print("Default company already exists.")

def create_subscription_plans():
    """Create subscription plans."""
    from subscriptions.models import SubscriptionPlan

    try:
        # Check the actual fields in the model
        print("Checking SubscriptionPlan model fields...")
        fields = [f.name for f in SubscriptionPlan._meta.get_fields()]
        print(f"Available fields: {fields}")

        # Create basic plans with minimal fields
        print("Creating basic subscription plans...")

        # Create Basic plan
        basic_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Basic',
            defaults={
                'price': 0,
                'plan_type': 'jobseeker',
            }
        )
        if created:
            print("Created Basic plan")

        # Create Pro plan
        pro_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Pro',
            defaults={
                'price': 1999,
                'plan_type': 'jobseeker',
            }
        )
        if created:
            print("Created Pro plan")

        # Create Employer Basic plan
        employer_basic, created = SubscriptionPlan.objects.get_or_create(
            name='Employer Basic',
            defaults={
                'price': 4999,
                'plan_type': 'employer',
            }
        )
        if created:
            print("Created Employer Basic plan")

        # Create Employer Pro plan
        employer_pro, created = SubscriptionPlan.objects.get_or_create(
            name='Employer Pro',
            defaults={
                'price': 9999,
                'plan_type': 'employer',
            }
        )
        if created:
            print("Created Employer Pro plan")

    except Exception as e:
        print(f"Error creating subscription plans: {e}")
        print("Skipping subscription plan creation.")

def create_legal_pages():
    """Create legal pages."""
    from jobs.models import LegalPage

    try:
        # Check the actual fields in the model
        print("Checking LegalPage model fields...")
        fields = [f.name for f in LegalPage._meta.get_fields()]
        print(f"Available fields: {fields}")

        # Create terms page
        terms_content = """
# Terms and Conditions

## 1. Introduction

Welcome to SearchFind. These Terms and Conditions govern your use of our website and services.

## 2. Acceptance of Terms

By accessing or using our services, you agree to be bound by these Terms and Conditions.

## 3. User Accounts

You are responsible for maintaining the confidentiality of your account information.

## 4. Job Listings and Applications

Employers are responsible for the accuracy of their job listings. Job seekers are responsible for the accuracy of their applications.

## 5. Privacy

Your privacy is important to us. Please review our Privacy Policy to understand how we collect and use your information.

## 6. Intellectual Property

All content on this website is the property of SearchFind and is protected by copyright laws.

## 7. Limitation of Liability

SearchFind is not liable for any damages arising from your use of our services.

## 8. Governing Law

These Terms and Conditions are governed by the laws of the jurisdiction in which SearchFind operates.

## 9. Changes to Terms

We reserve the right to modify these Terms and Conditions at any time.

## 10. Contact Us

If you have any questions about these Terms and Conditions, please contact us.
        """

        privacy_content = """
# Privacy Policy

## 1. Introduction

This Privacy Policy describes how SearchFind collects, uses, and shares your personal information.

## 2. Information We Collect

We collect information you provide directly to us, such as your name, email address, and resume.

## 3. How We Use Your Information

We use your information to provide and improve our services, communicate with you, and for other purposes described in this Privacy Policy.

## 4. How We Share Your Information

We may share your information with employers when you apply for jobs, and with service providers who help us operate our business.

## 5. Your Choices

You can access, update, or delete your account information at any time.

## 6. Security

We take reasonable measures to protect your personal information.

## 7. International Transfers

Your information may be transferred to and processed in countries other than your own.

## 8. Children's Privacy

Our services are not directed to children under the age of 13.

## 9. Changes to This Privacy Policy

We may update this Privacy Policy from time to time.

## 10. Contact Us

If you have any questions about this Privacy Policy, please contact us.
        """

        faq_content = """
# Frequently Asked Questions

## General Questions

### What is SearchFind?

SearchFind is a job board platform that connects job seekers with employers.

### How do I create an account?

Click on the "Sign Up" button in the top right corner of the page and follow the instructions.

## For Job Seekers

### How do I apply for a job?

Browse job listings and click on the "Apply" button for the job you're interested in.

### How do I create a profile?

After signing up, go to your dashboard and click on "Edit Profile" to complete your profile.

### Is my information secure?

Yes, we take security seriously and use industry-standard measures to protect your information.

## For Employers

### How do I post a job?

After signing up as an employer, go to your dashboard and click on "Post a Job" to create a new job listing.

### How do I manage applications?

Go to your dashboard and click on "Manage Applications" to view and manage job applications.

### How do I edit my company profile?

Go to your dashboard and click on "Edit Company Profile" to update your company information.

## Subscription and Payments

### What subscription plans do you offer?

We offer both free and premium plans for job seekers and employers. Visit our Plans page for more information.

### How do I upgrade my subscription?

Go to your dashboard and click on "Subscription" to view and upgrade your plan.

### How do I cancel my subscription?

Go to your dashboard, click on "Subscription", and then click on "Cancel Subscription".
        """

        # Create terms page
        try:
            terms_page, created = LegalPage.objects.get_or_create(
                slug='terms',
                defaults={
                    'title': 'Terms and Conditions',
                    'content': terms_content,
                    'page_type': 'terms',
                }
            )
            if created:
                print("Created Terms and Conditions page")
        except Exception as e:
            print(f"Error creating Terms page: {e}")

        # Create privacy page
        try:
            privacy_page, created = LegalPage.objects.get_or_create(
                slug='privacy',
                defaults={
                    'title': 'Privacy Policy',
                    'content': privacy_content,
                    'page_type': 'privacy',
                }
            )
            if created:
                print("Created Privacy Policy page")
        except Exception as e:
            print(f"Error creating Privacy page: {e}")

        # Create FAQ page
        try:
            faq_page, created = LegalPage.objects.get_or_create(
                slug='faq',
                defaults={
                    'title': 'Frequently Asked Questions',
                    'content': faq_content,
                    'page_type': 'faq',
                }
            )
            if created:
                print("Created FAQ page")
        except Exception as e:
            print(f"Error creating FAQ page: {e}")

    except Exception as e:
        print(f"Error creating legal pages: {e}")
        print("Skipping legal page creation.")

def populate_database():
    """Populate the database with initial data."""
    print("=" * 80)
    print("Populating PostgreSQL database with initial data")
    print("=" * 80)

    create_job_categories()
    create_default_company()
    create_subscription_plans()
    create_legal_pages()

    print("\nDatabase population completed!")
    print("=" * 80)

if __name__ == "__main__":
    populate_database()
