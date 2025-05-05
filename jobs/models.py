from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_countries.fields import CountryField

class JobCategory(models.Model):
    """Model for job categories."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Job Category')
        verbose_name_plural = _('Job Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('jobs:category_detail', kwargs={'slug': self.slug})

class JobListing(models.Model):
    """Model for job listings."""
    JOB_TYPE_CHOICES = (
        ('full_time', _('Full Time')),
        ('part_time', _('Part Time')),
        ('contract', _('Contract')),
        ('internship', _('Internship')),
        ('remote', _('Remote')),
    )

    EXPERIENCE_LEVEL_CHOICES = (
        ('entry', _('Entry Level')),
        ('mid', _('Mid Level')),
        ('senior', _('Senior Level')),
        ('executive', _('Executive Level')),
    )

    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('closed', _('Closed')),
        ('expired', _('Expired')),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='jobs')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_listings', null=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='entry')
    skills_required = models.TextField(help_text=_('Enter skills separated by commas'))
    application_deadline = models.DateTimeField(blank=True, null=True, help_text=_('Deadline for job applications'))

    # Application options
    application_url = models.URLField(blank=True, null=True,
                                     help_text=_('External URL where candidates can apply (leave blank to use internal application)'))
    is_external_url_verified = models.BooleanField(default=False,
                                                 help_text=_('Has this external URL been verified by admin?'))
    is_remote = models.BooleanField(default=False)

    # Cover letter requirement
    cover_letter_required = models.BooleanField(default=False,
                                              help_text=_('Is a cover letter required for applications?'))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    has_been_renewed = models.BooleanField(default=False, help_text=_('Job has been renewed at least once'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Job Listing')
        verbose_name_plural = _('Job Listings')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'slug': self.slug})

    @property
    def is_expired(self):
        if not self.application_deadline:
            return False
        return self.application_deadline < timezone.now()

    def get_skills_as_list(self):
        return [skill.strip() for skill in self.skills_required.split(',')]

class JobApplication(models.Model):
    """Model for job applications."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('reviewed', _('Reviewed')),
        ('shortlisted', _('Shortlisted')),
        ('interview', _('Interview')),
        ('rejected', _('Rejected')),
        ('hired', _('Hired')),
        ('withdrawn', _('Withdrawn')),
    )

    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='applications/resumes/')
    cover_letter = models.TextField(blank=True, null=True)

    # Application status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True, help_text=_('Timestamp of the last message sent'))

    # Employer feedback
    employer_notes = models.TextField(blank=True, null=True)
    feedback_to_applicant = models.TextField(blank=True, null=True,
                                           help_text=_('Feedback that will be shared with the applicant'))

    # Interview scheduling
    interview_date = models.DateTimeField(blank=True, null=True)
    interview_location = models.CharField(max_length=255, blank=True, null=True)
    interview_type = models.CharField(max_length=50, blank=True, null=True,
                                    choices=(
                                        ('in_person', _('In Person')),
                                        ('phone', _('Phone')),
                                        ('video', _('Video')),
                                    ))

    # Applicant actions
    is_withdrawn = models.BooleanField(default=False)
    withdrawal_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Job Application')
        verbose_name_plural = _('Job Applications')
        ordering = ['-applied_at']
        # Ensure a user can only apply once to a job
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.email} - {self.job.title}"

class SavedJob(models.Model):
    """Model for saved/bookmarked jobs."""
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='saved_by')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Saved Job')
        verbose_name_plural = _('Saved Jobs')
        ordering = ['-saved_at']
        unique_together = ('job', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.job.title}"

class Notification(models.Model):
    """Model for user notifications."""
    NOTIFICATION_TYPES = (
        ('application_status', _('Application Status Update')),
        ('new_job', _('New Job Matching Skills')),
        ('application_received', _('Application Received')),
        ('message', _('New Message')),
        ('system', _('System Notification')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_job = models.ForeignKey(JobListing, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    related_application = models.ForeignKey(JobApplication, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"

class ApplicationMessage(models.Model):
    """Model for messages between employers and applicants regarding a specific job application."""
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_application_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Application Message')
        verbose_name_plural = _('Application Messages')
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class BlockedUser(models.Model):
    """Model for blocked users to prevent messaging."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked_users')
    blocked_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked_by')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Blocked User')
        verbose_name_plural = _('Blocked Users')
        unique_together = ('user', 'blocked_user')

    def __str__(self):
        return f"{self.user.email} blocked {self.blocked_user.email}"

class Newsletter(models.Model):
    """Model for newsletter subscriptions."""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Newsletter Subscription')
        verbose_name_plural = _('Newsletter Subscriptions')
        ordering = ['-created_at']

    def __str__(self):
        return self.email

class Testimonial(models.Model):
    """Model for user testimonials."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='testimonials')
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    user_role = models.CharField(max_length=100, help_text=_('e.g. Software Developer, HR Manager'))
    profile_image = models.ImageField(upload_to='testimonials/', blank=True, null=True, help_text=_('Profile image for the testimonial'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Testimonial')
        verbose_name_plural = _('Testimonials')
        ordering = ['-created_at']

    def __str__(self):
        return f"Testimonial by {self.user.get_full_name()}"

class TeamMember(models.Model):
    """Model for team members."""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0, help_text=_('Order of appearance'))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Team Member')
        verbose_name_plural = _('Team Members')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class TrustedCompany(models.Model):
    """Model for trusted companies displayed on the homepage."""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='trusted_companies/')
    website = models.URLField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0, help_text=_('Order of appearance'))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Trusted Company')
        verbose_name_plural = _('Trusted Companies')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Company(models.Model):
    """Model for companies that can post jobs."""

    def get_full_name(self):
        """Return the full name of the company."""
        return self.name
    COMPANY_SIZE_CHOICES = (
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001+', '1001+ employees'),
    )

    STATUS_CHOICES = (
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    )

    INDUSTRY_CHOICES = (
        ('accounting', _('Accounting')),
        ('advertising', _('Advertising')),
        ('aerospace', _('Aerospace')),
        ('agriculture', _('Agriculture')),
        ('automotive', _('Automotive')),
        ('banking', _('Banking')),
        ('biotechnology', _('Biotechnology')),
        ('construction', _('Construction')),
        ('consulting', _('Consulting')),
        ('consumer_goods', _('Consumer Goods')),
        ('education', _('Education')),
        ('energy', _('Energy')),
        ('entertainment', _('Entertainment')),
        ('fashion', _('Fashion')),
        ('finance', _('Finance')),
        ('food_beverage', _('Food & Beverage')),
        ('government', _('Government')),
        ('healthcare', _('Healthcare')),
        ('hospitality', _('Hospitality')),
        ('insurance', _('Insurance')),
        ('legal', _('Legal')),
        ('manufacturing', _('Manufacturing')),
        ('marketing', _('Marketing')),
        ('media', _('Media')),
        ('non_profit', _('Non-Profit')),
        ('pharmaceutical', _('Pharmaceutical')),
        ('real_estate', _('Real Estate')),
        ('retail', _('Retail')),
        ('technology', _('Technology')),
        ('telecommunications', _('Telecommunications')),
        ('transportation', _('Transportation')),
        ('travel', _('Travel')),
        ('utilities', _('Utilities')),
        ('other', _('Other')),
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_companies')
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='company_covers/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES)
    other_industry = models.CharField(max_length=100, blank=True, null=True, help_text=_('If you selected "Other" as industry, please specify'))
    company_size = models.CharField(max_length=50, choices=COMPANY_SIZE_CHOICES)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    country = CountryField(blank_label=_('Select Country'), blank=True, null=True)
    headquarters = models.CharField(max_length=255, help_text=_('City or specific location'))
    specialties = models.TextField(blank=True, null=True, help_text=_('Comma-separated list of specialties'))
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('jobs:company_detail', kwargs={'slug': self.slug})

    @property
    def job_count(self):
        return self.jobs.filter(status='published').count()

    @property
    def active_job_count(self):
        from django.utils import timezone
        from django.db.models import Q
        return self.jobs.filter(
            status='published'
        ).filter(
            Q(application_deadline__gt=timezone.now()) | Q(application_deadline__isnull=True)
        ).count()

    def is_connected_with_user(self, user):
        """Check if a user is connected with this company."""
        if not user or not user.is_authenticated:
            return False
        return self.connections.filter(user=user, status='approved').exists()

    def get_connection_status(self, user):
        """Get the connection status between a user and this company."""
        if not user or not user.is_authenticated:
            return None
        try:
            connection = self.connections.get(user=user)
            return connection.status
        except CompanyConnection.DoesNotExist:
            return None

    def is_followed_by_user(self, user):
        """Check if a user is following this company."""
        if not user or not user.is_authenticated:
            return False
        return self.followers.filter(user=user).exists()

    @property
    def follower_count(self):
        """Get the number of followers for this company."""
        return self.followers.count()

    @property
    def connection_count(self):
        """Get the number of approved connections for this company."""
        return self.connections.filter(status='approved').count()

class JobPackage(models.Model):
    """Model for job posting packages."""
    DURATION_CHOICES = (
        (30, _('30 Days')),
        (60, _('60 Days')),
        (90, _('90 Days')),
        (180, _('6 Months')),
        (365, _('1 Year')),
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(choices=DURATION_CHOICES, default=30)
    featured_job = models.BooleanField(default=False, help_text=_('Job will be featured in listings'))
    priority_placement = models.BooleanField(default=False, help_text=_('Job will appear at the top of search results'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Job Package')
        verbose_name_plural = _('Job Packages')
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ${self.price} ({self.duration_days} days)"

class JobRenewal(models.Model):
    """Model for job renewal transactions."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )

    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='renewals')
    package = models.ForeignKey(JobPackage, on_delete=models.SET_NULL, null=True, related_name='renewals')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_renewals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    old_expiry_date = models.DateTimeField(blank=True, null=True)
    new_expiry_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Job Renewal')
        verbose_name_plural = _('Job Renewals')
        ordering = ['-created_at']

    def __str__(self):
        return f"Renewal for {self.job.title} - {self.status}"




class JobAnalytics(models.Model):
    """Model for tracking job performance analytics."""
    job = models.OneToOneField(JobListing, on_delete=models.CASCADE, related_name='analytics')

    # View statistics
    total_views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)

    # Application statistics
    total_applications = models.PositiveIntegerField(default=0)
    application_rate = models.FloatField(default=0.0, help_text=_('Applications per view (%)'))

    # Conversion statistics
    shortlisted_count = models.PositiveIntegerField(default=0)
    interview_count = models.PositiveIntegerField(default=0)
    hired_count = models.PositiveIntegerField(default=0)

    # Time-based metrics
    avg_time_to_apply = models.DurationField(null=True, blank=True, help_text=_('Average time between view and application'))
    time_to_first_application = models.DurationField(null=True, blank=True)

    # Demographic data (anonymized)
    applicant_locations = models.JSONField(default=dict, blank=True, help_text=_('Count of applicants by location'))

    # Engagement metrics
    save_count = models.PositiveIntegerField(default=0, help_text=_('Number of times job was saved'))
    click_through_rate = models.FloatField(default=0.0, help_text=_('Percentage of views that resulted in application page view'))

    # Referral tracking
    referral_sources = models.JSONField(default=dict, blank=True, help_text=_('Count of views by referral source'))

    # Daily tracking data
    daily_views = models.JSONField(default=dict, blank=True, help_text=_('Daily view counts'))
    daily_applications = models.JSONField(default=dict, blank=True, help_text=_('Daily application counts'))

    def __str__(self):
        return f"Analytics for {self.job.title}"

    def update_application_stats(self):
        """Update application statistics based on current data."""
        # Count applications by status
        applications = self.job.applications.all()
        self.total_applications = applications.count()

        if self.total_views > 0:
            self.application_rate = (self.total_applications / self.total_views) * 100

        self.shortlisted_count = applications.filter(status='shortlisted').count()
        self.interview_count = applications.filter(status='interview').count()
        self.hired_count = applications.filter(status='hired').count()

        # Update location data
        locations = {}
        for app in applications:
            location = app.applicant.location or 'Unknown'
            locations[location] = locations.get(location, 0) + 1
        self.applicant_locations = locations

        # Update save count
        self.save_count = self.job.saved_by.count()

        self.save()


class CompanyConnection(models.Model):
    """Model for connections between users and companies."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_connections')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='connections')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True, help_text=_('Message sent with the connection request'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Company Connection')
        verbose_name_plural = _('Company Connections')
        ordering = ['-created_at']
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user.email} - {self.company.name} ({self.get_status_display()})"


class CompanyFollower(models.Model):
    """Model for users following companies to receive job notifications."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_companies')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Company Follower')
        verbose_name_plural = _('Company Followers')
        ordering = ['-created_at']
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user.email} follows {self.company.name}"


class LegalPage(models.Model):
    """Model for legal pages like Terms & Conditions, Privacy Policy, etc."""
    PAGE_TYPE_CHOICES = (
        ('terms', _('Terms & Conditions')),
        ('privacy', _('Privacy Policy')),
        ('cookies', _('Cookie Policy')),
        ('faq', _('FAQ')),
        ('other', _('Other')),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    page_type = models.CharField(max_length=20, choices=PAGE_TYPE_CHOICES, default='other')
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Legal Page')
        verbose_name_plural = _('Legal Pages')
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('jobs:legal_page', kwargs={'slug': self.slug})


class SiteSettings(models.Model):
    """Model for storing site-wide settings."""
    site_name = models.CharField(max_length=100, default='SearchFind')
    site_logo = models.ImageField(upload_to='site_settings/', null=True, blank=True, help_text=_('Site logo for emails and branding'))
    site_favicon = models.ImageField(upload_to='site_settings/', null=True, blank=True, help_text=_('Site favicon'))
    primary_color = models.CharField(max_length=20, default='#3B82F6', help_text=_('Primary color in hex format (e.g. #3B82F6)'))
    secondary_color = models.CharField(max_length=20, default='#1E40AF', help_text=_('Secondary color in hex format (e.g. #1E40AF)'))

    # Contact Information
    contact_email = models.EmailField(default='contact@searchfind.com')
    support_email = models.EmailField(default='support@searchfind.com')
    phone_number = models.CharField(max_length=20, default='+1 (123) 456-7890', blank=True)
    address_line1 = models.CharField(max_length=100, default='123 Main Street', blank=True)
    address_line2 = models.CharField(max_length=100, default='Suite 456', blank=True)
    city = models.CharField(max_length=50, default='New York', blank=True)
    state = models.CharField(max_length=50, default='NY', blank=True)
    postal_code = models.CharField(max_length=20, default='10001', blank=True)
    country = models.CharField(max_length=50, default='United States', blank=True)

    # Business Hours
    business_hours = models.TextField(default='Monday - Friday: 9:00 AM - 6:00 PM\nSaturday: 10:00 AM - 2:00 PM\nSunday: Closed',
                                     help_text=_('Business hours, one per line'), blank=True)

    # Social Media
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            # Update existing instance instead of creating a new one
            self.pk = SiteSettings.objects.first().pk
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create site settings."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class HeroSection(models.Model):
    """Model for customizing the hero section on various pages."""
    SECTION_TYPE_CHOICES = (
        ('home', _('Home Page')),
        ('jobs', _('Jobs Page')),
        ('companies', _('Companies Page')),
        ('candidates', _('Candidates Page')),
    )

    section_type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES, unique=True)
    title = models.CharField(max_length=255, default="Find Your Dream Job")
    subtitle = models.CharField(max_length=255, default="Search thousands of jobs from top companies")
    background_image = models.ImageField(upload_to='hero_images/', blank=True, null=True,
                                       help_text=_('Background image for the hero section (recommended size: 1920x600px)'))
    mobile_background_image = models.ImageField(upload_to='hero_images/', blank=True, null=True,
                                              help_text=_('Background image for the hero section on mobile (recommended size: 768x500px)'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Hero Section')
        verbose_name_plural = _('Hero Sections')

    def __str__(self):
        return f"Hero Section - {self.get_section_type_display()}"

    @classmethod
    def get_section(cls, section_type):
        """Get the hero section for a specific page type or create a default one if none exists."""
        section = cls.objects.filter(section_type=section_type, is_active=True).first()
        if not section:
            section = cls.objects.create(section_type=section_type, is_active=True)
        return section
