#!/usr/bin/env python
"""
Simplified script to create sample companies and job listings on PythonAnywhere.

This script creates:
1. Ghana Job Search company with 10 job listings
2. Celemin Employment Agency with 15 job listings

Usage:
    python scripts/create_sample_data.py
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
from django.utils.text import slugify
from django.utils import timezone
from jobs.models import Company, JobListing, JobCategory
import random
import datetime

User = get_user_model()

def create_sample_data():
    """Create sample companies and job listings."""
    print("Creating sample data...")

    # Get or create admin user
    try:
        admin = User.objects.get(email='admin@searchfind.com')
        print(f"Using existing admin user: {admin.email}")
    except User.DoesNotExist:
        admin = User.objects.create_superuser(
            email='admin@searchfind.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print(f"Created admin user: {admin.email}")

    # Create Ghana Job Search company
    ghana_job_search, created = Company.objects.get_or_create(
        name="Ghana Job Search",
        defaults={
            'slug': 'ghana-job-search',
            'owner': admin,
            'description': "Ghana Job Search is a leading job board in Ghana connecting employers with qualified candidates.",
            'short_description': "Leading job board in Ghana",
            'industry': "human_resources",
            'company_size': "11-50",
            'headquarters': "Accra, Ghana",
            'status': "approved"
        }
    )
    if created:
        print(f"Created company: {ghana_job_search.name}")
    else:
        print(f"Using existing company: {ghana_job_search.name}")

    # Create Celemin Employment Agency company
    celemin_agency, created = Company.objects.get_or_create(
        name="Celemin Employment Agency",
        defaults={
            'slug': 'celemin-employment-agency',
            'owner': admin,
            'description': "Celemin Employment Agency specializes in connecting top talent with leading employers across Ghana.",
            'short_description': "Premier employment agency in Ghana",
            'industry': "human_resources",
            'company_size': "11-50",
            'headquarters': "Kumasi, Ghana",
            'status': "approved"
        }
    )
    if created:
        print(f"Created company: {celemin_agency.name}")
    else:
        print(f"Using existing company: {celemin_agency.name}")

    # Get all categories or create default ones
    categories = list(JobCategory.objects.all())
    if not categories:
        default_categories = [
            'Information Technology', 'Finance', 'Healthcare', 'Education',
            'Marketing', 'Sales', 'Customer Service', 'Human Resources',
            'Engineering', 'Administrative'
        ]
        for name in default_categories:
            category = JobCategory.objects.create(name=name, slug=slugify(name))
            categories.append(category)
            print(f"Created category: {category.name}")

    # Sample job titles
    job_titles = [
        "Software Developer", "Marketing Manager", "Accountant", "HR Specialist",
        "Sales Representative", "Customer Service Agent", "Project Manager",
        "Administrative Assistant", "Financial Analyst", "Data Scientist",
        "Graphic Designer", "Content Writer", "Operations Manager", "Teacher",
        "Nurse", "Engineer", "Product Manager", "Social Media Specialist",
        "Business Analyst", "Executive Assistant", "Web Developer", "UX Designer"
    ]

    # Sample locations in Ghana
    locations = [
        "Accra", "Kumasi", "Tamale", "Cape Coast", "Takoradi",
        "Sunyani", "Koforidua", "Ho", "Wa", "Bolgatanga",
        "Remote - Ghana", "Hybrid - Accra"
    ]

    # Create 10 job listings for Ghana Job Search
    print("\nCreating job listings for Ghana Job Search...")
    for i in range(1, 11):
        title = f"{random.choice(job_titles)} at Ghana Job Search ({i})"
        slug = slugify(title)

        # Skip if job already exists
        if JobListing.objects.filter(slug=slug).exists():
            print(f"Job already exists: {title}")
            continue

        # Create job listing
        job = JobListing.objects.create(
            title=title,
            slug=slug,
            company=ghana_job_search,
            posted_by=admin,
            category=random.choice(categories),
            description=f"<p>We are looking for a talented {title.split(' at ')[0]} to join our team.</p>",
            requirements="<ul><li>Bachelor's degree</li><li>3+ years of experience</li><li>Strong communication skills</li></ul>",
            responsibilities="<ul><li>Work with team members</li><li>Complete assigned tasks</li><li>Report to manager</li></ul>",
            location=random.choice(locations),
            salary_min=random.randint(1500, 3000),
            salary_max=random.randint(3500, 6000),
            job_type=random.choice(['full_time', 'part_time', 'contract', 'remote']),
            experience_level=random.choice(['entry', 'mid', 'senior']),
            skills_required="Communication, Teamwork, Problem Solving",
            application_deadline=timezone.now() + datetime.timedelta(days=random.randint(7, 30)),
            status="published",
            created_at=timezone.now()
        )
        print(f"Created job: {job.title}")

    # Create 15 job listings for Celemin Employment Agency
    print("\nCreating job listings for Celemin Employment Agency...")
    for i in range(1, 16):
        title = f"{random.choice(job_titles)} at Celemin Employment Agency ({i})"
        slug = slugify(title)

        # Skip if job already exists
        if JobListing.objects.filter(slug=slug).exists():
            print(f"Job already exists: {title}")
            continue

        # Create job listing
        job = JobListing.objects.create(
            title=title,
            slug=slug,
            company=celemin_agency,
            posted_by=admin,
            category=random.choice(categories),
            description=f"<p>Celemin Employment Agency is recruiting for a {title.split(' at ')[0]} position.</p>",
            requirements="<ul><li>Relevant qualification</li><li>Experience in similar role</li><li>Good interpersonal skills</li></ul>",
            responsibilities="<ul><li>Perform assigned duties</li><li>Collaborate with team</li><li>Meet targets</li></ul>",
            location=random.choice(locations),
            salary_min=random.randint(1500, 3000),
            salary_max=random.randint(3500, 6000),
            job_type=random.choice(['full_time', 'part_time', 'contract', 'remote']),
            experience_level=random.choice(['entry', 'mid', 'senior']),
            skills_required="Teamwork, Time Management, Attention to Detail",
            application_deadline=timezone.now() + datetime.timedelta(days=random.randint(7, 30)),
            status="published",
            created_at=timezone.now()
        )
        print(f"Created job: {job.title}")

    print("\nSample data creation completed!")

if __name__ == "__main__":
    create_sample_data()
