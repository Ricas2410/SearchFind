# Generated by Django 5.2 on 2025-04-25 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_privacy_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_pro',
            field=models.BooleanField(default=False, help_text='Whether user has an active pro subscription'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='pro_expiry_date',
            field=models.DateTimeField(blank=True, help_text='When the pro subscription expires', null=True),
        ),
    ]
