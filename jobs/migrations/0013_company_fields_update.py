from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from django_countries.fields import CountryField


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0012_joblisting_posted_by'),
    ]

    operations = [
        # First, add the new fields to Company
        migrations.AddField(
            model_name='company',
            name='country',
            field=CountryField(blank=True, blank_label='Select Country', null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_industry',
            field=models.CharField(blank=True, help_text='If you selected "Other" as industry, please specify', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='headquarters',
            field=models.CharField(help_text='City or specific location', max_length=255),
        ),
        # Make posted_by nullable
        migrations.AlterField(
            model_name='joblisting',
            name='posted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='job_listings', to=settings.AUTH_USER_MODEL),
        ),
    ]
