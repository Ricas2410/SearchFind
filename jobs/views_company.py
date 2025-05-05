from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse

from .models import Company, JobListing
from .forms import CompanyForm

def company_list(request):
    """View for listing all approved companies."""
    companies = Company.objects.filter(status='approved').order_by('-is_featured', '-created_at')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(industry__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(headquarters__icontains=search_query)
        )

    # Filter by industry
    industry = request.GET.get('industry', '')
    if industry:
        companies = companies.filter(industry=industry)

    # Filter by company size
    company_size = request.GET.get('size', '')
    if company_size:
        companies = companies.filter(company_size=company_size)

    # Get all available industries for filter dropdown
    industries = Company.objects.filter(status='approved').values_list('industry', flat=True).distinct()

    # Pagination
    paginator = Paginator(companies, 12)  # Show 12 companies per page
    page_number = request.GET.get('page', 1)
    companies_page = paginator.get_page(page_number)

    context = {
        'companies': companies_page,
        'search_query': search_query,
        'industry_filter': industry,
        'size_filter': company_size,
        'industries': industries,
        'company_sizes': Company.COMPANY_SIZE_CHOICES,
    }

    return render(request, 'jobs/company_list.html', context)

def company_detail(request, slug):
    """View for company details and job listings."""
    company = get_object_or_404(Company, slug=slug, status='approved')

    # Get company's active job listings
    from django.utils import timezone
    from django.db.models import Q
    jobs = JobListing.objects.filter(
        company=company,
        status='published'
    ).filter(
        # Filter for non-expired jobs (application_deadline is in the future or null)
        Q(application_deadline__gt=timezone.now()) | Q(application_deadline__isnull=True)
    ).order_by('-is_featured', '-created_at')

    # Pagination for jobs
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page', 1)
    jobs_page = paginator.get_page(page_number)

    # Get connection and follower status for authenticated users
    connection_status = None
    is_following = False
    if request.user.is_authenticated:
        connection_status = company.get_connection_status(request.user)
        is_following = company.is_followed_by_user(request.user)

    # Get similar companies in the same industry
    similar_companies = Company.objects.filter(
        industry=company.industry,
        status='approved'
    ).exclude(
        id=company.id
    ).order_by('-is_featured')[:4]

    context = {
        'company': company,
        'jobs': jobs_page,
        'job_count': jobs.count(),
        'connection_status': connection_status,
        'is_following': is_following,
        'follower_count': company.follower_count,
        'connection_count': company.connection_count,
        'similar_companies': similar_companies,
    }

    return render(request, 'jobs/company_detail.html', context)

@login_required
def create_company(request):
    """View for creating a new company."""
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()

            messages.success(request, _('Your company has been submitted for approval. You will be notified once it is approved.'))
            return redirect('jobs:employer_dashboard')
    else:
        form = CompanyForm()

    context = {
        'form': form,
        'title': _('Register Your Company'),
    }

    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'jobs/company_form_dashboard.html', context)

    return render(request, 'jobs/company_form.html', context)

@login_required
def edit_company(request, slug):
    """View for editing an existing company."""
    company = get_object_or_404(Company, slug=slug, owner=request.user)

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            # If company was previously approved and significant fields changed, set back to pending
            if company.status == 'approved' and significant_changes(company, form.cleaned_data):
                company = form.save(commit=False)
                company.status = 'pending'
                company.save()
                messages.warning(request, _('Your company information has been updated but requires re-approval due to significant changes.'))
            else:
                form.save()
                messages.success(request, _('Your company information has been updated successfully.'))

            return redirect('jobs:company_detail', slug=company.slug)
    else:
        form = CompanyForm(instance=company)

    context = {
        'form': form,
        'company': company,
        'title': _('Edit Company'),
    }

    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'jobs/company_form_dashboard.html', context)

    return render(request, 'jobs/company_form.html', context)

def significant_changes(company, cleaned_data):
    """Check if significant company details have changed that would require re-approval."""
    significant_fields = ['name', 'industry', 'company_size', 'headquarters']

    for field in significant_fields:
        if getattr(company, field) != cleaned_data.get(field):
            return True

    return False

@login_required
def my_companies(request):
    """View for listing companies owned by the current user."""
    companies = Company.objects.filter(owner=request.user).order_by('-created_at')

    context = {
        'companies': companies,
    }

    # Check if the request is coming from the dashboard
    if request.GET.get('dashboard') == 'true':
        return render(request, 'jobs/my_companies_dashboard.html', context)

    return render(request, 'jobs/my_companies.html', context)
