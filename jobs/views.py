from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    JobListing, JobCategory, JobApplication, SavedJob, Notification,
    ApplicationMessage, BlockedUser, Newsletter, Testimonial, TeamMember, TrustedCompany,
    JobPackage, JobRenewal, JobAnalytics, LegalPage, Company, CompanyConnection, CompanyFollower,
    SiteSettings
)
from .forms import JobListingForm, JobApplicationForm, JobSearchForm

def home(request):
    """Home page view with featured jobs and search functionality."""
    # Get hero section for home page
    from .models import HeroSection
    hero_section = HeroSection.get_section('home')

    featured_jobs = JobListing.objects.filter(status='published', is_featured=True).order_by('-created_at')[:8]
    recent_jobs = JobListing.objects.filter(status='published').order_by('-created_at')[:10]
    categories = JobCategory.objects.all()

    # Count jobs by category
    category_counts = {}
    for category in categories:
        category_counts[category.id] = JobListing.objects.filter(category=category, status='published').count()

    # Get statistics for the hero section
    total_jobs = JobListing.objects.filter(status='published').count()
    total_companies = JobListing.objects.filter(status='published').values('company').distinct().count()
    total_categories = categories.count()

    # Get testimonials if available
    testimonials = []
    if 'Testimonial' in globals():
        testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')[:5]

    # Get team members if available
    team_members = []
    if 'TeamMember' in globals():
        team_members = TeamMember.objects.filter(is_active=True).order_by('order')

    # Get trusted companies if available
    trusted_companies = []
    if 'TrustedCompany' in globals():
        trusted_companies = TrustedCompany.objects.filter(is_active=True).order_by('order')

    # Search form
    search_form = JobSearchForm()

    context = {
        'featured_jobs': featured_jobs,
        'recent_jobs': recent_jobs,
        'categories': categories,
        'category_counts': category_counts,
        'search_form': search_form,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_categories': total_categories,
        'testimonials': testimonials,
        'team_members': team_members,
        'trusted_companies': trusted_companies,
        'hero_section': hero_section,
    }
    return render(request, 'jobs/home.html', context)

def job_list(request):
    """View for listing and searching jobs."""
    # Get hero section for jobs page
    from .models import HeroSection
    hero_section = HeroSection.get_section('jobs')

    jobs = JobListing.objects.filter(status='published').order_by('-created_at')
    categories = JobCategory.objects.all()

    # Process search form
    form = JobSearchForm(request.GET)
    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')
        job_types = form.cleaned_data.get('job_type')
        experience_levels = form.cleaned_data.get('experience_level')
        min_salary = form.cleaned_data.get('min_salary')
        max_salary = form.cleaned_data.get('max_salary')
        skills = form.cleaned_data.get('skills')
        is_remote = form.cleaned_data.get('is_remote')
        date_posted = form.cleaned_data.get('date_posted')
        has_salary = form.cleaned_data.get('has_salary')
        exclude_expired = form.cleaned_data.get('exclude_expired')

        # Apply filters
        if keyword:
            jobs = jobs.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(company__name__icontains=keyword) |
                Q(skills_required__icontains=keyword)
            )

        if location:
            jobs = jobs.filter(location__icontains=location)

        if category:
            jobs = jobs.filter(category=category)

        if job_types:
            jobs = jobs.filter(job_type__in=job_types)

        if experience_levels:
            jobs = jobs.filter(experience_level__in=experience_levels)

        if min_salary:
            jobs = jobs.filter(salary_min__gte=min_salary)

        if max_salary:
            jobs = jobs.filter(salary_max__lte=max_salary)

        if skills:
            skill_list = [skill.strip() for skill in skills.split(',')]
            for skill in skill_list:
                jobs = jobs.filter(skills_required__icontains=skill)

        if is_remote:
            jobs = jobs.filter(is_remote=True)

        # Filter by date posted
        if date_posted:
            days = int(date_posted)
            date_threshold = timezone.now() - timezone.timedelta(days=days)
            jobs = jobs.filter(created_at__gte=date_threshold)

        # Show only jobs with salary information
        if has_salary:
            jobs = jobs.filter(
                Q(salary_min__isnull=False) |
                Q(salary_max__isnull=False)
            )

        # Exclude expired jobs if requested
        if exclude_expired:
            jobs = jobs.filter(
                Q(application_deadline__isnull=True) |
                Q(application_deadline__gt=timezone.now())
            )

    # Apply sorting
    sort_option = request.GET.get('sort', 'newest')
    if sort_option == 'oldest':
        jobs = jobs.order_by('created_at')
    elif sort_option == 'salary_high':
        jobs = jobs.order_by('-salary_max', '-salary_min')
    elif sort_option == 'salary_low':
        jobs = jobs.order_by('salary_min', 'salary_max')
    else:  # newest first (default)
        jobs = jobs.order_by('-created_at')

    # Get saved jobs for the current user
    saved_jobs = []
    if request.user.is_authenticated and request.user.user_type == 'job_seeker':
        saved_job_ids = SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
        saved_jobs = JobListing.objects.filter(id__in=saved_job_ids)

    # Pagination
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'jobs': page_obj,
        'form': form,
        'categories': categories,
        'total_jobs': jobs.count(),
        'saved_jobs': saved_jobs,
        'hero_section': hero_section,
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, slug):
    """View for displaying job details and handling job applications."""
    job = get_object_or_404(JobListing, slug=slug, status='published')

    # Increment view count
    job.views_count += 1
    job.save()

    # Track analytics
    from jobs.models import JobAnalytics
    import datetime
    import json

    analytics, created = JobAnalytics.objects.get_or_create(job=job)

    # Update view statistics
    analytics.total_views += 1

    # Track unique views (based on session)
    session_key = f'viewed_job_{job.id}'
    first_view_time_key = f'first_viewed_job_{job.id}_time'

    if not request.session.get(session_key):
        request.session[session_key] = True
        request.session.modified = True
        analytics.unique_views += 1

        # Store the first view time for calculating time to apply later
        if not request.session.get(first_view_time_key):
            request.session[first_view_time_key] = timezone.now().isoformat()
            request.session.modified = True

    # Track referral source if available
    referrer = request.META.get('HTTP_REFERER', '')
    if referrer:
        referral_sources = analytics.referral_sources or {}
        domain = referrer.split('/')[2] if '/' in referrer else referrer
        referral_sources[domain] = referral_sources.get(domain, 0) + 1
        analytics.referral_sources = referral_sources

    # Track daily views
    today = timezone.now().date().isoformat()
    daily_views = analytics.daily_views or {}
    daily_views[today] = daily_views.get(today, 0) + 1
    analytics.daily_views = daily_views

    # Save analytics
    analytics.save()

    # Check if user has saved this job
    is_saved = False
    has_applied = False
    if request.user.is_authenticated:
        is_saved = SavedJob.objects.filter(job=job, user=request.user).exists()
        has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()

    # Similar jobs using the recommender system
    from jobs.recommender import get_similar_jobs
    similar_jobs = get_similar_jobs(job, limit=4)

    # Get job match score for pro users
    match_score = None
    if request.user.is_authenticated and request.user.user_type == 'job_seeker' and hasattr(request.user, 'has_active_pro') and request.user.has_active_pro():
        # Check if we have an existing match score
        try:
            from subscriptions.ai_models import JobMatchScore
            match_score, created = JobMatchScore.objects.get_or_create(
                user=request.user,
                job=job,
                defaults={
                    'skills_match': 0,
                    'experience_match': 0,
                    'education_match': 0,
                    'overall_match': 0
                }
            )

            # If this is a new match score, calculate it
            if created:
                # Get user skills and job required skills
                user_skills = request.user.skills or ""
                job_skills = job.skills_required or ""

                # Convert to lists
                user_skill_list = [skill.strip().lower() for skill in user_skills.split(',') if skill.strip()]
                job_skill_list = [skill.strip().lower() for skill in job_skills.split(',') if skill.strip()]

                # Calculate matching skills
                matching_skills = set(user_skill_list).intersection(set(job_skill_list))
                missing_skills = set(job_skill_list) - set(user_skill_list)

                # Calculate match percentages
                if job_skill_list:
                    skills_match = int((len(matching_skills) / len(job_skill_list)) * 100)
                else:
                    skills_match = 100

                # For demo purposes, generate random scores for other categories
                import random
                experience_match = random.randint(60, 95)
                education_match = random.randint(60, 95)

                # Calculate overall match
                overall_match = (skills_match + experience_match + education_match) // 3

                # Update match score
                match_score.skills_match = skills_match
                match_score.experience_match = experience_match
                match_score.education_match = education_match
                match_score.overall_match = overall_match
                match_score.matching_skills = list(matching_skills)
                match_score.missing_skills = list(missing_skills)
                match_score.save()
        except:
            # If there's an error, just continue without match score
            pass

    # Application form
    form = None
    if request.user.is_authenticated and request.user.user_type == 'job_seeker' and not has_applied:
        form = JobApplicationForm(user=request.user, job=job)

        if request.method == 'POST':
            # Check if user has already applied to this job
            if JobApplication.objects.filter(job=job, applicant=request.user).exists():
                messages.error(request, _('You have already applied to this job.'))
                return redirect('jobs:job_detail', slug=slug)

            form = JobApplicationForm(request.POST, request.FILES, user=request.user, job=job)
            if form.is_valid():
                try:
                    # Create the application
                    application = form.save(commit=False)
                    application.job = job
                    application.applicant = request.user
                    application.status = 'pending'

                    # Handle resume upload or use profile resume
                    if form.cleaned_data.get('use_profile_resume', False) and request.user.resume:
                        application.resume = request.user.resume
                    elif 'resume' in request.FILES:
                        application.resume = request.FILES['resume']
                    elif not application.resume and not request.user.resume:
                        messages.error(request, _('Please upload a resume.'))
                        return redirect('jobs:job_detail', slug=slug)

                    # Save the application
                    application.save()

                    # Create notification for employer
                    Notification.objects.create(
                        user=job.posted_by,
                        notification_type='application_received',
                        title=_('New Application Received'),
                        message=_(f'You have received a new application from {request.user.get_full_name()} for the job: {job.title}'),
                        related_job=job,
                        related_application=application
                    )

                    # Create notification for job seeker
                    Notification.objects.create(
                        user=request.user,
                        notification_type='application_status',
                        title=_('Application Submitted'),
                        message=_(f'Your application for {job.title} has been submitted successfully. The status is now: Pending Review.'),
                        related_job=job,
                        related_application=application
                    )

                    # Update job analytics
                    from jobs.models import JobAnalytics
                    import datetime

                    analytics, _ = JobAnalytics.objects.get_or_create(job=job)

                    # Update application count
                    analytics.total_applications += 1

                    # Calculate application rate
                    if analytics.total_views > 0:
                        analytics.application_rate = (analytics.total_applications / analytics.total_views) * 100

                    # Track time to apply
                    session_key = f'first_viewed_job_{job.id}_time'
                    first_view_time = request.session.get(session_key)

                    if first_view_time:
                        # Calculate time between first view and application
                        first_view_datetime = datetime.datetime.fromisoformat(first_view_time)
                        time_to_apply = timezone.now() - first_view_datetime

                        # Update time to first application if this is the first one
                        if analytics.total_applications == 1:
                            analytics.time_to_first_application = time_to_apply

                        # Update average time to apply
                        if analytics.avg_time_to_apply:
                            # Calculate new average
                            total_seconds = analytics.avg_time_to_apply.total_seconds() * (analytics.total_applications - 1)
                            total_seconds += time_to_apply.total_seconds()
                            analytics.avg_time_to_apply = datetime.timedelta(seconds=total_seconds / analytics.total_applications)
                        else:
                            analytics.avg_time_to_apply = time_to_apply

                    # Update location data
                    locations = analytics.applicant_locations or {}
                    location = request.user.location or 'Unknown'
                    locations[location] = locations.get(location, 0) + 1
                    analytics.applicant_locations = locations

                    # Track daily applications
                    today = timezone.now().date().isoformat()
                    daily_applications = analytics.daily_applications or {}
                    daily_applications[today] = daily_applications.get(today, 0) + 1
                    analytics.daily_applications = daily_applications

                    # Save analytics
                    analytics.save()

                    messages.success(request, _('Your application has been submitted successfully! You can track its status in your dashboard.'))
                    return redirect('jobs:job_seeker_dashboard')

                except Exception as e:
                    if 'UNIQUE constraint' in str(e):
                        messages.error(request, _('You have already applied to this job.'))
                    else:
                        messages.error(request, _('An error occurred while submitting your application. Please try again.'))
                        print(f"Application error: {str(e)}")  # Log the error for debugging
                    return redirect('jobs:job_detail', slug=slug)
            else:
                # Form is not valid, display errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

    # Get count of jobs from the same company
    company_job_count = JobListing.objects.filter(
        company=job.company,
        status='published'
    ).exclude(id=job.id).count()

    # Check if user has pro subscription
    has_pro = False
    if request.user.is_authenticated and request.user.user_type == 'job_seeker':
        has_pro = hasattr(request.user, 'has_active_pro') and request.user.has_active_pro()

    context = {
        'job': job,
        'similar_jobs': similar_jobs,
        'is_saved': is_saved,
        'has_applied': has_applied,
        'form': form,
        'match_score': match_score,
        'company_job_count': company_job_count,
        'has_pro': has_pro,
    }
    return render(request, 'jobs/job_detail.html', context)

def category_detail(request, slug):
    """View for displaying jobs by category."""
    category = get_object_or_404(JobCategory, slug=slug)
    jobs = JobListing.objects.filter(category=category, status='published').order_by('-created_at')

    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'jobs': page_obj,
        'total_jobs': jobs.count(),
    }
    return render(request, 'jobs/category_detail.html', context)

@login_required
def employer_dashboard(request):
    """Dashboard for employers to manage job listings."""
    if request.user.user_type != 'employer':
        messages.error(request, _('You do not have permission to access the employer dashboard.'))
        return redirect('jobs:home')

    # Get companies owned by the user
    from .models import Company
    companies = Company.objects.filter(owner=request.user)

    # Get jobs posted by the user's companies
    jobs = JobListing.objects.filter(company__in=companies).order_by('-created_at')
    applications = JobApplication.objects.filter(job__company__in=companies).order_by('-applied_at')

    # Statistics
    total_jobs = jobs.count()
    active_jobs = jobs.filter(status='published').count()
    total_applications = applications.count()
    new_applications = applications.filter(status='pending').count()

    # Add companies to context
    company_count = companies.count()

    # Get candidate recommendations if employer has pro subscription
    candidate_recommendations = {}
    if hasattr(request.user, 'has_active_pro') and request.user.has_active_pro():
        # Import the candidate recommender
        from .candidate_recommender import get_candidate_recommendations_for_employer
        candidate_recommendations = get_candidate_recommendations_for_employer(request.user)

    context = {
        'jobs': jobs,
        'applications': applications,
        'companies': companies,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'new_applications': new_applications,
        'company_count': company_count,
        'candidate_recommendations': candidate_recommendations,
        'has_pro': hasattr(request.user, 'has_active_pro') and request.user.has_active_pro(),
    }
    return render(request, 'jobs/employer_dashboard.html', context)

@login_required
def job_seeker_dashboard(request):
    """Dashboard for job seekers to manage applications and saved jobs."""
    if request.user.user_type != 'job_seeker':
        messages.error(request, _('You do not have permission to access the job seeker dashboard.'))
        return redirect('jobs:home')

    applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
    saved_jobs = SavedJob.objects.filter(user=request.user).order_by('-saved_at')

    # Statistics
    total_applications = applications.count()
    pending_applications = applications.filter(status='pending').count()
    shortlisted_applications = applications.filter(status='shortlisted').count()
    rejected_applications = applications.filter(status='rejected').count()

    # Get recommended jobs
    recommended_jobs = []
    try:
        # Try to use the existing recommender if it exists
        from jobs.recommender import get_recommended_jobs
        recommended_jobs = get_recommended_jobs(request.user, limit=6)
    except ImportError:
        # Fall back to our new recommender
        try:
            from jobs.job_recommender import get_recommended_jobs
            recommended_jobs = get_recommended_jobs(request.user, limit=6)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting recommended jobs: {str(e)}")

    # Filter out any recommendations with empty slugs
    if recommended_jobs:
        recommended_jobs = [job_match for job_match in recommended_jobs if job_match['job'] and job_match['job'].slug]

    # Calculate profile completion percentage
    profile_completion = 0
    if hasattr(request.user, 'get_profile_completion_percentage'):
        profile_completion = request.user.get_profile_completion_percentage()

    # Check if user has pro subscription
    has_pro = False
    if hasattr(request.user, 'has_active_pro'):
        has_pro = request.user.has_active_pro()

    context = {
        'applications': applications,
        'saved_jobs': saved_jobs,
        'recommended_jobs': recommended_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'shortlisted_applications': shortlisted_applications,
        'rejected_applications': rejected_applications,
        'now': timezone.now(),
        'has_pro': has_pro,
        'profile_completion': profile_completion,
    }
    return render(request, 'jobs/job_seeker_dashboard.html', context)

@login_required
def create_job(request):
    """View for employers to create new job listings."""
    if request.user.user_type != 'employer':
        messages.error(request, _('Only employers can create job listings.'))
        return redirect('jobs:home')

    if request.method == 'POST':
        form = JobListingForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save()
            messages.success(request, _('Job listing created successfully!'))
            return redirect('jobs:job_detail', slug=job.slug)
    else:
        form = JobListingForm(user=request.user)

    context = {
        'form': form,
        'title': _('Create Job Listing'),
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def edit_job(request, slug):
    """View for employers to edit their job listings."""
    job = get_object_or_404(JobListing, slug=slug)

    # Check if user is the owner of the job
    if job.posted_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden(_('You do not have permission to edit this job listing.'))

    if request.method == 'POST':
        form = JobListingForm(request.POST, instance=job, user=request.user)
        if form.is_valid():
            job = form.save()
            messages.success(request, _('Job listing updated successfully!'))
            return redirect('jobs:job_detail', slug=job.slug)
    else:
        form = JobListingForm(instance=job, user=request.user)

    context = {
        'form': form,
        'title': _('Edit Job Listing'),
        'job': job,
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
@require_POST
def toggle_save_job(request, job_id):
    """AJAX view for saving/unsaving jobs."""
    job = get_object_or_404(JobListing, id=job_id)

    if request.user.user_type != 'job_seeker':
        return JsonResponse({'error': _('Only job seekers can save jobs.')}, status=403)

    saved = SavedJob.objects.filter(job=job, user=request.user).exists()

    if saved:
        SavedJob.objects.filter(job=job, user=request.user).delete()
        return JsonResponse({'status': 'unsaved'})
    else:
        SavedJob.objects.create(job=job, user=request.user)
        return JsonResponse({'status': 'saved'})

@login_required
def update_application_status(request, application_id):
    """View for employers to update application status."""
    application = get_object_or_404(JobApplication, id=application_id)

    # Check if user is the employer for this job
    if application.job.posted_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden(_('You do not have permission to update this application.'))

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes')

        if new_status in dict(JobApplication.STATUS_CHOICES):
            old_status = application.status
            application.status = new_status

            if notes:
                application.employer_notes = notes

            application.save()

            # Create notification for job seeker
            Notification.objects.create(
                user=application.applicant,
                notification_type='application_status',
                title=_('Application Status Updated'),
                message=_(f'Your application for {application.job.title} has been updated from {old_status} to {new_status}.'),
                related_job=application.job,
                related_application=application
            )

            messages.success(request, _('Application status updated successfully!'))
        else:
            messages.error(request, _('Invalid status.'))

    return redirect(request.META.get('HTTP_REFERER', reverse('jobs:employer_dashboard')))

@login_required
def notifications(request):
    """View for displaying user notifications."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark all as read if requested
    if request.GET.get('mark_all_read'):
        notifications.update(is_read=True)
        messages.success(request, _('All notifications marked as read.'))
        return redirect('jobs:notifications')

    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'notifications': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'jobs/notifications_dashboard.html', context)

    return render(request, 'jobs/notifications.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """AJAX view for marking a notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

def about(request):
    """View for the about page."""
    return render(request, 'jobs/about.html')

def contact(request):
    """View for the contact page."""
    site_settings = SiteSettings.get_settings()
    return render(request, 'jobs/contact.html', {'site_settings': site_settings})

def testimonials(request):
    """View for displaying all testimonials."""
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')

    context = {
        'testimonials': testimonials,
    }
    return render(request, 'jobs/testimonials.html', context)

def terms(request):
    """View for the terms and conditions page."""
    try:
        terms_page = LegalPage.objects.get(page_type='terms', is_active=True)
        return render(request, 'jobs/legal_page.html', {'legal_page': terms_page})
    except LegalPage.DoesNotExist:
        # Fallback to static template if no database content
        return render(request, 'jobs/terms.html')

def privacy(request):
    """View for the privacy policy page."""
    try:
        privacy_page = LegalPage.objects.get(page_type='privacy', is_active=True)
        return render(request, 'jobs/legal_page.html', {'legal_page': privacy_page})
    except LegalPage.DoesNotExist:
        # Fallback to static template if no database content
        return render(request, 'jobs/privacy.html')

def cookies(request):
    """View for the cookie policy page."""
    try:
        cookies_page = LegalPage.objects.get(page_type='cookies', is_active=True)
        return render(request, 'jobs/legal_page.html', {'legal_page': cookies_page})
    except LegalPage.DoesNotExist:
        # Fallback to static template if no database content
        return render(request, 'jobs/cookies.html')

def legal_page(request, slug):
    """View for displaying any legal page by slug."""
    legal_page = get_object_or_404(LegalPage, slug=slug, is_active=True)
    return render(request, 'jobs/legal_page.html', {'legal_page': legal_page})

def faq(request):
    """View for the FAQ page."""
    return render(request, 'jobs/faq.html')









@csrf_exempt
@require_POST
def subscribe_newsletter(request):
    """AJAX view for newsletter subscription."""
    try:
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'success': False, 'error': 'Email is required.'})

        # Check if email already exists
        if Newsletter.objects.filter(email=email).exists():
            # If it exists but is inactive, reactivate it
            newsletter = Newsletter.objects.get(email=email)
            if not newsletter.is_active:
                newsletter.is_active = True
                newsletter.save()
                return JsonResponse({'success': True, 'message': 'Your subscription has been reactivated!'})
            return JsonResponse({'success': False, 'error': 'This email is already subscribed.'})

        # Create new subscription
        Newsletter.objects.create(email=email)

        return JsonResponse({'success': True, 'message': 'Thank you for subscribing!'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request format.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def unsubscribe_newsletter(request):
    """View for newsletter unsubscribe page."""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                newsletter = Newsletter.objects.get(email=email)
                # Generate a secure token
                import hashlib
                import time
                token = hashlib.sha256(f"{email}{time.time()}{settings.SECRET_KEY}".encode()).hexdigest()

                # Send confirmation email
                subject = _('Confirm Unsubscribe Request')
                unsubscribe_link = request.build_absolute_uri(
                    reverse('jobs:unsubscribe_confirm', kwargs={'email': email, 'token': token})
                )

                context = {
                    'email': email,
                    'unsubscribe_link': unsubscribe_link,
                }

                html_message = render_to_string('emails/unsubscribe_confirmation.html', context)
                plain_message = render_to_string('emails/unsubscribe_confirmation_plain.html', context)

                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                )

                messages.success(request, _('Please check your email to confirm unsubscribing.'))
                return redirect('jobs:home')
            except Newsletter.DoesNotExist:
                messages.error(request, _('This email is not subscribed to our newsletter.'))
        else:
            messages.error(request, _('Please provide your email address.'))

    return render(request, 'jobs/unsubscribe.html')

def unsubscribe_confirm(request, email, token):
    """View to confirm newsletter unsubscription."""
    try:
        newsletter = Newsletter.objects.get(email=email)
        newsletter.is_active = False
        newsletter.save()
        messages.success(request, _('You have been successfully unsubscribed from our newsletter.'))
    except Newsletter.DoesNotExist:
        messages.error(request, _('Invalid unsubscribe link.'))

    return redirect('jobs:home')

@login_required
def job_analytics(request, job_id):
    """View for employers to see analytics for a specific job."""
    job = get_object_or_404(JobListing, id=job_id)

    # Check if user is the owner of the job
    if job.posted_by != request.user and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to view analytics for this job.'))
        return redirect('jobs:employer_dashboard')

    # Get or create analytics for this job
    from jobs.models import JobAnalytics
    import json
    from datetime import datetime, timedelta

    analytics, _ = JobAnalytics.objects.get_or_create(job=job)

    # Update analytics with latest data
    analytics.update_application_stats()

    # Prepare performance trends data
    daily_views = analytics.daily_views or {}
    daily_applications = analytics.daily_applications or {}

    # Get all dates from job creation to today
    start_date = job.created_at.date()
    end_date = timezone.now().date()
    date_range = []
    views_data = []
    applications_data = []

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        date_range.append(current_date.strftime('%b %d'))
        views_data.append(daily_views.get(date_str, 0))
        applications_data.append(daily_applications.get(date_str, 0))
        current_date += timedelta(days=1)

    # Prepare chart data
    performance_data = {
        'dates': date_range,
        'views': views_data,
        'applications': applications_data
    }

    context = {
        'job': job,
        'analytics': analytics,
        'performance_data': json.dumps(performance_data)
    }

    return render(request, 'jobs/job_analytics.html', context)

@login_required
def applications_list(request, job_id):
    """View for employers to see all applications for a specific job."""
    job = get_object_or_404(JobListing, id=job_id)

    # Check if user is the employer for this job
    if job.posted_by != request.user and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to view applications for this job.'))
        return redirect('jobs:employer_dashboard')

    applications = JobApplication.objects.filter(job=job)

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(JobApplication.STATUS_CHOICES):
        applications = applications.filter(status=status_filter)

    # Sort applications
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        applications = applications.order_by('applied_at')
    else:  # newest first (default)
        applications = applications.order_by('-applied_at')

    # Get counts for different statuses
    pending_count = JobApplication.objects.filter(job=job, status='pending').count()
    shortlisted_count = JobApplication.objects.filter(job=job, status='shortlisted').count()
    interview_count = JobApplication.objects.filter(job=job, status='interview').count()

    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'job': job,
        'applications': page_obj,
        'pending_count': pending_count,
        'shortlisted_count': shortlisted_count,
        'interview_count': interview_count,
    }
    return render(request, 'jobs/applications_list.html', context)

@login_required
def application_detail(request, application_id):
    """View for displaying application details and allowing employers to update status."""
    application = get_object_or_404(JobApplication, id=application_id)

    # Check if user is the employer or the applicant
    if application.job.posted_by != request.user and application.applicant != request.user and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to view this application.'))
        return redirect('jobs:employer_dashboard')

    # Get messages for this application
    application_messages = ApplicationMessage.objects.filter(application=application).order_by('created_at')

    # Different templates for employer and applicant
    if application.job.posted_by == request.user or request.user.is_superuser:
        # Employer view
        context = {
            'application': application,
            'messages': application_messages,
        }
        return render(request, 'jobs/application_detail.html', context)
    else:
        # Job seeker view
        context = {
            'application': application,
            'messages': application_messages,
        }
        return render(request, 'jobs/jobseeker_application_detail.html', context)

@login_required
@require_POST
def update_job_status(request):
    """View for employers to update job status (publish, close, etc.)."""
    job_id = request.POST.get('job_id')
    new_status = request.POST.get('status')

    job = get_object_or_404(JobListing, id=job_id)

    # Check if user is the owner of the job
    if job.posted_by != request.user and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to update this job.'))
        return redirect('jobs:employer_dashboard')

    if new_status in dict(JobListing.STATUS_CHOICES):
        old_status = job.status
        job.status = new_status

        # If reopening an expired job, reset the deadline if it's in the past
        if new_status == 'published' and (old_status == 'expired' or old_status == 'closed'):
            if job.application_deadline and job.application_deadline < timezone.now():
                # Set deadline to 30 days from now
                job.application_deadline = timezone.now() + timezone.timedelta(days=30)

        job.save()

        status_display = dict(JobListing.STATUS_CHOICES)[new_status]
        messages.success(request, _(f'Job status updated to {status_display} successfully!'))
    else:
        messages.error(request, _('Invalid status.'))

    return redirect('jobs:employer_dashboard')

@login_required
@require_POST
def extend_deadline(request):
    """View for employers to extend job application deadline."""
    job_id = request.POST.get('job_id')
    new_deadline = request.POST.get('new_deadline')

    job = get_object_or_404(JobListing, id=job_id)

    # Check if user is the owner of the job
    if job.posted_by != request.user and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to update this job.'))
        return redirect('jobs:employer_dashboard')

    try:
        # Parse the new deadline
        new_deadline_dt = timezone.datetime.fromisoformat(new_deadline)

        # Ensure the new deadline is in the future
        if new_deadline_dt <= timezone.now():
            messages.error(request, _('The new deadline must be in the future.'))
            return redirect('jobs:employer_dashboard')

        # Update the job deadline
        job.application_deadline = new_deadline_dt

        # If job was expired, reactivate it
        if job.status == 'expired':
            job.status = 'published'

        job.save()

        messages.success(request, _('Job application deadline extended successfully!'))
    except ValueError:
        messages.error(request, _('Invalid date format.'))

    return redirect('jobs:employer_dashboard')

@login_required
@require_POST
def bulk_update_job_status(request):
    """View for employers to update status of multiple jobs at once."""
    job_filter = request.POST.get('job_filter')
    new_status = request.POST.get('new_status')

    # Validate the new status
    if new_status not in dict(JobListing.STATUS_CHOICES):
        messages.error(request, _('Invalid status.'))
        return redirect('jobs:employer_dashboard')

    # Get companies owned by the user
    from .models import Company
    companies = Company.objects.filter(owner=request.user)

    # Get jobs based on filter
    if job_filter == 'all':
        jobs = JobListing.objects.filter(company__in=companies)
    else:
        jobs = JobListing.objects.filter(company__in=companies, status=job_filter)

    # Update job statuses
    count = jobs.count()
    if count > 0:
        # If changing to published and jobs were expired, update deadlines
        if new_status == 'published':
            for job in jobs:
                if job.status == 'expired' or (job.application_deadline and job.application_deadline < timezone.now()):
                    # Set deadline to 30 days from now
                    job.application_deadline = timezone.now() + timezone.timedelta(days=30)
                    job.status = 'published'
                    job.save()
                else:
                    job.status = new_status
                    job.save()
        else:
            # Simple status update
            jobs.update(status=new_status)

        status_display = dict(JobListing.STATUS_CHOICES)[new_status]
        messages.success(request, _(f'{count} jobs updated to {status_display} successfully!'))
    else:
        messages.info(request, _('No jobs matched the selected filter.'))

    return redirect('jobs:employer_dashboard')

@login_required
@require_POST
def bulk_extend_deadline(request):
    """View for employers to extend deadlines of multiple jobs at once."""
    job_filter = request.POST.get('job_filter')
    days = request.POST.get('days', '30')

    try:
        days = int(days)
        if days <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, _('Invalid number of days.'))
        return redirect('jobs:employer_dashboard')

    # Get companies owned by the user
    from .models import Company
    companies = Company.objects.filter(owner=request.user)

    # Get jobs based on filter
    if job_filter == 'all':
        jobs = JobListing.objects.filter(company__in=companies)
    else:
        jobs = JobListing.objects.filter(company__in=companies, status=job_filter)

    # Update job deadlines
    count = 0
    for job in jobs:
        # If deadline is in the past or None, set it to X days from now
        if not job.application_deadline or job.application_deadline < timezone.now():
            job.application_deadline = timezone.now() + timezone.timedelta(days=days)
        else:
            # Otherwise, add X days to the current deadline
            job.application_deadline = job.application_deadline + timezone.timedelta(days=days)

        # If job was expired, reactivate it
        if job.status == 'expired':
            job.status = 'published'

        job.save()
        count += 1

    if count > 0:
        messages.success(request, _(f'Application deadline extended by {days} days for {count} jobs.'))
    else:
        messages.info(request, _('No jobs matched the selected filter.'))

    return redirect('jobs:employer_dashboard')

@login_required
def renew_job(request, job_id):
    """View for employers to renew a job listing with a paid package."""
    job = get_object_or_404(JobListing, id=job_id)

    # Check if user is the owner of the job
    if job.posted_by != request.user and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to renew this job.'))
        return redirect('jobs:employer_dashboard')

    # Get available packages
    packages = JobPackage.objects.filter(is_active=True).order_by('price')

    if request.method == 'POST':
        package_id = request.POST.get('package_id')

        try:
            package = JobPackage.objects.get(id=package_id, is_active=True)

            # Create a job renewal record
            from jobs.models import JobRenewal

            renewal = JobRenewal.objects.create(
                job=job,
                package=package,
                user=request.user,
                amount=package.price,
                status='pending',
                old_expiry_date=job.application_deadline
            )

            # Redirect to payment processing
            return redirect('jobs:process_payment', renewal_id=renewal.id)

        except JobPackage.DoesNotExist:
            messages.error(request, _('Invalid package selected.'))

    context = {
        'job': job,
        'packages': packages
    }

    return render(request, 'jobs/renew_job.html', context)

@login_required
def process_payment(request, renewal_id):
    """View for processing payment for job renewal."""
    renewal = get_object_or_404(JobRenewal, id=renewal_id)

    # Check if user is the owner of the renewal
    if renewal.user != request.user and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to access this payment.'))
        return redirect('jobs:employer_dashboard')

    # Check if renewal is still pending
    if renewal.status != 'pending':
        messages.error(request, _('This renewal has already been processed.'))
        return redirect('jobs:employer_dashboard')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # In a real implementation, this would integrate with a payment gateway
        # For this demo, we'll simulate a successful payment

        # Update the renewal record
        renewal.status = 'completed'
        renewal.payment_method = payment_method
        renewal.transaction_id = f"DEMO-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        # Calculate new expiry date
        if renewal.package:
            days = renewal.package.duration_days

            # If deadline is in the past or None, set it from today
            if not renewal.job.application_deadline or renewal.job.application_deadline < timezone.now():
                new_deadline = timezone.now() + timezone.timedelta(days=days)
            else:
                # Otherwise, add days to the current deadline
                new_deadline = renewal.job.application_deadline + timezone.timedelta(days=days)

            renewal.new_expiry_date = new_deadline
            renewal.save()

            # Update the job
            job = renewal.job
            job.application_deadline = new_deadline

            # Update job features based on package
            if renewal.package.featured_job:
                job.is_featured = True

            # Mark as renewed
            job.has_been_renewed = True

            # If job was expired, reactivate it
            if job.status == 'expired':
                job.status = 'published'

            job.save()

            # Create notification
            from jobs.models import Notification

            Notification.objects.create(
                user=request.user,
                notification_type='system',
                title=_('Job Renewed Successfully'),
                message=_(f'Your job "{job.title}" has been renewed successfully for {days} days.'),
                related_job=job
            )

            messages.success(request, _(f'Payment successful! Your job has been renewed for {days} days.'))
            return redirect('jobs:employer_dashboard')
        else:
            messages.error(request, _('Invalid package.'))

    context = {
        'renewal': renewal
    }

    return render(request, 'jobs/process_payment.html', context)

@login_required
@require_POST
def update_application_status(request, application_id):
    """View for employers to update application status with more details."""
    application = get_object_or_404(JobApplication, id=application_id)

    # Check if user is the employer for this job
    if application.job.posted_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden(_('You do not have permission to update this application.'))

    new_status = request.POST.get('status')
    employer_notes = request.POST.get('employer_notes')
    feedback_to_applicant = request.POST.get('feedback_to_applicant')

    # Interview details if status is 'interview'
    interview_date = request.POST.get('interview_date')
    interview_type = request.POST.get('interview_type')
    interview_location = request.POST.get('interview_location')

    if new_status in dict(JobApplication.STATUS_CHOICES):
        old_status = application.status
        application.status = new_status

        if employer_notes:
            application.employer_notes = employer_notes

        if feedback_to_applicant:
            application.feedback_to_applicant = feedback_to_applicant

        # Handle interview details
        if new_status == 'interview':
            if interview_date:
                application.interview_date = interview_date
            if interview_type:
                application.interview_type = interview_type
            if interview_location:
                application.interview_location = interview_location

        application.save()

        # Create notification for job seeker
        notification_message = _(f'Your application for {application.job.title} has been updated to {application.get_status_display()}.')
        if feedback_to_applicant:
            notification_message += _(' The employer has provided feedback.')

        Notification.objects.create(
            user=application.applicant,
            notification_type='application_status',
            title=_('Application Status Updated'),
            message=notification_message,
            related_job=application.job,
            related_application=application
        )

        messages.success(request, _('Application status updated successfully!'))
    else:
        messages.error(request, _('Invalid status.'))

    return redirect('jobs:application_detail', application_id=application.id)

@login_required
@require_POST
def send_application_message(request, application_id):
    """View for sending messages regarding a specific application."""
    application = get_object_or_404(JobApplication, id=application_id)

    # Check if user is the employer or the applicant
    if application.job.posted_by != request.user and application.applicant != request.user:
        messages.error(request, _('You do not have permission to send messages for this application.'))
        return redirect('jobs:job_seeker_dashboard')

    # Check if application is withdrawn
    if application.status == 'withdrawn':
        messages.error(request, _('You cannot send messages for a withdrawn application.'))
        if request.user == application.applicant:
            return redirect('jobs:job_seeker_dashboard')
        else:
            return redirect('jobs:applications_list', job_id=application.job.id)

    # Check if either user has blocked the other
    if request.user == application.job.posted_by:
        recipient = application.applicant
    else:
        recipient = application.job.posted_by

    is_blocked = BlockedUser.objects.filter(
        (Q(user=request.user, blocked_user=recipient) | Q(user=recipient, blocked_user=request.user))
    ).exists()

    if is_blocked:
        messages.error(request, _('You cannot send messages to this user.'))
        if request.user == application.applicant:
            return redirect('jobs:application_detail', application_id=application.id)
        else:
            return redirect('jobs:application_detail', application_id=application.id)

    content = request.POST.get('content')
    if content and content.strip():
        # Create the message
        message = ApplicationMessage.objects.create(
            application=application,
            sender=request.user,
            content=content.strip()
        )

        # Update application's last_message_at field
        application.last_message_at = timezone.now()
        application.save(update_fields=['last_message_at'])

        # Create notification for recipient
        Notification.objects.create(
            user=recipient,
            notification_type='message',
            title=_('New Message'),
            message=_(f'You have received a new message from {request.user.get_full_name()} regarding the job: {application.job.title}'),
            related_job=application.job,
            related_application=application
        )

        messages.success(request, _('Message sent successfully!'))
    else:
        messages.error(request, _('Message cannot be empty.'))

    # Redirect to the appropriate page based on user type
    if request.user == application.applicant:
        return redirect('jobs:application_detail', application_id=application.id)
    else:
        return redirect('jobs:application_detail', application_id=application.id)

@login_required
def withdraw_application(request, application_id):
    """View for job seekers to withdraw their application."""
    application = get_object_or_404(JobApplication, id=application_id)

    # Check if user is the applicant
    if application.applicant != request.user:
        messages.error(request, _('You do not have permission to withdraw this application.'))
        return redirect('jobs:job_seeker_dashboard')

    # Check if application is already withdrawn or hired
    if application.status == 'withdrawn':
        messages.info(request, _('This application has already been withdrawn.'))
        return redirect('jobs:job_seeker_dashboard')

    if application.status == 'hired':
        messages.error(request, _('You cannot withdraw an application after being hired.'))
        return redirect('jobs:job_seeker_dashboard')

    if request.method == 'POST':
        reason = request.POST.get('reason')

        # Update application status
        application.status = 'withdrawn'
        application.withdrawal_reason = reason if reason else _('No reason provided')
        application.updated_at = timezone.now()
        application.save()

        # Create notification for employer
        Notification.objects.create(
            user=application.job.posted_by,
            notification_type='application_status',
            title=_('Application Withdrawn'),
            message=_(f'{request.user.get_full_name()} has withdrawn their application for {application.job.title}.'),
            related_job=application.job,
            related_application=application
        )

        # Create notification for job seeker
        Notification.objects.create(
            user=request.user,
            notification_type='application_status',
            title=_('Application Withdrawn'),
            message=_(f'You have successfully withdrawn your application for {application.job.title}.'),
            related_job=application.job,
            related_application=application
        )

        messages.success(request, _('Your application has been withdrawn successfully.'))
        return redirect('jobs:job_seeker_dashboard')

    context = {
        'application': application,
    }
    return render(request, 'jobs/withdraw_application.html', context)


@login_required
@require_POST
def connect_with_company(request, company_id):
    """View for users to request a connection with a company."""
    company = get_object_or_404(Company, id=company_id)

    # Check if user is not the owner of the company
    if company.owner == request.user:
        messages.error(request, _('You cannot connect with your own company.'))
        return redirect('jobs:company_detail', slug=company.slug)

    # Check if a connection already exists
    connection_status = company.get_connection_status(request.user)

    if connection_status == 'approved':
        messages.info(request, _('You are already connected with this company.'))
        return redirect('jobs:company_detail', slug=company.slug)
    elif connection_status == 'pending':
        messages.info(request, _('Your connection request is pending approval.'))
        return redirect('jobs:company_detail', slug=company.slug)
    elif connection_status == 'rejected':
        messages.error(request, _('Your connection request has been rejected by this company.'))
        return redirect('jobs:company_detail', slug=company.slug)

    # Create a new connection request
    message = request.POST.get('message', '')

    connection = CompanyConnection.objects.create(
        user=request.user,
        company=company,
        status='pending',
        message=message
    )

    # Create notification for company owner
    Notification.objects.create(
        user=company.owner,
        notification_type='system',
        title=_('New Connection Request'),
        message=_(f'{request.user.get_full_name()} has requested to connect with your company {company.name}.'),
    )

    messages.success(request, _('Connection request sent successfully! Waiting for approval.'))
    return redirect('jobs:company_detail', slug=company.slug)


@login_required
@require_POST
def approve_connection(request, connection_id):
    """View for company owners to approve connection requests."""
    connection = get_object_or_404(CompanyConnection, id=connection_id)

    # Check if user is the owner of the company
    if connection.company.owner != request.user:
        return HttpResponseForbidden(_('You do not have permission to approve this connection.'))

    if connection.status != 'pending':
        messages.error(request, _('This connection request has already been processed.'))
    else:
        connection.status = 'approved'
        connection.save()

        # Create notification for the user
        Notification.objects.create(
            user=connection.user,
            notification_type='system',
            title=_('Connection Request Approved'),
            message=_(f'Your connection request with {connection.company.name} has been approved.'),
        )

        messages.success(request, _('Connection request approved successfully!'))

    return redirect('jobs:manage_connections')


@login_required
@require_POST
def reject_connection(request, connection_id):
    """View for company owners to reject connection requests."""
    connection = get_object_or_404(CompanyConnection, id=connection_id)

    # Check if user is the owner of the company
    if connection.company.owner != request.user:
        return HttpResponseForbidden(_('You do not have permission to reject this connection.'))

    if connection.status != 'pending':
        messages.error(request, _('This connection request has already been processed.'))
    else:
        connection.status = 'rejected'
        connection.save()

        # Create notification for the user
        Notification.objects.create(
            user=connection.user,
            notification_type='system',
            title=_('Connection Request Rejected'),
            message=_(f'Your connection request with {connection.company.name} has been rejected.'),
        )

        messages.success(request, _('Connection request rejected successfully!'))

    return redirect('jobs:manage_connections')


@login_required
@require_POST
def follow_company(request, company_id):
    """View for users to follow a company."""
    company = get_object_or_404(Company, id=company_id)

    # Check if user is already following the company
    if company.is_followed_by_user(request.user):
        # Unfollow
        CompanyFollower.objects.filter(user=request.user, company=company).delete()
        messages.success(request, _(f'You have unfollowed {company.name}.'))
    else:
        # Follow
        CompanyFollower.objects.create(user=request.user, company=company)
        messages.success(request, _(f'You are now following {company.name}. You will receive notifications about new job postings.'))

    # Check if the request came from the dashboard
    if request.GET.get('dashboard') == 'true':
        return redirect(reverse('jobs:my_followed_companies') + '?dashboard=true')

    # Check if the request came from the HTTP_REFERER
    referer = request.META.get('HTTP_REFERER', '')
    if 'my-followed-companies' in referer:
        return redirect('jobs:my_followed_companies')

    # Default redirect to company detail
    return redirect('jobs:company_detail', slug=company.slug)


@login_required
def manage_connections(request):
    """View for company owners to manage connection requests."""
    if request.user.user_type != 'employer':
        messages.error(request, _('Only employers can access this page.'))
        return redirect('jobs:home')

    # Get companies owned by the user
    companies = Company.objects.filter(owner=request.user)

    # Get all connection requests for these companies
    pending_connections = CompanyConnection.objects.filter(
        company__in=companies,
        status='pending'
    ).order_by('-created_at')

    approved_connections = CompanyConnection.objects.filter(
        company__in=companies,
        status='approved'
    ).order_by('-created_at')

    context = {
        'pending_connections': pending_connections,
        'approved_connections': approved_connections,
        'companies': companies,
    }

    return render(request, 'jobs/manage_connections.html', context)


@login_required
def manage_followers(request):
    """View for company owners to manage followers."""
    if request.user.user_type != 'employer':
        messages.error(request, _('Only employers can access this page.'))
        return redirect('jobs:home')

    # Get companies owned by the user
    companies = Company.objects.filter(owner=request.user)

    # Get all followers for these companies
    company_followers = {}
    for company in companies:
        followers = CompanyFollower.objects.filter(company=company).order_by('-created_at')
        company_followers[company] = followers

    context = {
        'company_followers': company_followers,
        'companies': companies,
    }

    return render(request, 'jobs/manage_followers.html', context)


@login_required
def my_connections(request):
    """View for job seekers to manage their company connections."""
    if request.user.user_type != 'job_seeker':
        messages.error(request, _('Only job seekers can access this page.'))
        return redirect('jobs:home')

    # Get all connections for the user
    pending_connections = CompanyConnection.objects.filter(
        user=request.user,
        status='pending'
    ).order_by('-created_at')

    approved_connections = CompanyConnection.objects.filter(
        user=request.user,
        status='approved'
    ).order_by('-created_at')

    rejected_connections = CompanyConnection.objects.filter(
        user=request.user,
        status='rejected'
    ).order_by('-created_at')

    context = {
        'pending_connections': pending_connections,
        'approved_connections': approved_connections,
        'rejected_connections': rejected_connections,
    }

    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'jobs/my_connections_dashboard.html', context)

    return render(request, 'jobs/my_connections.html', context)


@login_required
def my_followed_companies(request):
    """View for job seekers to manage companies they follow."""
    if request.user.user_type != 'job_seeker':
        messages.error(request, _('Only job seekers can access this page.'))
        return redirect('jobs:home')

    # Get all companies followed by the user
    followed_companies = CompanyFollower.objects.filter(
        user=request.user
    ).select_related('company').order_by('-created_at')

    context = {
        'followed_companies': followed_companies,
    }

    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'jobs/my_followed_companies_dashboard.html', context)

    return render(request, 'jobs/my_followed_companies.html', context)


@login_required
@require_POST
def remove_connection(request, connection_id):
    """View for users to remove their connections with companies."""
    connection = get_object_or_404(CompanyConnection, id=connection_id, user=request.user)
    company_name = connection.company.name
    connection.delete()

    messages.success(request, _(f'Connection with {company_name} has been removed.'))
    return redirect('jobs:my_connections')
