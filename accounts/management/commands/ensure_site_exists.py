from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Ensures that the default site exists in the database'

    def handle(self, *args, **options):
        # Check if the default site exists
        if not Site.objects.filter(id=settings.SITE_ID).exists():
            # Create the default site
            site = Site.objects.create(
                id=settings.SITE_ID,
                domain='127.0.0.1:8000',
                name='SearchFind'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created default site: {site.name} ({site.domain})'))
        else:
            site = Site.objects.get(id=settings.SITE_ID)
            self.stdout.write(self.style.SUCCESS(f'Default site already exists: {site.name} ({site.domain})'))
