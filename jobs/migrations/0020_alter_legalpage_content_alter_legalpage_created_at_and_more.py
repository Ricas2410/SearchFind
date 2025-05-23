# Generated by Django 5.1.8 on 2025-04-27 02:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0019_alter_jobanalytics_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='legalpage',
            name='content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='legalpage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='legalpage',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='legalpage',
            name='page_type',
            field=models.CharField(choices=[('terms', 'Terms & Conditions'), ('privacy', 'Privacy Policy'), ('cookies', 'Cookie Policy'), ('other', 'Other')], default='other', max_length=20),
        ),
        migrations.AlterField(
            model_name='legalpage',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='legalpage',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='legalpage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='CompanyConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('message', models.TextField(blank=True, help_text='Message sent with the connection request', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections', to='jobs.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_connections', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Company Connection',
                'verbose_name_plural': 'Company Connections',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'company')},
            },
        ),
        migrations.CreateModel(
            name='CompanyFollower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='jobs.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed_companies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Company Follower',
                'verbose_name_plural': 'Company Followers',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'company')},
            },
        ),
    ]
