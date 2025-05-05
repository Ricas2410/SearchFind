from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from jobs.models import JobListing, JobApplication, SavedJob
import random
from datetime import timedelta
import os
from django.core.files.base import ContentFile

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample job seekers and applications'

    def handle(self, *args, **options):
        # Create job seeker users if they don't exist
        job_seekers = []
        job_seeker_data = [
            {
                'username': 'johndoe',
                'email': 'john.doe@example.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_type': 'job_seeker',
                'bio': 'Experienced software developer with a passion for creating efficient and scalable applications.',
                'skills': 'Python, JavaScript, React, Node.js, SQL, Git, Docker'
            },
            {
                'username': 'janesmith',
                'email': 'jane.smith@example.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'user_type': 'job_seeker',
                'bio': 'Marketing professional with expertise in digital marketing and content creation.',
                'skills': 'Social Media Marketing, SEO, Content Writing, Email Marketing, Google Analytics'
            },
            {
                'username': 'mikebrown',
                'email': 'mike.brown@example.com',
                'password': 'password123',
                'first_name': 'Mike',
                'last_name': 'Brown',
                'user_type': 'job_seeker',
                'bio': 'Data scientist with experience in machine learning and data analysis.',
                'skills': 'Python, R, Machine Learning, Data Analysis, SQL, Tableau, Statistics'
            },
            {
                'username': 'sarahjones',
                'email': 'sarah.jones@example.com',
                'password': 'password123',
                'first_name': 'Sarah',
                'last_name': 'Jones',
                'user_type': 'job_seeker',
                'bio': 'UX/UI designer focused on creating intuitive and engaging user experiences.',
                'skills': 'Figma, Adobe XD, Sketch, UI Design, UX Research, Prototyping, Wireframing'
            },
            {
                'username': 'davidwilson',
                'email': 'david.wilson@example.com',
                'password': 'password123',
                'first_name': 'David',
                'last_name': 'Wilson',
                'user_type': 'job_seeker',
                'bio': 'Project manager with a track record of delivering successful projects on time and within budget.',
                'skills': 'Project Management, Agile, Scrum, Jira, Risk Management, Stakeholder Communication'
            }
        ]
        
        for job_seeker in job_seeker_data:
            user, created = User.objects.get_or_create(
                username=job_seeker['username'],
                defaults={
                    'email': job_seeker['email'],
                    'first_name': job_seeker['first_name'],
                    'last_name': job_seeker['last_name'],
                    'user_type': job_seeker['user_type'],
                    'bio': job_seeker['bio'],
                    'skills': job_seeker['skills']
                }
            )
            
            if created:
                user.set_password(job_seeker['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created job seeker: {user.get_full_name()}'))
            else:
                self.stdout.write(f'Job seeker already exists: {user.get_full_name()}')
                
            job_seekers.append(user)
        
        # Get all published jobs
        jobs = JobListing.objects.filter(status='published')
        if not jobs.exists():
            self.stdout.write(self.style.ERROR('No published jobs found. Please run create_sample_jobs command first.'))
            return
        
        # Create sample applications and saved jobs
        applications_created = 0
        saved_jobs_created = 0
        
        # Create a dummy resume file
        dummy_resume_content = """
        RESUME
        
        Contact Information:
        Name: [Full Name]
        Email: [Email]
        Phone: [Phone Number]
        
        Summary:
        Experienced professional with skills in [Skills]. Seeking opportunities in [Field].
        
        Experience:
        [Company Name] - [Position]
        [Start Date] - [End Date]
        - [Responsibility 1]
        - [Responsibility 2]
        - [Responsibility 3]
        
        Education:
        [Degree] in [Field of Study]
        [University Name]
        [Graduation Year]
        
        Skills:
        - [Skill 1]
        - [Skill 2]
        - [Skill 3]
        - [Skill 4]
        - [Skill 5]
        
        References:
        Available upon request.
        """
        
        # Application statuses and their probabilities
        status_choices = ['pending', 'reviewed', 'shortlisted', 'rejected', 'hired']
        status_weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # 40% pending, 30% reviewed, etc.
        
        for job_seeker in job_seekers:
            # Each job seeker applies to 2-5 random jobs
            num_applications = random.randint(2, 5)
            applied_jobs = random.sample(list(jobs), min(num_applications, len(jobs)))
            
            for job in applied_jobs:
                # Create a resume file with the job seeker's name
                resume_filename = f"{job_seeker.first_name.lower()}_{job_seeker.last_name.lower()}_resume.pdf"
                
                # Personalized resume content
                personalized_resume = dummy_resume_content.replace('[Full Name]', job_seeker.get_full_name())
                personalized_resume = personalized_resume.replace('[Email]', job_seeker.email)
                personalized_resume = personalized_resume.replace('[Skills]', job_seeker.skills)
                personalized_resume = personalized_resume.replace('[Field]', job.category.name)
                
                # Create application with random status
                status = random.choices(status_choices, weights=status_weights)[0]
                
                # Random application date (between job creation and now)
                days_since_job_created = (timezone.now().date() - job.created_at.date()).days
                if days_since_job_created <= 0:
                    days_since_job_created = 1
                days_ago = random.randint(1, days_since_job_created)
                applied_at = timezone.now() - timedelta(days=days_ago)
                
                # Create the application
                application = JobApplication.objects.create(
                    job=job,
                    applicant=job_seeker,
                    status=status,
                    applied_at=applied_at,
                    cover_letter=f"""
                    Dear Hiring Manager,
                    
                    I am writing to express my interest in the {job.title} position at {job.company.company_name}. With my background in {job.category.name} and skills in {job_seeker.skills}, I believe I would be a valuable addition to your team.
                    
                    {job_seeker.bio}
                    
                    I am particularly interested in this role because it aligns with my career goals and offers an opportunity to contribute to {job.company.company_name}'s mission. I am impressed by your company's work in the industry and would be excited to be part of your team.
                    
                    Thank you for considering my application. I look forward to the opportunity to discuss how my skills and experience align with your needs.
                    
                    Sincerely,
                    {job_seeker.get_full_name()}
                    """
                )
                
                # Add resume file to the application
                application.resume.save(resume_filename, ContentFile(personalized_resume.encode('utf-8')))
                
                applications_created += 1
                self.stdout.write(f'Created application: {job_seeker.get_full_name()} applied to {job.title} at {job.company.company_name}')
            
            # Each job seeker saves 3-7 random jobs (that they haven't applied to)
            applied_job_ids = [job.id for job in applied_jobs]
            available_jobs = jobs.exclude(id__in=applied_job_ids)
            
            if available_jobs.exists():
                num_saved = random.randint(3, 7)
                saved_jobs = random.sample(list(available_jobs), min(num_saved, len(available_jobs)))
                
                for job in saved_jobs:
                    # Random saved date (between job creation and now)
                    days_since_job_created = (timezone.now().date() - job.created_at.date()).days
                    if days_since_job_created <= 0:
                        days_since_job_created = 1
                    days_ago = random.randint(1, days_since_job_created)
                    saved_at = timezone.now() - timedelta(days=days_ago)
                    
                    SavedJob.objects.create(
                        job=job,
                        user=job_seeker,
                        saved_at=saved_at
                    )
                    
                    saved_jobs_created += 1
                    self.stdout.write(f'Created saved job: {job_seeker.get_full_name()} saved {job.title} at {job.company.company_name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {applications_created} sample applications and {saved_jobs_created} saved jobs'))
