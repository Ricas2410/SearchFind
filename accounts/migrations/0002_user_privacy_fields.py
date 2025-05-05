from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='job_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='experience',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='education',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_profile_public',
            field=models.BooleanField(default=False, help_text='Allow employers to find your profile'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_resume',
            field=models.BooleanField(default=False, help_text='Make your resume visible to employers'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_contact_info',
            field=models.BooleanField(default=False, help_text='Show your contact information to employers'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_education',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_experience',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_skills',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='company_size',
            field=models.CharField(blank=True, choices=[('1-10', '1-10 employees'), ('11-50', '11-50 employees'), ('51-200', '51-200 employees'), ('201-500', '201-500 employees'), ('501-1000', '501-1000 employees'), ('1001+', '1001+ employees')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='industry',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
