from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Avg, Sum, F, Q
from datetime import timedelta, date

from .models import UserSubscription
from .analytics_models import EmployerAnalytics, JobSeekerAnalytics, JobListingAnalytics
from jobs.models import JobListing, JobApplication, SavedJob, Company


@login_required
def employer_analytics_dashboard(request):
    """View for employer analytics dashboard."""
    # Check if user is an employer
    if request.user.user_type != 'employer':
        messages.error(request, _('This feature is only available for employers.'))
        return redirect('jobs:home')
    
    # Check if user has an active pro subscription with advanced analytics
    has_pro = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__advanced_analytics=True
    ).exists()
    
    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')
    
    # Get user's companies
    companies = Company.objects.filter(owner=request.user)
    
    if not companies:
        messages.warning(request, _('You need to create a company first.'))
        return redirect('jobs:create_company')
    
    # Get selected company or default to first company
    selected_company_id = request.GET.get('company')
    if selected_company_id:
        selected_company = get_object_or_404(Company, id=selected_company_id, owner=request.user)
    else:
        selected_company = companies.first()
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    date_range = request.GET.get('date_range', '30')
    if date_range == '7':
        start_date = end_date - timedelta(days=7)
    elif date_range == '90':
        start_date = end_date - timedelta(days=90)
    elif date_range == '180':
        start_date = end_date - timedelta(days=180)
    elif date_range == '365':
        start_date = end_date - timedelta(days=365)
    
    # Get job listings for the selected company
    job_listings = JobListing.objects.filter(company=selected_company)
    
    # Get applications for the job listings
    applications = JobApplication.objects.filter(job__company=selected_company)
    
    # Calculate metrics
    total_job_listings = job_listings.count()
    active_job_listings = job_listings.filter(status='published').count()
    expired_job_listings = job_listings.filter(status='expired').count()
    
    total_applications = applications.count()
    new_applications = applications.filter(status='pending').count()
    reviewed_applications = applications.filter(status='reviewed').count()
    shortlisted_applications = applications.filter(status='shortlisted').count()
    rejected_applications = applications.filter(status='rejected').count()
    
    # Calculate application status distribution
    application_status_data = {
        'pending': new_applications,
        'reviewed': reviewed_applications,
        'shortlisted': shortlisted_applications,
        'rejected': rejected_applications
    }
    
    # Calculate job listing status distribution
    job_status_data = {
        'published': active_job_listings,
        'expired': expired_job_listings,
        'draft': job_listings.filter(status='draft').count()
    }
    
    # Get top performing job listings
    top_jobs = job_listings.annotate(
        application_count=Count('applications')
    ).order_by('-application_count')[:5]
    
    # Get application trend data
    application_trend = applications.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('created_at__date').annotate(
        count=Count('id')
    ).order_by('created_at__date')
    
    application_trend_data = {
        'labels': [str(item['created_at__date']) for item in application_trend],
        'data': [item['count'] for item in application_trend]
    }
    
    context = {
        'companies': companies,
        'selected_company': selected_company,
        'date_range': date_range,
        'total_job_listings': total_job_listings,
        'active_job_listings': active_job_listings,
        'expired_job_listings': expired_job_listings,
        'total_applications': total_applications,
        'new_applications': new_applications,
        'reviewed_applications': reviewed_applications,
        'shortlisted_applications': shortlisted_applications,
        'rejected_applications': rejected_applications,
        'application_status_data': application_status_data,
        'job_status_data': job_status_data,
        'top_jobs': top_jobs,
        'application_trend_data': application_trend_data
    }
    
    return render(request, 'subscriptions/employer_analytics.html', context)


@login_required
def job_listing_analytics(request, job_id):
    """View for job listing analytics."""
    # Check if user is an employer
    if request.user.user_type != 'employer':
        messages.error(request, _('This feature is only available for employers.'))
        return redirect('jobs:home')
    
    # Check if user has an active pro subscription with advanced analytics
    has_pro = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__advanced_analytics=True
    ).exists()
    
    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')
    
    # Get the job listing
    job = get_object_or_404(JobListing, id=job_id)
    
    # Check if user owns the company that posted the job
    if job.company.owner != request.user:
        messages.error(request, _('You do not have permission to view analytics for this job.'))
        return redirect('jobs:employer_dashboard')
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    date_range = request.GET.get('date_range', '30')
    if date_range == '7':
        start_date = end_date - timedelta(days=7)
    elif date_range == '90':
        start_date = end_date - timedelta(days=90)
    
    # Get applications for the job
    applications = JobApplication.objects.filter(job=job)
    
    # Calculate metrics
    total_applications = applications.count()
    new_applications = applications.filter(status='pending').count()
    reviewed_applications = applications.filter(status='reviewed').count()
    shortlisted_applications = applications.filter(status='shortlisted').count()
    rejected_applications = applications.filter(status='rejected').count()
    
    # Calculate application status distribution
    application_status_data = {
        'pending': new_applications,
        'reviewed': reviewed_applications,
        'shortlisted': shortlisted_applications,
        'rejected': rejected_applications
    }
    
    # Get application trend data
    application_trend = applications.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('created_at__date').annotate(
        count=Count('id')
    ).order_by('created_at__date')
    
    application_trend_data = {
        'labels': [str(item['created_at__date']) for item in application_trend],
        'data': [item['count'] for item in application_trend]
    }
    
    # Get top applicant locations
    top_locations = applications.values(
        'applicant__location'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Get top applicant skills
    top_skills = []
    for app in applications:
        if hasattr(app.applicant, 'skills') and app.applicant.skills:
            skills = [s.strip() for s in app.applicant.skills.split(',')]
            for skill in skills:
                if skill:
                    found = False
                    for i, s in enumerate(top_skills):
                        if s['skill'] == skill:
                            top_skills[i]['count'] += 1
                            found = True
                            break
                    if not found:
                        top_skills.append({'skill': skill, 'count': 1})
    
    top_skills = sorted(top_skills, key=lambda x: x['count'], reverse=True)[:10]
    
    context = {
        'job': job,
        'date_range': date_range,
        'total_applications': total_applications,
        'new_applications': new_applications,
        'reviewed_applications': reviewed_applications,
        'shortlisted_applications': shortlisted_applications,
        'rejected_applications': rejected_applications,
        'application_status_data': application_status_data,
        'application_trend_data': application_trend_data,
        'top_locations': top_locations,
        'top_skills': top_skills
    }
    
    return render(request, 'subscriptions/job_listing_analytics.html', context)


@login_required
def job_seeker_analytics_dashboard(request):
    """View for job seeker analytics dashboard."""
    # Check if user is a job seeker
    if request.user.user_type != 'job_seeker':
        messages.error(request, _('This feature is only available for job seekers.'))
        return redirect('jobs:home')
    
    # Check if user has an active pro subscription
    has_pro = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).exists()
    
    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    date_range = request.GET.get('date_range', '30')
    if date_range == '7':
        start_date = end_date - timedelta(days=7)
    elif date_range == '90':
        start_date = end_date - timedelta(days=90)
    
    # Get applications for the user
    applications = JobApplication.objects.filter(applicant=request.user)
    
    # Calculate metrics
    total_applications = applications.count()
    new_applications = applications.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).count()
    viewed_applications = applications.filter(status__in=['reviewed', 'shortlisted', 'rejected']).count()
    shortlisted_applications = applications.filter(status='shortlisted').count()
    rejected_applications = applications.filter(status='rejected').count()
    
    # Calculate application status distribution
    application_status_data = {
        'pending': applications.filter(status='pending').count(),
        'reviewed': applications.filter(status='reviewed').count(),
        'shortlisted': shortlisted_applications,
        'rejected': rejected_applications
    }
    
    # Get application trend data
    application_trend = applications.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('created_at__date').annotate(
        count=Count('id')
    ).order_by('created_at__date')
    
    application_trend_data = {
        'labels': [str(item['created_at__date']) for item in application_trend],
        'data': [item['count'] for item in application_trend]
    }
    
    # Get job match scores
    from .ai_models import JobMatchScore
    job_matches = JobMatchScore.objects.filter(user=request.user)
    
    average_match = job_matches.aggregate(avg=Avg('overall_match'))['avg'] or 0
    high_match_jobs = job_matches.filter(overall_match__gte=80).count()
    
    # Get match score distribution
    match_distribution = {
        'high': job_matches.filter(overall_match__gte=80).count(),
        'medium': job_matches.filter(overall_match__gte=50, overall_match__lt=80).count(),
        'low': job_matches.filter(overall_match__lt=50).count()
    }
    
    # Get top job categories applied to
    top_categories = applications.values(
        'job__category'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Get saved jobs
    saved_jobs = SavedJob.objects.filter(user=request.user).count()
    
    context = {
        'date_range': date_range,
        'total_applications': total_applications,
        'new_applications': new_applications,
        'viewed_applications': viewed_applications,
        'shortlisted_applications': shortlisted_applications,
        'rejected_applications': rejected_applications,
        'application_status_data': application_status_data,
        'application_trend_data': application_trend_data,
        'average_match': average_match,
        'high_match_jobs': high_match_jobs,
        'match_distribution': match_distribution,
        'top_categories': top_categories,
        'saved_jobs': saved_jobs
    }
    
    return render(request, 'subscriptions/job_seeker_analytics.html', context)
