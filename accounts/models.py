from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds fields for user role and profile information.
    """
    USER_TYPE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='job_seeker',
        verbose_name=_('User Type')
    )

    # Subscription status
    is_pro = models.BooleanField(default=False, help_text=_('Whether user has an active pro subscription'))
    pro_expiry_date = models.DateTimeField(null=True, blank=True, help_text=_('When the pro subscription expires'))

    def has_active_pro(self):
        """Check if the user has an active pro subscription."""
        # First check the built-in fields
        if self.is_pro and self.pro_expiry_date and self.pro_expiry_date > timezone.now():
            return True

        # Then check for active subscriptions in the subscription model
        try:
            from subscriptions.models import UserSubscription

            # Check if the user has any active subscription
            active_subscription = UserSubscription.objects.filter(
                user=self,
                status='active',
                end_date__gte=timezone.now()
            ).exists()

            # If we found an active subscription but the is_pro flag is not set,
            # update the user's pro status
            if active_subscription and not self.is_pro:
                self.update_pro_status()

            return active_subscription
        except Exception as e:
            # If there's any error (like the model doesn't exist), fall back to the is_pro field
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking pro status: {str(e)}")
            return self.is_pro

    def get_profile_completion_percentage(self):
        """Calculate the profile completion percentage."""
        fields_to_check = [
            'bio', 'location', 'phone_number', 'profile_picture',
            'skills', 'experience', 'education', 'resume',
            'job_title'
        ]

        # Count how many fields are filled
        filled_fields = sum(1 for field in fields_to_check if getattr(self, field))

        # Calculate percentage
        percentage = int((filled_fields / len(fields_to_check)) * 100)

        return percentage
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Additional fields for job seekers
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text=_('Comma-separated list of skills'))
    job_title = models.CharField(max_length=255, blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    # Privacy settings for job seekers
    is_profile_public = models.BooleanField(default=False, help_text=_('Allow employers to find your profile'))
    show_resume = models.BooleanField(default=False, help_text=_('Make your resume visible to employers'))
    show_contact_info = models.BooleanField(default=False, help_text=_('Show your contact information to employers'))
    show_education = models.BooleanField(default=True)
    show_experience = models.BooleanField(default=True)
    show_skills = models.BooleanField(default=True)

    # Additional fields for employers
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_size = models.CharField(max_length=50, blank=True, null=True, choices=(
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001+', '1001+ employees'),
    ))
    industry = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Ensure superusers always have user_type set to 'admin'
        if self.is_superuser and self.user_type != 'admin':
            self.user_type = 'admin'
        super().save(*args, **kwargs)

    def update_pro_status(self):
        """Update pro status based on subscriptions."""
        from subscriptions.models import UserSubscription

        # Check for active subscription
        active_subscription = UserSubscription.objects.filter(
            user=self,
            status='active',
            end_date__gt=timezone.now()
        ).first()

        if active_subscription:
            self.is_pro = True
            self.pro_expiry_date = active_subscription.end_date
        else:
            self.is_pro = False

        self.save(update_fields=['is_pro', 'pro_expiry_date'])

    def calculate_profile_completeness(self):
        """
        Calculate the profile completeness percentage based on filled fields.
        Returns a tuple of (percentage, missing_fields) where missing_fields is a list
        of field names that are empty.
        """
        missing_fields = []

        # Common fields for all user types
        if not self.first_name:
            missing_fields.append('First Name')
        if not self.last_name:
            missing_fields.append('Last Name')
        if not self.phone_number:
            missing_fields.append('Phone Number')
        if not self.profile_picture:
            missing_fields.append('Profile Picture')
        if not self.location:
            missing_fields.append('Location')

        # Job seeker specific fields
        if self.user_type == 'job_seeker':
            if not self.bio:
                missing_fields.append('Bio')
            if not self.job_title:
                missing_fields.append('Job Title')
            if not self.skills:
                missing_fields.append('Skills')
            if not self.experience:
                missing_fields.append('Experience')
            if not self.education:
                missing_fields.append('Education')
            if not self.resume:
                missing_fields.append('Resume')

            # Total fields for job seekers: 11
            total_fields = 11

        # Employer specific fields
        elif self.user_type == 'employer':
            if not self.company_name:
                missing_fields.append('Company Name')
            if not self.company_website:
                missing_fields.append('Company Website')
            if not self.company_description:
                missing_fields.append('Company Description')
            if not self.company_logo:
                missing_fields.append('Company Logo')
            if not self.company_size:
                missing_fields.append('Company Size')
            if not self.industry:
                missing_fields.append('Industry')

            # Total fields for employers: 11
            total_fields = 11
        else:
            # Admin or other user types
            total_fields = 5

        # Calculate percentage
        filled_fields = total_fields - len(missing_fields)
        percentage = int((filled_fields / total_fields) * 100)

        return (percentage, missing_fields)
