from django.core.management.base import BaseCommand
from jobs.models import JobListing, Company
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix job listings with invalid company references'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Get all companies
            companies = list(Company.objects.all())
            
            # If there are no companies, we can't fix the issue
            if not companies:
                self.stdout.write(self.style.ERROR('No companies found. Please create at least one company first.'))
                return
            
            # Get the first company to use as default
            default_company = companies[0]
            
            # Get all job listings with invalid company references
            for job in JobListing.objects.all():
                if not Company.objects.filter(id=job.company_id).exists():
                    self.stdout.write(f'Fixing job {job.id}: {job.title} - changing company_id from {job.company_id} to {default_company.id}')
                    job.company = default_company
                    job.save(update_fields=['company'])
            
            self.stdout.write(self.style.SUCCESS('Successfully fixed job listings with invalid company references'))
