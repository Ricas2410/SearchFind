from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from django.utils.text import slugify


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0010_testimonial_profile_image'),
    ]

    operations = [
        # Create the Company model
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='company_covers/')),
                ('website', models.URLField(blank=True, null=True)),
                ('description', models.TextField()),
                ('short_description', models.CharField(blank=True, max_length=255, null=True)),
                ('industry', models.CharField(max_length=100)),
                ('company_size', models.CharField(choices=[('1-10', '1-10 employees'), ('11-50', '11-50 employees'), ('51-200', '51-200 employees'), ('201-500', '201-500 employees'), ('501-1000', '501-1000 employees'), ('1001+', '1001+ employees')], max_length=50)),
                ('founded_year', models.PositiveIntegerField(blank=True, null=True)),
                ('headquarters', models.CharField(max_length=255)),
                ('specialties', models.TextField(blank=True, help_text='Comma-separated list of specialties', null=True)),
                ('facebook', models.URLField(blank=True, null=True)),
                ('twitter', models.URLField(blank=True, null=True)),
                ('linkedin', models.URLField(blank=True, null=True)),
                ('instagram', models.URLField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_companies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
                'ordering': ['-created_at'],
            },
        ),
    ]
