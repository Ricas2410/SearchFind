from django.urls import path
from . import views
from . import views_company

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<slug:slug>/', views.job_detail, name='job_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),

    # Employer dashboard and job management
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('create-job/', views.create_job, name='create_job'),
    path('edit-job/<slug:slug>/', views.edit_job, name='edit_job'),
    path('update-job-status/', views.update_job_status, name='update_job_status'),
    path('extend-deadline/', views.extend_deadline, name='extend_deadline'),
    path('bulk-update-job-status/', views.bulk_update_job_status, name='bulk_update_job_status'),
    path('bulk-extend-deadline/', views.bulk_extend_deadline, name='bulk_extend_deadline'),
    path('renew-job/<int:job_id>/', views.renew_job, name='renew_job'),
    path('process-payment/<int:renewal_id>/', views.process_payment, name='process_payment'),

    # Job seeker dashboard
    path('job-seeker/dashboard/', views.job_seeker_dashboard, name='job_seeker_dashboard'),
    path('toggle-save-job/<int:job_id>/', views.toggle_save_job, name='toggle_save_job'),

    # Application management
    path('applications/<int:job_id>/', views.applications_list, name='applications_list'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('update-application-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
    path('job-analytics/<int:job_id>/', views.job_analytics, name='job_analytics'),
    path('send-application-message/<int:application_id>/', views.send_application_message, name='send_application_message'),
    path('withdraw-application/<int:application_id>/', views.withdraw_application, name='withdraw_application'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('cookies/', views.cookies, name='cookies'),
    path('faq/', views.faq, name='faq'),
    path('legal/<slug:slug>/', views.legal_page, name='legal_page'),

    # Companies
    path('companies/', views_company.company_list, name='company_list'),
    path('companies/create/', views_company.create_company, name='create_company'),
    path('companies/<slug:slug>/edit/', views_company.edit_company, name='edit_company'),
    path('companies/<slug:slug>/', views_company.company_detail, name='company_detail'),
    path('my-companies/', views_company.my_companies, name='my_companies'),

    # Newsletter
    path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('unsubscribe/', views.unsubscribe_newsletter, name='unsubscribe_newsletter'),
    path('unsubscribe/<str:email>/<str:token>/', views.unsubscribe_confirm, name='unsubscribe_confirm'),

    # Company Connections and Followers
    path('connect-with-company/<int:company_id>/', views.connect_with_company, name='connect_with_company'),
    path('approve-connection/<int:connection_id>/', views.approve_connection, name='approve_connection'),
    path('reject-connection/<int:connection_id>/', views.reject_connection, name='reject_connection'),
    path('follow-company/<int:company_id>/', views.follow_company, name='follow_company'),
    path('manage-connections/', views.manage_connections, name='manage_connections'),
    path('manage-followers/', views.manage_followers, name='manage_followers'),
    path('my-connections/', views.my_connections, name='my_connections'),
    path('my-followed-companies/', views.my_followed_companies, name='my_followed_companies'),
    path('remove-connection/<int:connection_id>/', views.remove_connection, name='remove_connection'),
]
