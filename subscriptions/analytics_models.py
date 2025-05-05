from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jobs.models import JobListing, Company

class EmployerAnalytics(models.Model):
    """Model for storing employer analytics data."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()

    # Job listing metrics
    total_job_listings = models.PositiveIntegerField(default=0)
    active_job_listings = models.PositiveIntegerField(default=0)
    expired_job_listings = models.PositiveIntegerField(default=0)

    # Application metrics
    total_applications = models.PositiveIntegerField(default=0)
    new_applications = models.PositiveIntegerField(default=0)
    reviewed_applications = models.PositiveIntegerField(default=0)
    shortlisted_applications = models.PositiveIntegerField(default=0)
    rejected_applications = models.PositiveIntegerField(default=0)

    # Engagement metrics
    job_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    average_time_on_page = models.FloatField(default=0)

    # Conversion metrics
    view_to_application_rate = models.FloatField(default=0)
    application_to_shortlist_rate = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Employer Analytics')
        verbose_name_plural = _('Employer Analytics')
        ordering = ['-date']
        unique_together = ['company', 'date']

    def __str__(self):
        return f"Analytics for {self.company.name} on {self.date}"


class JobSeekerAnalytics(models.Model):
    """Model for storing job seeker analytics data."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()

    # Application metrics
    total_applications = models.PositiveIntegerField(default=0)
    new_applications = models.PositiveIntegerField(default=0)
    viewed_applications = models.PositiveIntegerField(default=0)
    shortlisted_applications = models.PositiveIntegerField(default=0)
    rejected_applications = models.PositiveIntegerField(default=0)

    # Profile metrics
    profile_views = models.PositiveIntegerField(default=0)
    profile_completion = models.FloatField(default=0)

    # Engagement metrics
    job_views = models.PositiveIntegerField(default=0)
    saved_jobs = models.PositiveIntegerField(default=0)

    # Match metrics
    average_job_match = models.FloatField(default=0)
    high_match_jobs = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Job Seeker Analytics')
        verbose_name_plural = _('Job Seeker Analytics')
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"Analytics for {self.user.email} on {self.date}"


class JobListingAnalytics(models.Model):
    """Model for storing job listing analytics data."""
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='subscription_analytics')
    date = models.DateField()

    # View metrics
    views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)

    # Application metrics
    applications = models.PositiveIntegerField(default=0)
    qualified_applications = models.PositiveIntegerField(default=0)

    # Engagement metrics
    average_time_on_page = models.FloatField(default=0)
    bounce_rate = models.FloatField(default=0)

    # Conversion metrics
    view_to_application_rate = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Job Listing Analytics')
        verbose_name_plural = _('Job Listing Analytics')
        ordering = ['-date']
        unique_together = ['job', 'date']

    def __str__(self):
        return f"Analytics for {self.job.title} on {self.date}"
