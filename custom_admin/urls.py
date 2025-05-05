from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),

    # User Management
    path('users/', views.user_management, name='user_management'),

    # Jobs Management
    path('jobs/', views.job_management, name='job_management'),
    path('job-categories/', views.job_category_management, name='job_category_management'),
    path('job-applications/', views.job_application_management, name='job_application_management'),
    path('saved-jobs/', views.saved_job_management, name='saved_job_management'),
    path('job-renewals/', views.job_renewal_management, name='job_renewal_management'),
    path('job-packages/', views.job_package_management, name='job_package_management'),
    path('job-analytics/', views.job_analytics_management, name='job_analytics_management'),
    path('export-job-analytics/', views.export_job_analytics, name='export_job_analytics'),

    # Company Management
    path('companies/', views.company_management, name='company_management'),
    path('company-connections/', views.company_connection_management, name='company_connection_management'),
    path('company-followers/', views.company_follower_management, name='company_follower_management'),
    path('trusted-companies/', views.trusted_company_management, name='trusted_company_management'),

    # Content Management
    path('testimonials/', views.testimonial_management, name='testimonial_management'),
    path('team-members/', views.team_member_management, name='team_member_management'),
    path('newsletter/', views.newsletter_management, name='newsletter_management'),
    path('hero-sections/', views.hero_section_management, name='hero_section_management'),
    path('legal-pages/', views.legal_page_management, name='legal_page_management'),
    path('notifications/', views.notification_management, name='notification_management'),

    # Subscription Management
    path('subscriptions/', views.subscription_management, name='subscription_management'),
    path('subscription-plans/', views.subscription_plan_management, name='subscription_plan_management'),
    path('user-subscriptions/', views.user_subscription_management, name='user_subscription_management'),
    path('paystack-config/', views.paystack_config_management, name='paystack_config_management'),
    path('test-paystack-payment/', views.test_paystack_payment, name='test_paystack_payment'),
    path('paystack-test/', views.simple_paystack_test, name='simple_paystack_test'),
    path('paystack-test-success/', views.paystack_test_success, name='paystack_test_success'),

    # Pro Features Management
    path('resume-analyses/', views.resume_analysis_management, name='resume_analysis_management'),
    path('resume-builders/', views.resume_builder_management, name='resume_builder_management'),
    path('job-match-scores/', views.job_match_score_management, name='job_match_score_management'),
    path('company-match-scores/', views.company_match_score_management, name='company_match_score_management'),

    # Social Account Management
    path('social-accounts/', views.social_account_management, name='social_account_management'),
    path('social-app-tokens/', views.social_app_token_management, name='social_app_token_management'),
    path('social-applications/', views.social_application_management, name='social_application_management'),

    # Settings
    path('site-settings/', views.site_settings, name='site_settings'),
]
