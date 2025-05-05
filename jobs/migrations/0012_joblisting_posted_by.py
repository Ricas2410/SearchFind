from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0011_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblisting',
            name='posted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posted_jobs', to=settings.AUTH_USER_MODEL),
        ),
    ]
