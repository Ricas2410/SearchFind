from django.urls import path
from . import views
from . import views_pro_features
from . import analytics_views
from . import subscription_management_views
from . import views_enhanced_ai

app_name = 'subscriptions'

urlpatterns = [
    # Subscription management
    path('plans/', views.subscription_plans, name='plans'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('payment/<int:subscription_id>/', views.process_payment, name='process_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('cancel/<int:subscription_id>/', views.cancel_subscription, name='cancel_subscription'),

    # Subscription management (advanced)
    path('manage/', subscription_management_views.manage_subscription, name='manage_subscription'),
    path('upgrade/<int:plan_id>/', subscription_management_views.upgrade_subscription, name='upgrade_subscription'),
    path('downgrade/<int:plan_id>/', subscription_management_views.downgrade_subscription, name='downgrade_subscription'),
    path('renew/<int:subscription_id>/', subscription_management_views.renew_subscription, name='renew_subscription'),
    path('cancel-api/', subscription_management_views.cancel_subscription_api, name='cancel_subscription_api'),
    path('invoice/<int:subscription_id>/', subscription_management_views.subscription_invoice, name='subscription_invoice'),

    # Paystack webhook
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),

    # AI features for Pro users
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('resume-builder/result/<int:builder_id>/', views.resume_builder_result, name='resume_builder_result'),
    path('resume-analysis/', views.resume_analysis, name='resume_analysis'),
    path('resume-analysis/result/<int:analysis_id>/', views.resume_analysis_result, name='resume_analysis_result'),
    path('job-match/<int:job_id>/', views.job_match_score, name='job_match_score'),

    # New Pro features
    path('interview-preparation/', views_pro_features.interview_preparation, name='interview_preparation'),
    path('interview-preparation/<int:job_id>/', views_pro_features.generate_interview_questions, name='interview_questions'),
    path('interview-preparation/<int:prep_id>/practice/<str:question_type>/<int:question_index>/',
         views_pro_features.practice_interview_answer, name='practice_answer'),
    path('interview-preparation/<int:prep_id>/feedback/<str:question_type>/<int:question_index>/',
         views_pro_features.interview_feedback, name='interview_feedback'),
    path('salary-insights/', views_pro_features.salary_insights, name='salary_insights'),
    path('salary-insights/result/<int:insight_id>/', views_pro_features.salary_insights_result, name='salary_insights_result'),
    path('career-path/', views_pro_features.career_path_planning, name='career_path'),

    # Enhanced AI features
    path('cover-letter/generate/<int:job_id>/', views_enhanced_ai.generate_improved_cover_letter, name='generate_cover_letter'),
    path('cover-letter/result/<int:analysis_id>/', views_enhanced_ai.cover_letter_result, name='cover_letter_result'),
    path('cover-letter/analyze/', views_enhanced_ai.analyze_cover_letter, name='analyze_cover_letter'),
    path('job-posting/improve/', views_enhanced_ai.improve_job_posting, name='improve_job_posting'),
    path('job-posting/improve/<int:job_id>/', views_enhanced_ai.improve_job_posting, name='improve_specific_job_posting'),
    path('job-posting/optimize-requirements/', views_enhanced_ai.optimize_requirements, name='optimize_requirements'),
    
    # Resume analysis and improvement
    path('apply-with-analysis/<int:job_id>/', views_enhanced_ai.apply_with_resume_analysis, name='apply_with_resume_analysis'),
    path('apply-with-improved-resume/<int:job_id>/', views_enhanced_ai.apply_with_improved_resume, name='apply_with_improved_resume'),
    
    # Job matching
    path('job-match/percentage/<int:job_id>/', views_enhanced_ai.get_job_match_percentage, name='get_job_match_percentage'),
    path('job-match/dashboard/', views_enhanced_ai.job_match_dashboard, name='job_match_dashboard'),
    
    # Career planning
    path('career-prospects/', views_enhanced_ai.analyze_career_prospects, name='analyze_career_prospects'),

    # Analytics
    path('analytics/employer/', analytics_views.employer_analytics_dashboard, name='employer_analytics'),
    path('analytics/job/<int:job_id>/', analytics_views.job_listing_analytics, name='job_analytics'),
    path('analytics/job-seeker/', analytics_views.job_seeker_analytics_dashboard, name='job_seeker_analytics'),

    # Admin configuration
    path('admin/paystack-config/', views.admin_paystack_config, name='admin_paystack_config'),
]
