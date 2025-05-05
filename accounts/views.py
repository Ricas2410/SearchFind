from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.contrib.auth.views import LoginView as BaseLoginView

from .forms import CustomUserCreationForm, JobSeekerProfileForm, EmployerProfileForm
from .models import CustomUser
from jobs.models import BlockedUser
from .social_auth_config import get_social_auth_status, ensure_site_exists

class CustomLoginView(BaseLoginView):
    """Custom login view that includes social authentication status."""
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        """Add social authentication status to the context."""
        context = super().get_context_data(**kwargs)
        # Ensure site exists for social auth
        ensure_site_exists()
        context['social_auth_status'] = get_social_auth_status()
        return context

class SignUpView(CreateView):
    """View for user registration."""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'

    def get_context_data(self, **kwargs):
        """Add social authentication status to the context."""
        context = super().get_context_data(**kwargs)
        # Ensure site exists for social auth
        ensure_site_exists()
        context['social_auth_status'] = get_social_auth_status()
        return context

    def form_valid(self, form):
        user = form.save()
        # Send verification email
        user.is_active = False
        user.save()

        # Create verification token and send email
        from django.contrib.sites.shortcuts import get_current_site
        from django.template.loader import render_to_string
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.core.mail import EmailMultiAlternatives
        from .tokens import account_activation_token
        from jobs.models import SiteSettings

        # Get site settings
        site_settings = SiteSettings.get_settings()

        current_site = get_current_site(self.request)
        mail_subject = 'Activate your SearchFind account'

        # Context for email template
        context = {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'site_name': site_settings.site_name,
            'contact_email': site_settings.contact_email,
            'support_email': site_settings.support_email,
            'year': timezone.now().year,
        }

        # Render HTML email
        html_message = render_to_string('accounts/account_activation_email.html', context)

        # Create plain text version
        text_message = f"""
Hi {user.first_name},

Thank you for registering with {site_settings.site_name}! Please click on the link below to confirm your email address and activate your account:

http://{current_site.domain}{reverse('accounts:activate', kwargs={'uidb64': context['uid'], 'token': context['token']})}

If you didn't register for an account on {site_settings.site_name}, please ignore this email.

Best regards,
The {site_settings.site_name} Team
        """

        # Send email with both HTML and plain text versions
        from_email = site_settings.contact_email or 'noreply@searchfind.com'
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=text_message,
            from_email=from_email,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        messages.success(self.request, _('Your account has been created successfully! Please check your email to activate your account.'))
        return redirect('accounts:activation_sent')

@login_required
def profile_view(request):
    """View for displaying user profile."""
    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'accounts/profile_dashboard.html')
    return render(request, 'accounts/profile.html')

@login_required
def profile_detail(request, user_id):
    """View for displaying another user's profile."""
    user = get_object_or_404(CustomUser, id=user_id)

    # Check if there's a connection between the users
    connection = None
    if request.user.is_authenticated and request.user.id != user.id:
        from messaging.models import Connection
        from django.db.models import Q

        connection = Connection.objects.filter(
            (Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user))
        ).first()

    context = {
        'profile_user': user,
        'connection': connection
    }

    return render(request, 'accounts/profile_detail.html', context)

@login_required
def edit_profile(request):
    """View for editing user profile based on user type."""
    user = request.user

    if user.user_type == 'job_seeker':
        if request.method == 'POST':
            form = JobSeekerProfileForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, _('Your profile has been updated successfully!'))
                return redirect('accounts:profile')
        else:
            form = JobSeekerProfileForm(instance=user)
    elif user.user_type == 'employer':
        if request.method == 'POST':
            form = EmployerProfileForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, _('Your profile has been updated successfully!'))
                return redirect('accounts:profile')
        else:
            form = EmployerProfileForm(instance=user)
    else:
        messages.error(request, _('Invalid user type.'))
        return redirect('home')

    context = {
        'form': form,
        'user_type': user.user_type
    }

    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'accounts/edit_profile_dashboard.html', context)

    return render(request, 'accounts/edit_profile.html', context)

@login_required
def switch_user_type(request):
    """View for switching between job seeker and employer roles."""
    user = request.user

    if request.method == 'POST':
        new_type = request.POST.get('user_type')

        if new_type in ['job_seeker', 'employer']:
            user.user_type = new_type
            user.save()
            messages.success(request, _('Your account type has been switched successfully!'))
        else:
            messages.error(request, _('Invalid user type.'))

    return redirect('accounts:profile')

def activation_sent(request):
    """View for displaying a message that activation email has been sent."""
    return render(request, 'accounts/activation_sent.html')

def activate(request, uidb64, token):
    """View for activating a user account."""
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str
    from .tokens import account_activation_token
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, _('Your account has been activated successfully!'))
        return redirect('jobs:home')
    else:
        messages.error(request, _('Activation link is invalid or has expired!'))
        return redirect('jobs:home')

@login_required
def privacy_settings(request):
    """View for managing privacy settings."""
    user = request.user

    # Only job seekers can set privacy settings
    if user.user_type != 'job_seeker':
        messages.error(request, _('Only job seekers can access privacy settings.'))
        return redirect('accounts:profile')

    # Get blocked users
    blocked_users = BlockedUser.objects.filter(user=user)

    if request.method == 'POST':
        # Update privacy settings
        user.is_profile_public = 'is_profile_public' in request.POST
        user.show_resume = 'show_resume' in request.POST
        user.show_contact_info = 'show_contact_info' in request.POST
        user.show_education = 'show_education' in request.POST
        user.show_experience = 'show_experience' in request.POST
        user.show_skills = 'show_skills' in request.POST

        user.save()

        messages.success(request, _('Your privacy settings have been updated successfully!'))
        return redirect('accounts:privacy_settings')

    context = {
        'blocked_users': blocked_users,
    }

    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'accounts/privacy_settings_dashboard.html', context)

    return render(request, 'accounts/privacy_settings.html', context)

@login_required
@require_POST
def block_user(request, user_id):
    """View for blocking a user."""
    user_to_block = get_object_or_404(CustomUser, id=user_id)

    # Can't block yourself
    if user_to_block == request.user:
        messages.error(request, _('You cannot block yourself.'))
        return redirect('accounts:profile')

    # Check if already blocked
    if BlockedUser.objects.filter(user=request.user, blocked_user=user_to_block).exists():
        messages.info(request, _('This user is already blocked.'))
    else:
        reason = request.POST.get('reason', '')
        BlockedUser.objects.create(
            user=request.user,
            blocked_user=user_to_block,
            reason=reason
        )
        messages.success(request, _('User has been blocked successfully.'))

    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'accounts:profile'))

@login_required
@require_POST
def unblock_user(request, blocked_id):
    """View for unblocking a user."""
    blocked = get_object_or_404(BlockedUser, id=blocked_id, user=request.user)
    blocked.delete()

    messages.success(request, _('User has been unblocked successfully.'))

    # Redirect back to the same page (dashboard or regular)
    if request.GET.get('dashboard') == 'true':
        return redirect(reverse('accounts:privacy_settings') + '?dashboard=true')
    return redirect('accounts:privacy_settings')

@login_required
def download_data(request):
    """View for downloading user data."""
    user = request.user

    # Create a dictionary with all user data
    user_data = {
        'personal_info': {
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'bio': user.bio,
            'location': user.location,
            'user_type': user.get_user_type_display(),
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
        }
    }

    # Add job seeker specific data
    if user.user_type == 'job_seeker':
        from jobs.models import JobApplication, SavedJob

        # Get applications
        applications = JobApplication.objects.filter(applicant=user)
        application_data = []
        for app in applications:
            application_data.append({
                'job_title': app.job.title,
                'company': app.job.company.name if app.job.company else None,
                'status': app.get_status_display(),
                'applied_date': app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # Get saved jobs
        saved_jobs = SavedJob.objects.filter(user=user)
        saved_job_data = []
        for saved in saved_jobs:
            saved_job_data.append({
                'job_title': saved.job.title,
                'company': saved.job.company.name if saved.job.company else None,
                'saved_date': saved.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        user_data['job_seeker_info'] = {
            'job_title': user.job_title,
            'skills': user.skills,
            'experience': user.experience,
            'education': user.education,
            'applications': application_data,
            'saved_jobs': saved_job_data,
        }

    # Add employer specific data
    elif user.user_type == 'employer':
        from jobs.models import JobListing, Company

        # Get job listings
        job_listings = JobListing.objects.filter(posted_by=user)
        job_listing_data = []
        for job in job_listings:
            job_listing_data.append({
                'title': job.title,
                'company': job.company.name if job.company else None,
                'status': job.get_status_display(),
                'created_date': job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'application_count': job.applications.count(),
            })

        # Get companies
        companies = Company.objects.filter(owner=user)
        company_data = []
        for company in companies:
            company_data.append({
                'name': company.name,
                'website': company.website,
                'industry': company.industry,
                'size': company.get_size_display(),
                'created_date': company.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        user_data['employer_info'] = {
            'company_name': user.company_name,
            'company_website': user.company_website,
            'company_description': user.company_description,
            'industry': user.industry,
            'company_size': user.get_company_size_display() if user.company_size else None,
            'job_listings': job_listing_data,
            'companies': company_data,
        }

    # Convert to JSON
    import json
    from django.http import HttpResponse

    response = HttpResponse(json.dumps(user_data, indent=4), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{user.username}_data.json"'

    return response

@login_required
@require_POST
def delete_account(request):
    """View for deleting user account."""
    user = request.user
    password = request.POST.get('password', '')
    confirm_delete = request.POST.get('confirm_delete', '') == 'on'

    # Verify password and confirmation
    if not confirm_delete:
        messages.error(request, _('You must confirm that you understand this action is permanent.'))
        return redirect('accounts:privacy_settings')

    if not user.check_password(password):
        messages.error(request, _('Incorrect password. Account deletion failed.'))
        if request.GET.get('dashboard') == 'true':
            return redirect(reverse('accounts:privacy_settings') + '?dashboard=true')
        return redirect('accounts:privacy_settings')

    # Log the user out and delete the account
    username = user.username
    logout(request)
    user.delete()

    messages.success(request, _(f'Your account ({username}) has been permanently deleted.'))
    return redirect('jobs:home')
