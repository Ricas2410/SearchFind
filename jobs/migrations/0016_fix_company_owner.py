from django.db import migrations

def fix_company_owner(apps, schema_editor):
    """Fix company owner field."""
    Company = apps.get_model('jobs', 'Company')
    User = apps.get_model('accounts', 'CustomUser')
    
    # Get the first admin user or create one if none exists
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        # Create a default admin user if none exists
        admin_user = User.objects.create(
            email='admin@searchfind.com',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        admin_user.set_password('admin123')
        admin_user.save()
    
    # Update all companies without an owner
    for company in Company.objects.filter(owner__isnull=True):
        company.owner = admin_user
        company.save()

def reverse_func(apps, schema_editor):
    # No need to reverse this migration
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0015_alter_joblisting_company'),
    ]

    operations = [
        migrations.RunPython(fix_company_owner, reverse_func),
    ]
