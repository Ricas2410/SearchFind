from django.db import migrations
from django.conf import settings

def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    
    # Create the default site if it doesn't exist
    if not Site.objects.filter(id=settings.SITE_ID).exists():
        Site.objects.create(
            id=settings.SITE_ID,
            domain='127.0.0.1:8000',
            name='SearchFind'
        )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_is_pro_customuser_pro_expiry_date'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_site),
    ]
