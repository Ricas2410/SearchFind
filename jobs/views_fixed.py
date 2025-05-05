from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json

from .models import (
    JobListing, JobCategory, JobApplication, SavedJob, Notification,
    JobPackage, JobRenewal, Newsletter, ApplicationMessage
)
from .forms import JobSearchForm, JobListingForm, JobApplicationForm

def home(request):
    """Home page view with featured jobs and search functionality."""
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
    }
    return render(request, 'jobs/home.html', context)

# ... [rest of the file remains the same] ...

def about(request):
    """View for the about page."""
    return render(request, 'jobs/about.html')

def contact(request):
    """View for the contact page."""
    return render(request, 'jobs/contact.html')

def testimonials(request):
    """View for displaying all testimonials."""
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')

    context = {
        'testimonials': testimonials,
    }
    return render(request, 'jobs/testimonials.html', context)

def terms(request):
    """View for the terms and conditions page."""
    return render(request, 'jobs/terms.html')

def privacy(request):
    """View for the privacy policy page."""
    return render(request, 'jobs/privacy.html')

def cookies(request):
    """View for the cookie policy page."""
    return render(request, 'jobs/cookies.html')

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

# ... [rest of the file remains the same] ...
