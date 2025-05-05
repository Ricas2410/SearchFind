from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jobs.models import JobListing, Company

class ResumeAnalysis(models.Model):
    """Model for storing AI resume analysis results."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume_analyses')
    resume_file = models.FileField(upload_to='ai_analyses/resumes/', null=True, blank=True)
    
    # Parsed resume data
    parsed_skills = models.JSONField(default=dict, help_text=_('Skills extracted from resume'))
    parsed_experience = models.JSONField(default=dict, help_text=_('Experience extracted from resume'))
    parsed_education = models.JSONField(default=dict, help_text=_('Education extracted from resume'))
    
    # Analysis results
    skill_score = models.PositiveSmallIntegerField(default=0, help_text=_('Score from 0-100 for skills'))
    experience_score = models.PositiveSmallIntegerField(default=0, help_text=_('Score from 0-100 for experience'))
    education_score = models.PositiveSmallIntegerField(default=0, help_text=_('Score from 0-100 for education'))
    overall_score = models.PositiveSmallIntegerField(default=0, help_text=_('Overall resume score from 0-100'))
    
    # Improvement suggestions
    suggestions = models.JSONField(default=list, help_text=_('List of improvement suggestions'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Resume Analysis')
        verbose_name_plural = _('Resume Analyses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Resume Analysis for {self.user.email}"


class JobMatchScore(models.Model):
    """Model for storing job match scores for users."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_match_scores')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='match_scores')
    
    # Match scores
    skills_match = models.PositiveSmallIntegerField(default=0, help_text=_('Skills match percentage'))
    experience_match = models.PositiveSmallIntegerField(default=0, help_text=_('Experience match percentage'))
    education_match = models.PositiveSmallIntegerField(default=0, help_text=_('Education match percentage'))
    overall_match = models.PositiveSmallIntegerField(default=0, help_text=_('Overall match percentage'))
    
    # Match details
    matching_skills = models.JSONField(default=list, help_text=_('List of matching skills'))
    missing_skills = models.JSONField(default=list, help_text=_('List of missing skills'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Job Match Score')
        verbose_name_plural = _('Job Match Scores')
        ordering = ['-overall_match']
        unique_together = ['user', 'job']
    
    def __str__(self):
        return f"{self.user.email} - {self.job.title} ({self.overall_match}%)"


class CompanyMatchScore(models.Model):
    """Model for storing company match scores for users."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_match_scores')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='match_scores')
    
    # Match scores
    culture_match = models.PositiveSmallIntegerField(default=0, help_text=_('Culture match percentage'))
    industry_match = models.PositiveSmallIntegerField(default=0, help_text=_('Industry match percentage'))
    skill_match = models.PositiveSmallIntegerField(default=0, help_text=_('Skill match percentage'))
    overall_match = models.PositiveSmallIntegerField(default=0, help_text=_('Overall match percentage'))
    
    # Match details
    match_reasons = models.JSONField(default=list, help_text=_('Reasons for the match'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Company Match Score')
        verbose_name_plural = _('Company Match Scores')
        ordering = ['-overall_match']
        unique_together = ['user', 'company']
    
    def __str__(self):
        return f"{self.user.email} - {self.company.name} ({self.overall_match}%)"


class CoverLetterAnalysis(models.Model):
    """Model for storing cover letter analysis results."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cover_letter_analyses')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='cover_letter_analyses', null=True, blank=True)
    
    # Cover letter content
    original_content = models.TextField(blank=True, null=True, help_text=_('Original cover letter content'))
    improved_content = models.TextField(blank=True, null=True, help_text=_('AI-improved cover letter content'))
    
    # Analysis data
    analysis_data = models.JSONField(default=dict, help_text=_('Analysis data and metadata'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cover Letter Analysis')
        verbose_name_plural = _('Cover Letter Analyses')
        ordering = ['-created_at']
    
    def __str__(self):
        job_info = f" for {self.job.title}" if self.job else ""
        return f"Cover Letter Analysis - {self.user.email}{job_info}"


class ResumeBuilder(models.Model):
    """Model for storing AI-generated resume content."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume_builders')
    job_listing = models.ForeignKey(JobListing, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_resumes')
    
    # Original resume content
    original_content = models.TextField(blank=True, null=True)
    
    # Generated content
    generated_summary = models.TextField(blank=True, null=True)
    generated_skills = models.JSONField(default=list)
    generated_experience = models.JSONField(default=list)
    generated_education = models.JSONField(default=list)
    
    # Final resume
    final_content = models.TextField(blank=True, null=True)
    final_file = models.FileField(upload_to='ai_generated/resumes/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Resume Builder')
        verbose_name_plural = _('Resume Builders')
        ordering = ['-created_at']
    
    def __str__(self):
        job_info = f" for {self.job_listing.title}" if self.job_listing else ""
        return f"Resume Builder - {self.user.email}{job_info}"
