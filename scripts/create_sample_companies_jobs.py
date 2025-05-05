#!/usr/bin/env python
"""
Script to create sample companies and job listings.

This script creates:
1. Ghana Job Search company with 10 job listings
2. Celemin Employment Agency with 15 job listings

Usage:
    python scripts/create_sample_companies_jobs.py
"""

import os
import sys
import random
import datetime
from pathlib import Path
from django.utils.text import slugify
from django.utils import timezone

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from jobs.models import Company, JobListing, JobCategory

User = get_user_model()

# Sample job titles by category
JOB_TITLES = {
    'Information Technology': [
        'Software Engineer', 'Web Developer', 'Data Scientist', 'DevOps Engineer',
        'IT Support Specialist', 'Network Administrator', 'Database Administrator',
        'Systems Analyst', 'Cloud Architect', 'Mobile App Developer',
        'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
        'UI/UX Designer', 'QA Engineer', 'Product Manager', 'Scrum Master'
    ],
    'Finance': [
        'Accountant', 'Financial Analyst', 'Investment Banker', 'Financial Advisor',
        'Auditor', 'Tax Consultant', 'Risk Analyst', 'Credit Analyst',
        'Finance Manager', 'Treasurer', 'Payroll Specialist', 'Bookkeeper'
    ],
    'Healthcare': [
        'Nurse', 'Doctor', 'Medical Assistant', 'Pharmacist', 'Physical Therapist',
        'Dental Hygienist', 'Radiologic Technologist', 'Healthcare Administrator',
        'Medical Receptionist', 'Laboratory Technician', 'Nutritionist'
    ],
    'Education': [
        'Teacher', 'Professor', 'School Counselor', 'Principal', 'Librarian',
        'Education Coordinator', 'Curriculum Developer', 'Special Education Teacher',
        'Teaching Assistant', 'School Administrator', 'Education Consultant'
    ],
    'Marketing': [
        'Marketing Manager', 'Digital Marketing Specialist', 'SEO Specialist',
        'Content Writer', 'Social Media Manager', 'Brand Manager', 'Market Researcher',
        'Public Relations Specialist', 'Email Marketing Specialist', 'Growth Hacker'
    ],
    'Sales': [
        'Sales Representative', 'Account Executive', 'Sales Manager', 'Business Development Manager',
        'Inside Sales Representative', 'Outside Sales Representative', 'Sales Consultant',
        'Retail Sales Associate', 'Sales Director', 'Territory Sales Manager'
    ],
    'Customer Service': [
        'Customer Service Representative', 'Call Center Agent', 'Customer Success Manager',
        'Technical Support Specialist', 'Client Relations Manager', 'Customer Experience Manager',
        'Help Desk Analyst', 'Customer Service Manager', 'Client Services Coordinator'
    ],
    'Human Resources': [
        'HR Manager', 'Recruiter', 'HR Coordinator', 'Talent Acquisition Specialist',
        'Training and Development Specialist', 'Compensation and Benefits Specialist',
        'Employee Relations Manager', 'HR Business Partner', 'HR Director'
    ],
    'Engineering': [
        'Civil Engineer', 'Mechanical Engineer', 'Electrical Engineer', 'Chemical Engineer',
        'Structural Engineer', 'Environmental Engineer', 'Aerospace Engineer',
        'Biomedical Engineer', 'Industrial Engineer', 'Petroleum Engineer'
    ],
    'Administrative': [
        'Administrative Assistant', 'Office Manager', 'Executive Assistant',
        'Receptionist', 'Data Entry Clerk', 'Office Coordinator', 'Secretary',
        'Administrative Coordinator', 'Front Desk Receptionist', 'File Clerk'
    ]
}

# Sample locations in Ghana
GHANA_LOCATIONS = [
    'Accra', 'Kumasi', 'Tamale', 'Cape Coast', 'Sekondi-Takoradi',
    'Sunyani', 'Koforidua', 'Ho', 'Wa', 'Bolgatanga',
    'Tema', 'Obuasi', 'Techiman', 'Teshie', 'Madina',
    'East Legon, Accra', 'Airport Residential Area, Accra', 'Cantonments, Accra',
    'Labone, Accra', 'Adenta, Accra', 'Remote - Ghana', 'Hybrid - Accra'
]

# Sample job descriptions
JOB_DESCRIPTIONS = [
    """
    <h3>About the Role</h3>
    <p>We are looking for a talented professional to join our team. In this role, you will be responsible for developing and implementing strategies to achieve our business goals.</p>
    
    <h3>What You'll Do</h3>
    <ul>
        <li>Develop and implement effective strategies</li>
        <li>Collaborate with cross-functional teams</li>
        <li>Analyze data and generate insights</li>
        <li>Create and present reports to stakeholders</li>
        <li>Stay up-to-date with industry trends</li>
    </ul>
    """,
    
    """
    <h3>Job Overview</h3>
    <p>Join our dynamic team and make a significant impact on our growing company. This position offers a unique opportunity to contribute to our mission while developing your professional skills.</p>
    
    <h3>Key Responsibilities</h3>
    <ul>
        <li>Lead projects from conception to completion</li>
        <li>Manage client relationships and expectations</li>
        <li>Develop innovative solutions to complex problems</li>
        <li>Mentor junior team members</li>
        <li>Contribute to strategic planning initiatives</li>
    </ul>
    """,
    
    """
    <h3>About This Opportunity</h3>
    <p>We're seeking an experienced professional to help drive our company forward. This role combines strategic thinking with hands-on execution in a fast-paced environment.</p>
    
    <h3>Day-to-Day Responsibilities</h3>
    <ul>
        <li>Execute key initiatives aligned with company goals</li>
        <li>Collaborate with internal and external stakeholders</li>
        <li>Analyze performance metrics and recommend improvements</li>
        <li>Develop and maintain documentation</li>
        <li>Participate in regular team meetings and planning sessions</li>
    </ul>
    """
]

# Sample requirements
JOB_REQUIREMENTS = [
    """
    <h3>Qualifications</h3>
    <ul>
        <li>Bachelor's degree in a relevant field</li>
        <li>3+ years of experience in a similar role</li>
        <li>Strong analytical and problem-solving skills</li>
        <li>Excellent communication and interpersonal abilities</li>
        <li>Proficiency in relevant software and tools</li>
        <li>Ability to work independently and as part of a team</li>
    </ul>
    """,
    
    """
    <h3>Requirements</h3>
    <ul>
        <li>Bachelor's or Master's degree in a related discipline</li>
        <li>5+ years of progressive experience</li>
        <li>Demonstrated leadership and project management skills</li>
        <li>Strong verbal and written communication abilities</li>
        <li>Proficiency with industry-standard tools and technologies</li>
        <li>Ability to thrive in a fast-paced, dynamic environment</li>
    </ul>
    """,
    
    """
    <h3>Required Skills & Experience</h3>
    <ul>
        <li>Degree in relevant field or equivalent practical experience</li>
        <li>2+ years of experience in similar roles</li>
        <li>Strong organizational and time management skills</li>
        <li>Excellent attention to detail</li>
        <li>Ability to multitask and prioritize effectively</li>
        <li>Collaborative mindset with strong teamwork orientation</li>
    </ul>
    """
]

# Sample responsibilities
JOB_RESPONSIBILITIES = [
    """
    <h3>Core Responsibilities</h3>
    <ul>
        <li>Develop and implement strategies to achieve business objectives</li>
        <li>Manage projects from planning to execution</li>
        <li>Analyze data and generate actionable insights</li>
        <li>Collaborate with cross-functional teams</li>
        <li>Prepare and present reports to stakeholders</li>
        <li>Stay current with industry trends and best practices</li>
    </ul>
    """,
    
    """
    <h3>Your Responsibilities</h3>
    <ul>
        <li>Lead the development and execution of key initiatives</li>
        <li>Build and maintain relationships with clients and partners</li>
        <li>Identify opportunities for process improvement</li>
        <li>Mentor and develop junior team members</li>
        <li>Contribute to strategic planning and goal setting</li>
        <li>Ensure compliance with company policies and procedures</li>
    </ul>
    """,
    
    """
    <h3>What You'll Be Doing</h3>
    <ul>
        <li>Execute daily operations aligned with department goals</li>
        <li>Collaborate with team members on projects and initiatives</li>
        <li>Monitor and report on key performance indicators</li>
        <li>Identify and resolve issues in a timely manner</li>
        <li>Maintain accurate records and documentation</li>
        <li>Participate in training and professional development activities</li>
    </ul>
    """
]

# Sample skills by category
SKILLS_BY_CATEGORY = {
    'Information Technology': 'Python, JavaScript, SQL, AWS, Docker, Git, React, Node.js, DevOps, Agile, Scrum, REST APIs, Cloud Computing',
    'Finance': 'Financial Analysis, Accounting, Budgeting, Forecasting, Excel, QuickBooks, SAP, Financial Reporting, Taxation, Risk Management',
    'Healthcare': 'Patient Care, Medical Records, Healthcare Compliance, Clinical Procedures, Medical Terminology, HIPAA, Electronic Health Records',
    'Education': 'Curriculum Development, Lesson Planning, Student Assessment, Classroom Management, Educational Technology, Special Education',
    'Marketing': 'Digital Marketing, SEO, SEM, Content Marketing, Social Media, Google Analytics, Email Marketing, Brand Management, Market Research',
    'Sales': 'Sales Strategy, CRM, Negotiation, Account Management, Lead Generation, Sales Forecasting, Customer Relationship Management',
    'Customer Service': 'Customer Support, Problem Resolution, Communication, CRM Software, Conflict Resolution, Call Center Operations',
    'Human Resources': 'Recruitment, Employee Relations, Performance Management, HRIS, Benefits Administration, Talent Development, Labor Laws',
    'Engineering': 'AutoCAD, Project Management, Technical Drawing, Structural Analysis, Quality Control, Engineering Design, Problem Solving',
    'Administrative': 'Office Management, Microsoft Office, Scheduling, Data Entry, Filing, Document Management, Administrative Support'
}

def create_admin_user():
    """Create an admin user if one doesn't exist."""
    try:
        admin = User.objects.get(email='admin@searchfind.com')
        print(f"Admin user already exists: {admin.email}")
        return admin
    except User.DoesNotExist:
        admin = User.objects.create_superuser(
            email='admin@searchfind.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        print(f"Created admin user: {admin.email}")
        return admin

def create_company(name, admin_user):
    """Create a company with the given name."""
    try:
        company = Company.objects.get(name=name)
        print(f"Company already exists: {company.name}")
        return company
    except Company.DoesNotExist:
        company = Company.objects.create(
            name=name,
            slug=slugify(name),
            owner=admin_user,
            description=f"{name} is a leading company in Ghana providing excellent services to clients across various industries.",
            short_description=f"{name} - Leading employment services in Ghana",
            industry="human_resources",
            company_size="11-50",
            headquarters="Accra, Ghana",
            website=f"https://www.{slugify(name)}.com",
            specialties="Recruitment, Job Placement, Career Development, HR Consulting",
            status="approved",
            is_featured=True,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        print(f"Created company: {company.name}")
        return company

def create_job_listing(company, category, index):
    """Create a job listing for the given company and category."""
    # Get job titles for this category
    titles = JOB_TITLES.get(category.name, JOB_TITLES['Information Technology'])
    
    # Select a random title
    title = random.choice(titles)
    
    # Create a unique title with company name
    unique_title = f"{title} at {company.name} ({index})"
    
    # Generate a unique slug
    slug = slugify(unique_title)
    
    # Check if job listing with this slug already exists
    if JobListing.objects.filter(slug=slug).exists():
        print(f"Job listing already exists: {unique_title}")
        return None
    
    # Select random description, requirements, and responsibilities
    description = random.choice(JOB_DESCRIPTIONS)
    requirements = random.choice(JOB_REQUIREMENTS)
    responsibilities = random.choice(JOB_RESPONSIBILITIES)
    
    # Select random location in Ghana
    location = random.choice(GHANA_LOCATIONS)
    
    # Generate random salary range
    salary_min = random.randint(1500, 5000)
    salary_max = salary_min + random.randint(500, 3000)
    
    # Select random job type and experience level
    job_type = random.choice(['full_time', 'part_time', 'contract', 'remote'])
    experience_level = random.choice(['entry', 'mid', 'senior', 'executive'])
    
    # Get skills for this category
    skills = SKILLS_BY_CATEGORY.get(category.name, SKILLS_BY_CATEGORY['Information Technology'])
    
    # Generate random application deadline (1-30 days from now)
    days_ahead = random.randint(1, 30)
    application_deadline = timezone.now() + datetime.timedelta(days=days_ahead)
    
    # Create the job listing
    job = JobListing.objects.create(
        title=unique_title,
        slug=slug,
        company=company,
        posted_by=company.owner,
        category=category,
        description=description,
        requirements=requirements,
        responsibilities=responsibilities,
        location=location,
        salary_min=salary_min,
        salary_max=salary_max,
        job_type=job_type,
        experience_level=experience_level,
        skills_required=skills,
        application_deadline=application_deadline,
        is_remote=(job_type == 'remote' or 'Remote' in location),
        cover_letter_required=random.choice([True, False]),
        status='published',
        is_featured=random.choice([True, False]),
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    print(f"Created job listing: {job.title}")
    return job

def main():
    """Main function to create sample companies and job listings."""
    print("=" * 80)
    print("Creating sample companies and job listings")
    print("=" * 80)
    
    # Create admin user
    admin_user = create_admin_user()
    
    # Create companies
    ghana_job_search = create_company("Ghana Job Search", admin_user)
    celemin_agency = create_company("Celemin Employment Agency", admin_user)
    
    # Get all job categories
    categories = list(JobCategory.objects.all())
    
    # If no categories exist, create some
    if not categories:
        print("No job categories found. Creating default categories...")
        default_categories = [
            'Information Technology', 'Finance', 'Healthcare', 'Education',
            'Marketing', 'Sales', 'Customer Service', 'Human Resources',
            'Engineering', 'Administrative'
        ]
        
        for category_name in default_categories:
            category = JobCategory.objects.create(
                name=category_name,
                slug=slugify(category_name)
            )
            categories.append(category)
            print(f"Created category: {category.name}")
    
    # Create 10 job listings for Ghana Job Search
    print("\nCreating job listings for Ghana Job Search...")
    for i in range(1, 11):
        category = random.choice(categories)
        create_job_listing(ghana_job_search, category, i)
    
    # Create 15 job listings for Celemin Employment Agency
    print("\nCreating job listings for Celemin Employment Agency...")
    for i in range(1, 16):
        category = random.choice(categories)
        create_job_listing(celemin_agency, category, i)
    
    print("\nSample data creation completed!")
    print("=" * 80)
    print(f"Created 2 companies:")
    print(f"1. {ghana_job_search.name}")
    print(f"2. {celemin_agency.name}")
    print(f"Created 10 job listings for {ghana_job_search.name}")
    print(f"Created 15 job listings for {celemin_agency.name}")
    print("=" * 80)

if __name__ == "__main__":
    main()
