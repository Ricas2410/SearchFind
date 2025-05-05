from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from jobs.models import JobListing
from django.utils.translation import gettext_lazy as _
import datetime

class Command(BaseCommand):
    help = 'Sends email notifications for jobs that are about to expire'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=3,
            help='Number of days before expiration to send warning'
        )

    def handle(self, *args, **options):
        days_before = options['days']
        now = timezone.now()
        
        # Calculate the date range for jobs about to expire
        warning_date = now + datetime.timedelta(days=days_before)
        
        # Get published jobs that will expire in the specified number of days
        # We want jobs where the deadline is between now and the warning date
        expiring_jobs = JobListing.objects.filter(
            status='published',
            application_deadline__gt=now,
            application_deadline__lte=warning_date
        )
        
        count = 0
        for job in expiring_jobs:
            # Send email to the employer
            if job.company.email:
                days_left = (job.application_deadline - now).days
                hours_left = int(((job.application_deadline - now).seconds) / 3600)
                
                # Prepare the context for the email template
                context = {
                    'job': job,
                    'days_left': days_left,
                    'hours_left': hours_left,
                    'expiration_date': job.application_deadline,
                    'dashboard_url': f"{settings.SITE_URL}/employer/dashboard/",
                    'job_url': f"{settings.SITE_URL}/jobs/{job.slug}/",
                }
                
                # Render the email content from template
                subject = _('Job Listing Expiration Warning: {0}').format(job.title)
                html_message = render_to_string('emails/job_expiration_warning.html', context)
                plain_message = render_to_string('emails/job_expiration_warning_plain.html', context)
                
                # Send the email
                try:
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[job.company.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'Sent expiration warning for job: {job.title}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to send email for job {job.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully sent {count} expiration warning emails'))
