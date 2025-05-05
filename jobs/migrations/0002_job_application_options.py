from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
        ('accounts', '0002_user_privacy_fields'),
    ]

    operations = [
        # Add new fields to JobListing
        migrations.AddField(
            model_name='joblisting',
            name='application_url',
            field=models.URLField(blank=True, help_text='External URL where candidates can apply (leave blank to use internal application)', null=True),
        ),
        migrations.AddField(
            model_name='joblisting',
            name='is_external_url_verified',
            field=models.BooleanField(default=False, help_text='Has this external URL been verified by admin?'),
        ),
        migrations.AddField(
            model_name='joblisting',
            name='is_remote',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='joblisting',
            name='cover_letter_required',
            field=models.BooleanField(default=False, help_text='Is a cover letter required for applications?'),
        ),
        
        # Update JobApplication status choices
        migrations.AlterField(
            model_name='jobapplication',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('shortlisted', 'Shortlisted'), ('interview', 'Interview'), ('rejected', 'Rejected'), ('hired', 'Hired'), ('withdrawn', 'Withdrawn')], default='pending', max_length=20),
        ),
        
        # Add new fields to JobApplication
        migrations.AddField(
            model_name='jobapplication',
            name='feedback_to_applicant',
            field=models.TextField(blank=True, help_text='Feedback that will be shared with the applicant', null=True),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='interview_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='interview_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='interview_type',
            field=models.CharField(blank=True, choices=[('in_person', 'In Person'), ('phone', 'Phone'), ('video', 'Video')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='is_withdrawn',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='withdrawal_reason',
            field=models.TextField(blank=True, null=True),
        ),
        
        # Create ApplicationMessage model
        migrations.CreateModel(
            name='ApplicationMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='jobs.jobapplication')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_application_messages', to='accounts.customuser')),
            ],
            options={
                'verbose_name': 'Application Message',
                'verbose_name_plural': 'Application Messages',
                'ordering': ['created_at'],
            },
        ),
        
        # Create BlockedUser model
        migrations.CreateModel(
            name='BlockedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blocked_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_by', to='accounts.customuser')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_users', to='accounts.customuser')),
            ],
            options={
                'verbose_name': 'Blocked User',
                'verbose_name_plural': 'Blocked Users',
                'unique_together': {('user', 'blocked_user')},
            },
        ),
    ]
