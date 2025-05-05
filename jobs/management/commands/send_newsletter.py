from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

from jobs.models import Newsletter, JobListing
import datetime

class Command(BaseCommand):
    help = 'Send newsletter emails to subscribers with recommended jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subject',
            type=str,
            help='Email subject',
            default='Latest Job Opportunities from SearchFind'
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Custom message to include in the email',
            default=''
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Include jobs posted in the last X days',
            default=7
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of jobs to include',
            default=10
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help='Send a test email to this address instead of all subscribers',
            default=None
        )

    def handle(self, *args, **options):
        subject = options['subject']
        custom_message = options['message']
        days = options['days']
        limit = options['limit']
        test_email = options['test_email']
        
        # Get active subscribers
        if test_email:
            recipients = [test_email]
            self.stdout.write(self.style.WARNING(f'Sending test email to {test_email}'))
        else:
            subscribers = Newsletter.objects.filter(is_active=True)
            recipients = [subscriber.email for subscriber in subscribers]
            self.stdout.write(self.style.SUCCESS(f'Found {len(recipients)} active subscribers'))
        
        if not recipients:
            self.stdout.write(self.style.ERROR('No recipients found. Aborting.'))
            return
        
        # Get recent jobs
        cutoff_date = timezone.now() - datetime.timedelta(days=days)
        recent_jobs = JobListing.objects.filter(
            created_at__gte=cutoff_date,
            status='published',
            application_deadline__gt=timezone.now()
        ).order_by('-is_featured', '-created_at')[:limit]
        
        self.stdout.write(self.style.SUCCESS(f'Found {recent_jobs.count()} recent jobs to include'))
        
        if not recent_jobs:
            self.stdout.write(self.style.ERROR('No recent jobs found. Aborting.'))
            return
        
        # Prepare email context
        context = {
            'jobs': recent_jobs,
            'custom_message': custom_message,
            'date': timezone.now(),
            'unsubscribe_url': f"{settings.SITE_URL}/unsubscribe/",
        }
        
        # Render email templates
        html_message = render_to_string('emails/newsletter.html', context)
        plain_message = render_to_string('emails/newsletter_plain.html', context)
        
        # Send emails
        sent_count = 0
        failed_count = 0
        
        for email in recipients:
            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send()
                sent_count += 1
                self.stdout.write(f'Sent newsletter to {email}')
            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f'Failed to send to {email}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Newsletter sent to {sent_count} subscribers ({failed_count} failed)'))
