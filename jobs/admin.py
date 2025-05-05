from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import redirect
from .models import (
    JobCategory, JobListing, JobApplication, SavedJob, Notification,
    JobPackage, JobRenewal, JobAnalytics, TrustedCompany, TeamMember,
    Testimonial, Newsletter, ApplicationMessage, BlockedUser, Company,
    LegalPage, CompanyConnection, CompanyFollower, SiteSettings, HeroSection
)
from django.utils.translation import gettext_lazy as _
from .admin_views import send_newsletter_view

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ('applied_at',)
    fields = ('applicant', 'status', 'applied_at', 'resume', 'employer_notes')

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'status', 'is_featured', 'created_at', 'application_deadline', 'views_count', 'is_expired')
    list_filter = ('status', 'job_type', 'experience_level', 'is_featured', 'created_at', 'application_deadline')
    search_fields = ('title', 'company__email', 'company__company_name', 'location', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ('views_count', 'created_at', 'updated_at', 'is_expired')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'company', 'category', 'status')
        }),
        (_('Job Details'), {
            'fields': ('description', 'requirements', 'responsibilities', 'location', 'is_remote', 'job_type', 'experience_level')
        }),
        (_('Salary Information'), {
            'fields': ('salary_min', 'salary_max')
        }),
        (_('Additional Information'), {
            'fields': ('skills_required', 'application_deadline', 'is_featured', 'cover_letter_required')
        }),
        (_('Application Method'), {
            'fields': ('application_url', 'is_external_url_verified')
        }),
        (_('Statistics'), {
            'fields': ('views_count', 'created_at', 'updated_at', 'is_expired')
        }),
    )
    inlines = [JobApplicationInline]
    actions = ['mark_as_expired', 'mark_as_closed', 'mark_as_published', 'extend_deadline_30_days']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user)

    def is_expired(self, obj):
        """Display if the job is expired based on deadline."""
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = _('Expired')

    def mark_as_expired(self, request, queryset):
        """Mark selected jobs as expired."""
        updated = queryset.update(status='expired')
        self.message_user(request, _(f'{updated} jobs marked as expired.'))
    mark_as_expired.short_description = _('Mark selected jobs as expired')

    def mark_as_closed(self, request, queryset):
        """Mark selected jobs as closed."""
        updated = queryset.update(status='closed')
        self.message_user(request, _(f'{updated} jobs marked as closed.'))
    mark_as_closed.short_description = _('Mark selected jobs as closed')

    def mark_as_published(self, request, queryset):
        """Mark selected jobs as published."""
        updated = queryset.update(status='published')
        self.message_user(request, _(f'{updated} jobs marked as published.'))
    mark_as_published.short_description = _('Mark selected jobs as published')

    def extend_deadline_30_days(self, request, queryset):
        """Extend application deadline by 30 days for selected jobs."""
        from django.utils import timezone
        import datetime

        count = 0
        for job in queryset:
            # If deadline is in the past or None, set it to 30 days from now
            if not job.application_deadline or job.application_deadline < timezone.now():
                job.application_deadline = timezone.now() + datetime.timedelta(days=30)
            else:
                # Otherwise, add 30 days to the current deadline
                job.application_deadline = job.application_deadline + datetime.timedelta(days=30)

            # If job was expired, reactivate it
            if job.status == 'expired':
                job.status = 'published'

            job.save()
            count += 1

        self.message_user(request, _(f'Application deadline extended by 30 days for {count} jobs.'))
    extend_deadline_30_days.short_description = _('Extend deadline by 30 days')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('job__title', 'applicant__email', 'applicant__first_name', 'applicant__last_name')
    readonly_fields = ('applied_at', 'updated_at')
    date_hierarchy = 'applied_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 'employer':
            return qs.filter(job__company=request.user)
        return qs.filter(applicant=request.user)

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('job__title', 'user__email')
    readonly_fields = ('saved_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(JobPackage)
class JobPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'featured_job', 'priority_placement', 'is_active')
    list_filter = ('featured_job', 'priority_placement', 'is_active', 'duration_days')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_active')

@admin.register(JobRenewal)
class JobRenewalAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'package', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('job__title', 'user__email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(JobAnalytics)
class JobAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('job', 'total_views', 'unique_views', 'total_applications', 'application_rate')
    search_fields = ('job__title',)
    readonly_fields = ('job', 'total_views', 'unique_views', 'total_applications', 'application_rate',
                      'shortlisted_count', 'interview_count', 'hired_count', 'avg_time_to_apply',
                      'time_to_first_application', 'applicant_locations', 'save_count', 'click_through_rate',
                      'referral_sources', 'daily_views', 'daily_applications')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(job__company=request.user)

@admin.register(TrustedCompany)
class TrustedCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'website_link', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('order', 'is_active')
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = _('Logo Preview')

    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
        return "-"
    website_link.short_description = _('Website')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'industry', 'company_size', 'status', 'owner_link', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'industry', 'company_size')
    search_fields = ('name', 'description', 'industry', 'headquarters', 'owner__email', 'owner__first_name', 'owner__last_name')
    readonly_fields = ('logo_preview', 'cover_preview', 'created_at', 'updated_at')
    list_editable = ('status', 'is_featured')
    actions = ['approve_companies', 'reject_companies']

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'owner', 'status', 'is_featured')
        }),
        (_('Company Details'), {
            'fields': ('industry', 'company_size', 'founded_year', 'headquarters', 'description', 'short_description', 'specialties')
        }),
        (_('Media'), {
            'fields': ('logo', 'logo_preview', 'cover_image', 'cover_preview')
        }),
        (_('Contact Information'), {
            'fields': ('website', 'facebook', 'twitter', 'linkedin', 'instagram')
        }),
        (_('Rejection'), {
            'fields': ('rejection_reason',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = _('Logo Preview')

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 300px;" />', obj.cover_image.url)
        return "No Cover Image"
    cover_preview.short_description = _('Cover Image Preview')

    def owner_link(self, obj):
        url = f"/admin/accounts/customuser/{obj.owner.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.owner.get_full_name() or obj.owner.email)
    owner_link.short_description = _('Owner')

    def approve_companies(self, request, queryset):
        updated = queryset.update(status='approved', rejection_reason=None)
        self.message_user(request, _(f'{updated} companies have been approved.'))
    approve_companies.short_description = _('Approve selected companies')

    def reject_companies(self, request, queryset):
        updated = queryset.update(status='rejected', rejection_reason='Rejected by admin')
        self.message_user(request, _(f'{updated} companies have been rejected.'))
    reject_companies.short_description = _('Reject selected companies')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'photo_preview', 'position', 'email', 'order', 'is_active')
    list_filter = ('is_active', 'position')
    search_fields = ('name', 'position', 'bio', 'email')
    list_editable = ('order', 'is_active')
    readonly_fields = ('photo_preview',)
    fieldsets = (
        (None, {
            'fields': ('name', 'position', 'bio', 'is_active', 'order')
        }),
        (_('Photo'), {
            'fields': ('photo', 'photo_preview')
        }),
        (_('Contact Information'), {
            'fields': ('email', 'linkedin', 'twitter')
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.photo.url)
        return "No Photo"
    photo_preview.short_description = _('Photo Preview')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_image_preview', 'rating_stars', 'user_role', 'content_excerpt', 'is_active', 'created_at')
    list_filter = ('rating', 'is_active', 'created_at', 'user_role')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'content', 'user_role')
    list_editable = ('is_active',)
    readonly_fields = ('profile_image_preview',)
    fieldsets = (
        (None, {
            'fields': ('user', 'user_role', 'rating', 'content', 'is_active')
        }),
        (_('Profile Image'), {
            'fields': ('profile_image', 'profile_image_preview')
        }),
    )

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;" />', obj.profile_image.url)
        elif obj.user.profile_picture:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;" />', obj.user.profile_picture.url)
        return "No Image"
    profile_image_preview.short_description = _('Profile Image')

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    rating_stars.short_description = _('Rating')

    def content_excerpt(self, obj):
        if len(obj.content) > 100:
            return obj.content[:100] + '...'
        return obj.content
    content_excerpt.short_description = _('Content')

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at', 'send_newsletter_button')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    list_editable = ('is_active',)
    actions = ['mark_active', 'mark_inactive']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-newsletter/', self.admin_site.admin_view(send_newsletter_view), name='send_newsletter'),
        ]
        return custom_urls + urls

    def send_newsletter_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Send Newsletter</a>',
            '/admin/jobs/newsletter/send-newsletter/'
        )
    send_newsletter_button.short_description = _('Send Newsletter')
    send_newsletter_button.allow_tags = True

    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f'{updated} subscribers marked as active.'))
    mark_active.short_description = _('Mark selected subscribers as active')

    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} subscribers marked as inactive.'))
    mark_inactive.short_description = _('Mark selected subscribers as inactive')


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    """Admin interface for managing legal pages."""
    list_display = ('title', 'page_type', 'slug', 'is_active', 'last_updated')
    list_filter = ('page_type', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'content_preview')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'page_type', 'is_active')
        }),
        (_('Content'), {
            'fields': ('content', 'content_preview'),
            'description': _('HTML content for the page. You can use the rich text editor to format the content.')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        """Display a preview of the HTML content."""
        if obj.content:
            return format_html('<div class="legal-content-preview">{}</div>', obj.content)
        return _("No content")
    content_preview.short_description = _('Content Preview')

    def last_updated(self, obj):
        """Format the last updated date."""
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    last_updated.short_description = _('Last Updated')

    class Media:
        css = {
            'all': ('admin/css/legal_page_admin.css',)
        }
        js = ('admin/js/legal_page_admin.js',)


@admin.register(CompanyConnection)
class CompanyConnectionAdmin(admin.ModelAdmin):
    """Admin interface for managing company connections."""
    list_display = ('user', 'company', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company__name', 'message')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['approve_connections', 'reject_connections']

    fieldsets = (
        (None, {
            'fields': ('user', 'company', 'status')
        }),
        (_('Message'), {
            'fields': ('message',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def approve_connections(self, request, queryset):
        """Approve selected connection requests."""
        updated = queryset.update(status='approved')
        self.message_user(request, _(f'{updated} connection requests approved.'))
    approve_connections.short_description = _('Approve selected connections')

    def reject_connections(self, request, queryset):
        """Reject selected connection requests."""
        updated = queryset.update(status='rejected')
        self.message_user(request, _(f'{updated} connection requests rejected.'))
    reject_connections.short_description = _('Reject selected connections')


@admin.register(CompanyFollower)
class CompanyFollowerAdmin(admin.ModelAdmin):
    """Admin interface for managing company followers."""
    list_display = ('user', 'company', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company__name')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('user', 'company')
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin interface for managing site settings."""
    list_display = ('site_name', 'logo_preview', 'contact_email', 'phone_number')
    readonly_fields = ('logo_preview', 'favicon_preview')
    fieldsets = (
        (_('Site Information'), {
            'fields': ('site_name', 'contact_email', 'support_email')
        }),
        (_('Branding'), {
            'fields': ('site_logo', 'logo_preview', 'site_favicon', 'favicon_preview', 'primary_color', 'secondary_color')
        }),
        (_('Contact Information'), {
            'fields': ('phone_number', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'business_hours')
        }),
        (_('Social Media'), {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url')
        }),
    )

    def logo_preview(self, obj):
        if obj.site_logo:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 300px;" />', obj.site_logo.url)
        return "No Logo"
    logo_preview.short_description = _('Logo Preview')

    def favicon_preview(self, obj):
        if obj.site_favicon:
            return format_html('<img src="{}" style="max-height: 32px; max-width: 32px;" />', obj.site_favicon.url)
        return "No Favicon"
    favicon_preview.short_description = _('Favicon Preview')

    def has_add_permission(self, request):
        # Only allow adding if no settings exist yet
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    """Admin interface for managing hero sections."""
    list_display = ('get_section_type_display', 'title', 'background_preview', 'is_active', 'updated_at')
    list_filter = ('section_type', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'subtitle')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'background_preview', 'mobile_background_preview')
    fieldsets = (
        (None, {
            'fields': ('section_type', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'subtitle')
        }),
        (_('Background Images'), {
            'fields': ('background_image', 'background_preview', 'mobile_background_image', 'mobile_background_preview'),
            'description': _('Upload background images for desktop and mobile views.')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def background_preview(self, obj):
        if obj.background_image:
            return format_html('<img src="{}" style="max-height: 150px; max-width: 400px;" />', obj.background_image.url)
        return "No background image"
    background_preview.short_description = _('Background Preview')

    def mobile_background_preview(self, obj):
        if obj.mobile_background_image:
            return format_html('<img src="{}" style="max-height: 150px; max-width: 200px;" />', obj.mobile_background_image.url)
        return "No mobile background image"
    mobile_background_preview.short_description = _('Mobile Background Preview')