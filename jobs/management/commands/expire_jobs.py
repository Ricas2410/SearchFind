from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import JobListing
from django.utils.translation import gettext_lazy as _

class Command(BaseCommand):
    help = 'Marks jobs with passed application deadlines as expired'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Get published jobs with passed deadlines
        expired_jobs = JobListing.objects.filter(
            status='published',
            application_deadline__lt=now
        )
        
        count = expired_jobs.count()
        
        if count > 0:
            # Update status to expired
            expired_jobs.update(status='expired')
            self.stdout.write(self.style.SUCCESS(f'Successfully marked {count} jobs as expired'))
        else:
            self.stdout.write(self.style.SUCCESS('No jobs to expire'))
