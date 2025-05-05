from django.core.management.base import BaseCommand
from jobs.models import Company
from accounts.models import CustomUser
from django.utils.text import slugify
from django.db import transaction

class Command(BaseCommand):
    help = 'Create a default company for migration purposes'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Check if we already have companies
            if Company.objects.exists():
                self.stdout.write(self.style.SUCCESS('Companies already exist. No need to create a default company.'))
                return
            
            # Get a user to be the owner
            user = CustomUser.objects.filter(is_superuser=True).first()
            if not user:
                user = CustomUser.objects.first()
            
            if not user:
                self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
                return
            
            # Create a default company
            company = Company.objects.create(
                name="Default Company",
                slug=slugify("Default Company"),
                owner=user,
                description="Default company created for migration purposes",
                industry="technology",
                company_size="1-10",
                headquarters="Default Location",
                status="approved"
            )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created default company with ID: {company.id}'))
