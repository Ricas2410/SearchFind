from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SubscriptionPlan, UserSubscription, PaystackConfig
from .ai_models import ResumeAnalysis, JobMatchScore, CompanyMatchScore, ResumeBuilder

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'duration_days', 'is_active')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'plan_type', 'description', 'price', 'duration_days', 'is_active')
        }),
        (_('Job Seeker Features'), {
            'fields': ('resume_builder', 'resume_review', 'job_match_recommendations', 'company_recommendations')
        }),
        (_('Employer Features'), {
            'fields': ('featured_jobs', 'priority_listing', 'candidate_matching', 'advanced_analytics')
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'amount_paid')
    list_filter = ('status', 'plan')
    search_fields = ('user__email', 'user__username', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['activate_subscriptions', 'cancel_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.activate()
        self.message_user(request, _('Selected subscriptions have been activated.'))
    activate_subscriptions.short_description = _('Activate selected subscriptions')
    
    def cancel_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.cancel()
        self.message_user(request, _('Selected subscriptions have been cancelled.'))
    cancel_subscriptions.short_description = _('Cancel selected subscriptions')


@admin.register(PaystackConfig)
class PaystackConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_live', 'currency', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('public_key', 'secret_key', 'is_live', 'webhook_secret', 'currency')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one configuration
        return PaystackConfig.objects.count() == 0


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'overall_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(JobMatchScore)
class JobMatchScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'overall_match', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username', 'job__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CompanyMatchScore)
class CompanyMatchScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'overall_match', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username', 'company__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ResumeBuilder)
class ResumeBuilderAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_listing', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username', 'job_listing__title')
    readonly_fields = ('created_at', 'updated_at')
