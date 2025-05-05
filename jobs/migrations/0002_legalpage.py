from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegalPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(help_text='URL-friendly name for the page', unique=True, verbose_name='Slug')),
                ('page_type', models.CharField(choices=[('terms', 'Terms & Conditions'), ('privacy', 'Privacy Policy'), ('cookies', 'Cookie Policy'), ('other', 'Other Legal Page')], default='other', max_length=20, verbose_name='Page Type')),
                ('content', models.TextField(help_text='HTML content for the page', verbose_name='Content')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Legal Page',
                'verbose_name_plural': 'Legal Pages',
                'ordering': ['title'],
            },
        ),
    ]
