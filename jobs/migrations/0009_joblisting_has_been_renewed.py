# Generated by Django 5.2 on 2025-04-25 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_add_initial_job_packages'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblisting',
            name='has_been_renewed',
            field=models.BooleanField(default=False, help_text='Job has been renewed at least once'),
        ),
    ]
