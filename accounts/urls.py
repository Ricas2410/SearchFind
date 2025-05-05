from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(
        next_page='jobs:home'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='jobs:home'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('switch-user-type/', views.switch_user_type, name='switch_user_type'),

    # Privacy settings
    path('privacy-settings/', views.privacy_settings, name='privacy_settings'),
    path('block-user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock-user/<int:blocked_id>/', views.unblock_user, name='unblock_user'),

    # Account management
    path('download-data/', views.download_data, name='download_data'),
    path('delete-account/', views.delete_account, name='delete_account'),

    # Account activation
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activation-sent/', views.activation_sent, name='activation_sent'),

    # Password reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
