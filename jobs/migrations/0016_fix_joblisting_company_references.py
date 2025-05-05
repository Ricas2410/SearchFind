from django.db import migrations

def fix_job_company_references(apps, schema_editor):
    """Fix job listings with invalid company references."""
    JobListing = apps.get_model('jobs', 'JobListing')
    Company = apps.get_model('jobs', 'Company')
    User = apps.get_model('accounts', 'CustomUser')

    # Get the first admin user or create one if none exists
    admin_user = User.objects.filter(is_superuser=True).first()

    if not admin_user:
        # Create a default admin user if none exists
        from django.contrib.auth.hashers import make_password
        admin_user = User.objects.create(
            email='admin@searchfind.com',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            password=make_password('admin123')
        )

    # Get all companies
    companies = list(Company.objects.all())

    # If there are no companies, create one
    if not companies:
        # Create a default company
        default_company = Company.objects.create(
            name="Default Company",
            slug="default-company",
            description="Default company for migration purposes",
            industry="technology",
            company_size="1-10",
            headquarters="Default Location",
            status="approved",
            owner=admin_user
        )
        companies = [default_company]

    # Get the first company to use as default
    default_company = companies[0]

    # Update all job listings with invalid company references
    for job in JobListing.objects.all():
        if not Company.objects.filter(id=job.company_id).exists():
            job.company = default_company
            job.save()

def reverse_func(apps, schema_editor):
    # No need to reverse this migration
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0015_alter_joblisting_company'),
    ]

    operations = [
        migrations.RunPython(fix_job_company_references, reverse_func),
    ]
