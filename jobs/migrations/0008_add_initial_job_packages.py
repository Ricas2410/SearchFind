from django.db import migrations

def create_initial_packages(apps, schema_editor):
    JobPackage = apps.get_model('jobs', 'JobPackage')
    
    # Basic package
    JobPackage.objects.create(
        name='Basic',
        description='Standard job listing with basic features.',
        price=49.99,
        duration_days=30,
        featured_job=False,
        priority_placement=False,
        is_active=True
    )
    
    # Premium package
    JobPackage.objects.create(
        name='Premium',
        description='Enhanced visibility with featured placement and extended duration.',
        price=99.99,
        duration_days=60,
        featured_job=True,
        priority_placement=False,
        is_active=True
    )
    
    # Enterprise package
    JobPackage.objects.create(
        name='Enterprise',
        description='Maximum exposure with top placement, featured status, and longest duration.',
        price=199.99,
        duration_days=90,
        featured_job=True,
        priority_placement=True,
        is_active=True
    )

def remove_initial_packages(apps, schema_editor):
    JobPackage = apps.get_model('jobs', 'JobPackage')
    JobPackage.objects.filter(name__in=['Basic', 'Premium', 'Enterprise']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_jobpackage_jobrenewal'),
    ]

    operations = [
        migrations.RunPython(create_initial_packages, remove_initial_packages),
    ]
