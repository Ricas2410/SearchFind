from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jobs.models import JobListing

class InterviewPrep(models.Model):
    """Model for storing interview preparation data."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interview_preps')
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='interview_preps')
    
    # Generated questions
    technical_questions = models.JSONField(default=list)
    behavioral_questions = models.JSONField(default=list)
    company_questions = models.JSONField(default=list)
    
    # User's practice answers
    practice_answers = models.JSONField(default=dict)
    
    # AI feedback on practice answers
    feedback = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Interview Preparation')
        verbose_name_plural = _('Interview Preparations')
        ordering = ['-created_at']
        unique_together = ['user', 'job_listing']
    
    def __str__(self):
        return f"Interview Prep for {self.user.email} - {self.job_listing.title}"


class SalaryInsights(models.Model):
    """Model for storing salary insights data."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salary_insights')
    job_title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    experience_level = models.CharField(max_length=100)
    
    # Salary data
    salary_range_min = models.DecimalField(max_digits=12, decimal_places=2)
    salary_range_max = models.DecimalField(max_digits=12, decimal_places=2)
    median_salary = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Additional insights
    factors = models.JSONField(default=list)
    negotiation_tips = models.JSONField(default=list)
    industry_trends = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Salary Insights')
        verbose_name_plural = _('Salary Insights')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Salary Insights for {self.job_title} in {self.location}"


class CareerPath(models.Model):
    """Model for storing career path recommendations."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='career_paths')
    current_role = models.CharField(max_length=255)
    target_role = models.CharField(max_length=255, blank=True, null=True)
    
    # Career path data
    path_steps = models.JSONField(default=list)
    skills_to_acquire = models.JSONField(default=list)
    certifications = models.JSONField(default=list)
    estimated_timeline = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Career Path')
        verbose_name_plural = _('Career Paths')
        ordering = ['-created_at']
    
    def __str__(self):
        target = f" to {self.target_role}" if self.target_role else ""
        return f"Career Path for {self.user.email}: {self.current_role}{target}"
