from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan
from django.db import transaction

class Command(BaseCommand):
    help = 'Create initial subscription plans'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Check if we already have plans
            if SubscriptionPlan.objects.exists():
                self.stdout.write(self.style.SUCCESS('Subscription plans already exist. No need to create initial plans.'))
                return
            
            # Create job seeker plans
            self.stdout.write('Creating job seeker subscription plans...')
            
            # Basic Pro plan for job seekers
            SubscriptionPlan.objects.create(
                name="Job Seeker Basic Pro",
                plan_type="job_seeker",
                description="Essential pro features for job seekers",
                price=9.99,
                duration_days=30,
                resume_builder=True,
                resume_review=True,
                job_match_recommendations=False,
                company_recommendations=False
            )
            
            # Premium Pro plan for job seekers
            SubscriptionPlan.objects.create(
                name="Job Seeker Premium Pro",
                plan_type="job_seeker",
                description="Complete pro package with all features for job seekers",
                price=19.99,
                duration_days=30,
                resume_builder=True,
                resume_review=True,
                job_match_recommendations=True,
                company_recommendations=True
            )
            
            # Create employer plans
            self.stdout.write('Creating employer subscription plans...')
            
            # Basic Pro plan for employers
            SubscriptionPlan.objects.create(
                name="Employer Basic Pro",
                plan_type="employer",
                description="Essential pro features for employers",
                price=29.99,
                duration_days=30,
                featured_jobs=True,
                priority_listing=False,
                candidate_matching=False,
                advanced_analytics=False
            )
            
            # Premium Pro plan for employers
            SubscriptionPlan.objects.create(
                name="Employer Premium Pro",
                plan_type="employer",
                description="Complete pro package with all features for employers",
                price=49.99,
                duration_days=30,
                featured_jobs=True,
                priority_listing=True,
                candidate_matching=True,
                advanced_analytics=True
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully created initial subscription plans'))
