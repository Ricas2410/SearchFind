from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model
from jobs.models import JobCategory, JobListing
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample job listings for testing'

    def handle(self, *args, **options):
        # Create employer users if they don't exist
        employers = []
        employer_data = [
            {
                'username': 'techcorp',
                'email': 'hr@techcorp.com',
                'password': 'password123',
                'first_name': 'Tech',
                'last_name': 'Corporation',
                'user_type': 'employer',
                'company_name': 'TechCorp Solutions',
                'company_website': 'https://techcorp.example.com',
                'company_description': 'A leading technology company specializing in software development and IT services.'
            },
            {
                'username': 'globalinc',
                'email': 'careers@globalinc.com',
                'password': 'password123',
                'first_name': 'Global',
                'last_name': 'Inc',
                'user_type': 'employer',
                'company_name': 'Global Innovations Inc.',
                'company_website': 'https://globalinc.example.com',
                'company_description': 'A multinational corporation with a focus on innovation and technology.'
            },
            {
                'username': 'startupxyz',
                'email': 'jobs@startupxyz.com',
                'password': 'password123',
                'first_name': 'Startup',
                'last_name': 'XYZ',
                'user_type': 'employer',
                'company_name': 'StartupXYZ',
                'company_website': 'https://startupxyz.example.com',
                'company_description': 'A fast-growing startup disrupting the tech industry with innovative solutions.'
            },
            {
                'username': 'healthplus',
                'email': 'careers@healthplus.com',
                'password': 'password123',
                'first_name': 'Health',
                'last_name': 'Plus',
                'user_type': 'employer',
                'company_name': 'HealthPlus Medical',
                'company_website': 'https://healthplus.example.com',
                'company_description': 'A healthcare company dedicated to improving patient care through technology.'
            },
            {
                'username': 'edutech',
                'email': 'hr@edutech.com',
                'password': 'password123',
                'first_name': 'Edu',
                'last_name': 'Tech',
                'user_type': 'employer',
                'company_name': 'EduTech Learning',
                'company_website': 'https://edutech.example.com',
                'company_description': 'An educational technology company transforming how people learn.'
            }
        ]
        
        for employer in employer_data:
            user, created = User.objects.get_or_create(
                username=employer['username'],
                defaults={
                    'email': employer['email'],
                    'first_name': employer['first_name'],
                    'last_name': employer['last_name'],
                    'user_type': employer['user_type'],
                    'company_name': employer['company_name'],
                    'company_website': employer['company_website'],
                    'company_description': employer['company_description']
                }
            )
            
            if created:
                user.set_password(employer['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created employer: {user.company_name}'))
            else:
                self.stdout.write(f'Employer already exists: {user.company_name}')
                
            employers.append(user)
        
        # Get all categories
        categories = JobCategory.objects.all()
        if not categories.exists():
            self.stdout.write(self.style.ERROR('No job categories found. Please run create_initial_data command first.'))
            return
            
        # Sample job data
        job_titles = {
            'Information Technology': [
                'Senior Software Engineer', 'Frontend Developer', 'Backend Developer', 
                'Full Stack Developer', 'DevOps Engineer', 'Data Scientist', 
                'Machine Learning Engineer', 'IT Support Specialist', 'Network Administrator',
                'Cybersecurity Analyst', 'Cloud Architect', 'Mobile App Developer'
            ],
            'Engineering': [
                'Mechanical Engineer', 'Electrical Engineer', 'Civil Engineer', 
                'Chemical Engineer', 'Aerospace Engineer', 'Biomedical Engineer',
                'Environmental Engineer', 'Structural Engineer', 'Automotive Engineer'
            ],
            'Marketing': [
                'Marketing Manager', 'Digital Marketing Specialist', 'SEO Specialist',
                'Content Writer', 'Social Media Manager', 'Brand Manager',
                'Marketing Analyst', 'Email Marketing Specialist', 'Growth Hacker'
            ],
            'Finance': [
                'Financial Analyst', 'Accountant', 'Investment Banker',
                'Financial Advisor', 'Auditor', 'Tax Consultant',
                'Risk Analyst', 'Credit Analyst', 'Financial Controller'
            ],
            'Healthcare': [
                'Registered Nurse', 'Physician', 'Medical Assistant',
                'Pharmacist', 'Physical Therapist', 'Dental Hygienist',
                'Healthcare Administrator', 'Medical Technologist', 'Radiologic Technologist'
            ],
            'Education': [
                'Teacher', 'Professor', 'School Counselor',
                'Education Administrator', 'Curriculum Developer', 'Special Education Teacher',
                'Educational Consultant', 'School Psychologist', 'Instructional Designer'
            ],
            'Sales': [
                'Sales Representative', 'Account Executive', 'Sales Manager',
                'Business Development Manager', 'Inside Sales Representative', 'Sales Engineer',
                'Territory Sales Manager', 'Retail Sales Associate', 'Sales Operations Manager'
            ],
            'Human Resources': [
                'HR Manager', 'Recruiter', 'HR Specialist',
                'Talent Acquisition Manager', 'Employee Relations Specialist', 'Compensation Analyst',
                'Training and Development Manager', 'HR Business Partner', 'Benefits Administrator'
            ],
            'Design': [
                'Graphic Designer', 'UX/UI Designer', 'Product Designer',
                'Web Designer', 'Interior Designer', 'Fashion Designer',
                'Industrial Designer', 'Art Director', 'Creative Director'
            ],
            'Customer Service': [
                'Customer Service Representative', 'Customer Success Manager', 'Technical Support Specialist',
                'Client Relationship Manager', 'Call Center Representative', 'Customer Experience Manager',
                'Help Desk Analyst', 'Customer Support Specialist', 'Client Services Coordinator'
            ]
        }
        
        locations = [
            'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Chicago, IL', 'Seattle, WA',
            'Boston, MA', 'Los Angeles, CA', 'Denver, CO', 'Atlanta, GA', 'Miami, FL',
            'Dallas, TX', 'Washington, DC', 'Portland, OR', 'Nashville, TN', 'Phoenix, AZ',
            'Remote', 'Hybrid - New York, NY', 'Hybrid - San Francisco, CA', 'Remote - US Only', 'Remote - Worldwide'
        ]
        
        job_types = ['full_time', 'part_time', 'contract', 'internship', 'remote']
        experience_levels = ['entry', 'mid', 'senior', 'executive']
        
        # Create sample job listings
        jobs_created = 0
        
        for category in categories:
            # Get job titles for this category
            titles = job_titles.get(category.name, job_titles['Information Technology'])
            
            # Create 3-5 jobs per category
            num_jobs = random.randint(3, 5)
            
            for _ in range(num_jobs):
                title = random.choice(titles)
                employer = random.choice(employers)
                location = random.choice(locations)
                job_type = random.choice(job_types)
                experience_level = random.choice(experience_levels)
                
                # Generate random salary range based on experience level
                if experience_level == 'entry':
                    salary_min = random.randint(40000, 60000)
                    salary_max = random.randint(60000, 80000)
                elif experience_level == 'mid':
                    salary_min = random.randint(70000, 90000)
                    salary_max = random.randint(90000, 120000)
                elif experience_level == 'senior':
                    salary_min = random.randint(100000, 130000)
                    salary_max = random.randint(130000, 180000)
                else:  # executive
                    salary_min = random.randint(150000, 200000)
                    salary_max = random.randint(200000, 300000)
                
                # Generate a unique slug
                base_slug = slugify(f"{title}-{employer.company_name}")
                suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4))
                slug = f"{base_slug}-{suffix}"
                
                # Generate random application deadline (between 7 and 30 days from now)
                days_ahead = random.randint(7, 30)
                application_deadline = timezone.now().date() + timedelta(days=days_ahead)
                
                # Generate skills based on category and job title
                if 'Software' in title or 'Developer' in title or 'Engineer' in title:
                    skills = 'Python, JavaScript, React, SQL, Git, Agile, REST API, AWS'
                elif 'Data' in title:
                    skills = 'Python, SQL, Machine Learning, Data Analysis, Pandas, NumPy, Visualization, Statistics'
                elif 'Marketing' in title:
                    skills = 'Social Media, Content Marketing, SEO, SEM, Google Analytics, Email Marketing, CRM'
                elif 'Sales' in title:
                    skills = 'CRM, Negotiation, Communication, Prospecting, Lead Generation, Closing, Relationship Building'
                elif 'Design' in title:
                    skills = 'Adobe Creative Suite, Figma, UI/UX, Typography, Color Theory, Responsive Design'
                elif 'HR' in title or 'Human Resources' in title:
                    skills = 'Recruiting, Onboarding, Employee Relations, Benefits Administration, HRIS, Compliance'
                else:
                    skills = 'Communication, Teamwork, Problem Solving, Critical Thinking, Time Management, Adaptability'
                
                # Create the job listing
                job = JobListing.objects.create(
                    title=title,
                    slug=slug,
                    company=employer,
                    category=category,
                    description=f"""
                    {employer.company_name} is seeking a talented {title} to join our team.
                    
                    About the Role:
                    As a {title}, you will be responsible for contributing to our team's success by leveraging your skills and expertise in {category.name.lower()}.
                    
                    This is an exciting opportunity to work with a dynamic team in a fast-paced environment. You'll have the chance to work on challenging projects and make a significant impact on our company's growth.
                    
                    About {employer.company_name}:
                    {employer.company_description}
                    
                    We offer competitive compensation, excellent benefits, and opportunities for professional growth and development.
                    """,
                    requirements=f"""
                    • {experience_level.capitalize()} level experience in {category.name}
                    • Strong knowledge of {skills.split(', ')[0]} and {skills.split(', ')[1]}
                    • Bachelor's degree in {category.name} or related field
                    • Excellent communication and teamwork skills
                    • Problem-solving abilities and attention to detail
                    • Ability to work independently and as part of a team
                    • Passion for learning and staying updated with industry trends
                    """,
                    responsibilities=f"""
                    • Collaborate with cross-functional teams to achieve company goals
                    • Develop and implement strategies to improve processes and outcomes
                    • Analyze data and provide insights to inform decision-making
                    • Maintain up-to-date knowledge of industry trends and best practices
                    • Contribute to a positive and productive work environment
                    • Participate in regular team meetings and provide updates on projects
                    • Mentor junior team members as needed
                    """,
                    location=location,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    job_type=job_type,
                    experience_level=experience_level,
                    skills_required=skills,
                    application_deadline=application_deadline,
                    status='published',
                    is_featured=random.choice([True, False, False, False]),  # 25% chance of being featured
                )
                
                jobs_created += 1
                self.stdout.write(f'Created job: {job.title} at {employer.company_name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {jobs_created} sample job listings'))
