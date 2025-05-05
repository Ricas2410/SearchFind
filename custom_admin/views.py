from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, datetime

from accounts.models import CustomUser
from jobs.models import (
    JobListing, JobApplication, JobCategory, Company,
    TrustedCompany, TeamMember, Testimonial, Newsletter, SiteSettings,
    SavedJob, Notification, JobPackage, JobRenewal, JobAnalytics,
    LegalPage, CompanyConnection, CompanyFollower, HeroSection
)
from subscriptions.models import SubscriptionPlan, UserSubscription, PaystackConfig
from subscriptions.ai_models import ResumeAnalysis, JobMatchScore, CompanyMatchScore, ResumeBuilder
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from .models import AdminDashboardStat

def is_admin(user):
    """Check if user is an admin."""
    return user.is_authenticated and (user.user_type == 'admin' or user.is_superuser)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard view."""
    # Get counts for dashboard stats
    total_users = CustomUser.objects.count()
    total_jobs = JobListing.objects.count()
    total_applications = JobApplication.objects.count()
    total_companies = Company.objects.count()

    # Get recent items
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_jobs = JobListing.objects.order_by('-created_at')[:5]
    recent_applications = JobApplication.objects.order_by('-applied_at')[:5]

    # Get user type distribution
    user_types = CustomUser.objects.values('user_type').annotate(count=Count('id'))

    # Get job status distribution
    job_statuses = JobListing.objects.values('status').annotate(count=Count('id'))

    # Get application status distribution
    application_statuses = JobApplication.objects.values('status').annotate(count=Count('id'))

    # Get custom dashboard stats
    dashboard_stats = AdminDashboardStat.objects.filter(is_active=True)

    context = {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_companies': total_companies,
        'recent_users': recent_users,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'user_types': user_types,
        'job_statuses': job_statuses,
        'application_statuses': application_statuses,
        'dashboard_stats': dashboard_stats,
    }

    return render(request, 'custom_admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_management(request):
    """View for managing users."""
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        try:
            user = CustomUser.objects.get(id=user_id)

            if action == 'activate':
                user.is_active = True
                user.save()
                messages.success(request, f"User {user.email} has been activated successfully.")

            elif action == 'deactivate':
                user.is_active = False
                user.save()
                messages.success(request, f"User {user.email} has been deactivated successfully.")

            elif action == 'delete':
                email = user.email
                user.delete()
                messages.success(request, f"User {email} has been deleted successfully.")

            elif action == 'make_admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()
                messages.success(request, f"User {user.email} has been made an admin successfully.")

            elif action == 'remove_admin':
                user.is_staff = False
                user.is_superuser = False
                user.save()
                messages.success(request, f"Admin privileges have been removed from {user.email} successfully.")

            elif action == 'make_employer':
                user.user_type = 'employer'
                user.save()
                messages.success(request, f"User {user.email} has been made an employer successfully.")

            elif action == 'make_jobseeker':
                user.user_type = 'jobseeker'
                user.save()
                messages.success(request, f"User {user.email} has been made a job seeker successfully.")

        except CustomUser.DoesNotExist:
            messages.error(request, "The user you are trying to manage does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:user_management')

    # GET request
    users = CustomUser.objects.all().order_by('-date_joined')

    # Filter by user type if provided
    user_type = request.GET.get('user_type')
    if user_type:
        users = users.filter(user_type=user_type)

    # Filter by status if provided
    is_active = request.GET.get('is_active')
    if is_active is not None:
        is_active = is_active == 'true'
        users = users.filter(is_active=is_active)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            email__icontains=search_query
        ) | users.filter(
            first_name__icontains=search_query
        ) | users.filter(
            last_name__icontains=search_query
        )

    context = {
        'users': users,
        'user_type': user_type,
        'is_active': is_active,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/user_management.html', context)

@login_required
@user_passes_test(is_admin)
def job_management(request):
    """View for managing job listings."""
    if request.method == 'POST':
        action = request.POST.get('action')
        job_id = request.POST.get('job_id')

        try:
            job = JobListing.objects.get(id=job_id)

            if action == 'approve':
                job.status = 'active'
                job.save()
                messages.success(request, f"Job '{job.title}' has been approved and is now active.")

            elif action == 'reject':
                rejection_reason = request.POST.get('rejection_reason')
                job.status = 'rejected'
                job.rejection_reason = rejection_reason
                job.save()
                messages.success(request, f"Job '{job.title}' has been rejected.")

            elif action == 'deactivate':
                job.status = 'inactive'
                job.save()
                messages.success(request, f"Job '{job.title}' has been deactivated.")

            elif action == 'delete':
                title = job.title
                job.delete()
                messages.success(request, f"Job '{title}' has been deleted.")

            elif action == 'feature':
                job.is_featured = True
                job.save()
                messages.success(request, f"Job '{job.title}' has been featured.")

            elif action == 'unfeature':
                job.is_featured = False
                job.save()
                messages.success(request, f"Job '{job.title}' has been unfeatured.")

        except JobListing.DoesNotExist:
            messages.error(request, "The job you are trying to manage does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:job_management')

    # GET request
    jobs = JobListing.objects.all().order_by('-created_at')

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        jobs = jobs.filter(status=status)

    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        jobs = jobs.filter(category_id=category_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        jobs = jobs.filter(
            title__icontains=search_query
        ) | jobs.filter(
            company__name__icontains=search_query
        )

    # Get all categories for filter dropdown
    categories = JobCategory.objects.all()

    context = {
        'jobs': jobs,
        'status': status,
        'category_id': category_id,
        'search_query': search_query,
        'categories': categories,
    }

    return render(request, 'custom_admin/job_management.html', context)

@login_required
@user_passes_test(is_admin)
def company_management(request):
    """View for managing companies."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'edit':
            company_id = request.POST.get('company_id')

            try:
                company = Company.objects.get(id=company_id)

                # Update basic company details
                company.name = request.POST.get('name')
                company.location = request.POST.get('location')
                company.website = request.POST.get('website')
                company.industry = request.POST.get('industry')
                company.company_size = request.POST.get('company_size')
                company.description = request.POST.get('description')
                company.verification_status = request.POST.get('verification_status')
                company.is_featured = request.POST.get('is_featured') == 'on'

                # Handle logo upload
                if 'logo' in request.FILES:
                    company.logo = request.FILES['logo']

                company.save()

                # Create notification for the company owner
                if company.verification_status == 'verified' and company.verification_status != request.POST.get('verification_status'):
                    Notification.objects.create(
                        user=company.owner,
                        notification_type='company',
                        title='Company Verified',
                        message=f'Your company {company.name} has been verified by the admin.',
                        related_id=company.id
                    )
                elif company.verification_status == 'rejected' and company.verification_status != request.POST.get('verification_status'):
                    Notification.objects.create(
                        user=company.owner,
                        notification_type='company',
                        title='Company Verification Rejected',
                        message=f'Your company {company.name} verification has been rejected. Please contact support for more information.',
                        related_id=company.id
                    )

                messages.success(request, f"Company '{company.name}' has been updated successfully.")

            except Company.DoesNotExist:
                messages.error(request, "The company you are trying to edit does not exist.")

        elif action == 'delete':
            company_id = request.POST.get('company_id')

            try:
                company = Company.objects.get(id=company_id)
                name = company.name

                # Check if there are active job listings
                if company.joblisting_set.count() > 0:
                    messages.warning(request, f"Cannot delete company '{name}' because it has active job listings. Please delete the job listings first.")
                else:
                    company.delete()
                    messages.success(request, f"Company '{name}' has been deleted successfully.")

            except Company.DoesNotExist:
                messages.error(request, "The company you are trying to delete does not exist.")

        return redirect('custom_admin:company_management')

    # GET request
    companies = Company.objects.all().order_by('-created_at')

    # Filter by verification status if provided
    verification_status = request.GET.get('verification_status')
    if verification_status:
        companies = companies.filter(verification_status=verification_status)

    # Filter by featured status if provided
    is_featured = request.GET.get('is_featured')
    if is_featured is not None:
        is_featured = is_featured == 'true'
        companies = companies.filter(is_featured=is_featured)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        companies = companies.filter(
            name__icontains=search_query
        ) | companies.filter(
            industry__icontains=search_query
        ) | companies.filter(
            location__icontains=search_query
        ) | companies.filter(
            owner__email__icontains=search_query
        )

    context = {
        'companies': companies,
        'verification_status': verification_status,
        'is_featured': is_featured,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/company_management.html', context)

@login_required
@user_passes_test(is_admin)
def testimonial_management(request):
    """View for managing testimonials."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')
            position = request.POST.get('position')
            company = request.POST.get('company')
            rating = request.POST.get('rating')
            testimonial_text = request.POST.get('testimonial')
            photo = request.FILES.get('photo')

            try:
                # Create the testimonial
                testimonial = Testimonial.objects.create(
                    name=name,
                    position=position,
                    company=company,
                    rating=rating,
                    testimonial=testimonial_text
                )

                if photo:
                    testimonial.photo = photo
                    testimonial.save()

                messages.success(request, f"Testimonial from '{name}' has been added successfully.")

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'edit':
            testimonial_id = request.POST.get('testimonial_id')

            try:
                testimonial = Testimonial.objects.get(id=testimonial_id)

                # Update testimonial details
                testimonial.name = request.POST.get('name')
                testimonial.position = request.POST.get('position')
                testimonial.company = request.POST.get('company')
                testimonial.rating = request.POST.get('rating')
                testimonial.testimonial = request.POST.get('testimonial')

                # Handle photo
                if 'remove_photo' in request.POST and testimonial.photo:
                    testimonial.photo.delete()
                    testimonial.photo = None

                if 'photo' in request.FILES:
                    if testimonial.photo:
                        testimonial.photo.delete()
                    testimonial.photo = request.FILES['photo']

                testimonial.save()

                messages.success(request, f"Testimonial from '{testimonial.name}' has been updated successfully.")

            except Testimonial.DoesNotExist:
                messages.error(request, "The testimonial you are trying to edit does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'delete':
            testimonial_id = request.POST.get('testimonial_id')

            try:
                testimonial = Testimonial.objects.get(id=testimonial_id)
                name = testimonial.name

                # Delete the photo file if it exists
                if testimonial.photo:
                    testimonial.photo.delete()

                # Delete the testimonial
                testimonial.delete()

                messages.success(request, f"Testimonial from '{name}' has been deleted successfully.")

            except Testimonial.DoesNotExist:
                messages.error(request, "The testimonial you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:testimonial_management')

    # GET request
    testimonials = Testimonial.objects.all().order_by('-created_at')

    # Filter by active status if provided
    is_active = request.GET.get('is_active')
    if is_active is not None:
        is_active = is_active == 'true'
        testimonials = testimonials.filter(is_active=is_active)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        from django.db.models import Q
        testimonials = testimonials.filter(
            Q(name__icontains=search_query) |
            Q(position__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(testimonial__icontains=search_query)
        )

    context = {
        'testimonials': testimonials,
        'is_active': is_active,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/testimonial_management.html', context)

@login_required
@user_passes_test(is_admin)
def trusted_company_management(request):
    """View for managing trusted companies."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')
            website = request.POST.get('website')
            order = request.POST.get('order')
            logo = request.FILES.get('logo')

            try:
                # Create the trusted company
                trusted_company = TrustedCompany.objects.create(
                    name=name,
                    website=website,
                    order=order
                )

                if logo:
                    trusted_company.logo = logo
                    trusted_company.save()

                messages.success(request, f"Trusted company '{name}' has been added successfully.")

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'edit':
            trusted_company_id = request.POST.get('trusted_company_id')

            try:
                trusted_company = TrustedCompany.objects.get(id=trusted_company_id)

                # Update trusted company details
                trusted_company.name = request.POST.get('name')
                trusted_company.website = request.POST.get('website')
                trusted_company.order = request.POST.get('order')

                # Handle logo
                if 'remove_logo' in request.POST and trusted_company.logo:
                    trusted_company.logo.delete()
                    trusted_company.logo = None

                if 'logo' in request.FILES:
                    if trusted_company.logo:
                        trusted_company.logo.delete()
                    trusted_company.logo = request.FILES['logo']

                trusted_company.save()

                messages.success(request, f"Trusted company '{trusted_company.name}' has been updated successfully.")

            except TrustedCompany.DoesNotExist:
                messages.error(request, "The trusted company you are trying to edit does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'delete':
            trusted_company_id = request.POST.get('trusted_company_id')

            try:
                trusted_company = TrustedCompany.objects.get(id=trusted_company_id)
                name = trusted_company.name

                # Delete the logo file if it exists
                if trusted_company.logo:
                    trusted_company.logo.delete()

                # Delete the trusted company
                trusted_company.delete()

                messages.success(request, f"Trusted company '{name}' has been deleted successfully.")

            except TrustedCompany.DoesNotExist:
                messages.error(request, "The trusted company you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:trusted_company_management')

    # GET request
    trusted_companies = TrustedCompany.objects.all().order_by('order')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        trusted_companies = trusted_companies.filter(name__icontains=search_query)

    # Get the next order number for new trusted companies
    next_order = 1
    if trusted_companies.exists():
        next_order = trusted_companies.aggregate(max_order=models.Max('order'))['max_order'] + 1

    context = {
        'trusted_companies': trusted_companies,
        'search_query': search_query,
        'next_order': next_order,
    }

    return render(request, 'custom_admin/trusted_company_management.html', context)

@login_required
@user_passes_test(is_admin)
def team_member_management(request):
    """View for managing team members."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')
            position = request.POST.get('position')
            email = request.POST.get('email')
            bio = request.POST.get('bio')
            linkedin = request.POST.get('linkedin')
            twitter = request.POST.get('twitter')
            facebook = request.POST.get('facebook')
            instagram = request.POST.get('instagram')
            order = request.POST.get('order')
            photo = request.FILES.get('photo')

            try:
                # Create the team member
                member = TeamMember.objects.create(
                    name=name,
                    position=position,
                    email=email,
                    bio=bio,
                    linkedin=linkedin,
                    twitter=twitter,
                    facebook=facebook,
                    instagram=instagram,
                    order=order
                )

                if photo:
                    member.photo = photo
                    member.save()

                messages.success(request, f"Team member '{name}' has been added successfully.")

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'edit':
            member_id = request.POST.get('member_id')

            try:
                member = TeamMember.objects.get(id=member_id)

                # Update member details
                member.name = request.POST.get('name')
                member.position = request.POST.get('position')
                member.email = request.POST.get('email')
                member.bio = request.POST.get('bio')
                member.linkedin = request.POST.get('linkedin')
                member.twitter = request.POST.get('twitter')
                member.facebook = request.POST.get('facebook')
                member.instagram = request.POST.get('instagram')
                member.order = request.POST.get('order')

                # Handle photo
                if 'remove_photo' in request.POST and member.photo:
                    member.photo.delete()
                    member.photo = None

                if 'photo' in request.FILES:
                    if member.photo:
                        member.photo.delete()
                    member.photo = request.FILES['photo']

                member.save()

                messages.success(request, f"Team member '{member.name}' has been updated successfully.")

            except TeamMember.DoesNotExist:
                messages.error(request, "The team member you are trying to edit does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'delete':
            member_id = request.POST.get('member_id')

            try:
                member = TeamMember.objects.get(id=member_id)
                name = member.name

                # Delete the photo file if it exists
                if member.photo:
                    member.photo.delete()

                # Delete the team member
                member.delete()

                messages.success(request, f"Team member '{name}' has been deleted successfully.")

            except TeamMember.DoesNotExist:
                messages.error(request, "The team member you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:team_member_management')

    # GET request
    team_members = TeamMember.objects.all().order_by('order')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        team_members = team_members.filter(
            name__icontains=search_query
        ) | team_members.filter(
            position__icontains=search_query
        ) | team_members.filter(
            email__icontains=search_query
        )

    # Get the next order number for new team members
    next_order = 1
    if team_members.exists():
        next_order = team_members.aggregate(max_order=models.Max('order'))['max_order'] + 1

    context = {
        'team_members': team_members,
        'search_query': search_query,
        'next_order': next_order,
    }

    return render(request, 'custom_admin/team_member_management.html', context)

@login_required
@user_passes_test(is_admin)
def newsletter_management(request):
    """View for managing newsletter subscribers."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'activate':
            subscriber_id = request.POST.get('subscriber_id')

            try:
                subscriber = Newsletter.objects.get(id=subscriber_id)
                subscriber.is_active = True
                subscriber.save()
                messages.success(request, f"Subscriber {subscriber.email} has been activated successfully.")

            except Newsletter.DoesNotExist:
                messages.error(request, "The subscriber you are trying to activate does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'deactivate':
            subscriber_id = request.POST.get('subscriber_id')

            try:
                subscriber = Newsletter.objects.get(id=subscriber_id)
                subscriber.is_active = False
                subscriber.save()
                messages.success(request, f"Subscriber {subscriber.email} has been deactivated successfully.")

            except Newsletter.DoesNotExist:
                messages.error(request, "The subscriber you are trying to deactivate does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'delete':
            subscriber_id = request.POST.get('subscriber_id')

            try:
                subscriber = Newsletter.objects.get(id=subscriber_id)
                email = subscriber.email
                subscriber.delete()
                messages.success(request, f"Subscriber {email} has been deleted successfully.")

            except Newsletter.DoesNotExist:
                messages.error(request, "The subscriber you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'send_newsletter':
            subject = request.POST.get('subject')
            content = request.POST.get('content')
            recipients_type = request.POST.get('recipients')
            test_mode = request.POST.get('test_mode') == 'on'
            attachment = request.FILES.get('attachment')

            try:
                # Get recipients based on selection
                if recipients_type == 'all_active':
                    recipients = Newsletter.objects.filter(is_active=True)
                elif recipients_type == 'all':
                    recipients = Newsletter.objects.all()
                elif recipients_type == 'selected':
                    selected_ids = request.POST.getlist('selected_subscribers')
                    recipients = Newsletter.objects.filter(id__in=selected_ids)
                else:
                    recipients = []

                # If test mode, only send to admin
                if test_mode:
                    admin_email = request.user.email
                    # Here you would implement the actual email sending logic
                    # For now, we'll just show a success message
                    messages.success(request, f"Test newsletter sent to {admin_email}.")
                else:
                    # Here you would implement the actual email sending logic to all recipients
                    # For now, we'll just show a success message
                    recipient_count = recipients.count()
                    messages.success(request, f"Newsletter sent to {recipient_count} subscribers.")

                    # Create notifications for each recipient who is also a user
                    from accounts.models import CustomUser
                    user_emails = CustomUser.objects.values_list('email', flat=True)
                    for subscriber in recipients:
                        if subscriber.email in user_emails:
                            try:
                                user = CustomUser.objects.get(email=subscriber.email)
                                Notification.objects.create(
                                    user=user,
                                    title=f"Newsletter: {subject}",
                                    message=f"A new newsletter has been sent to your email: {subject}",
                                    notification_type="newsletter"
                                )
                            except CustomUser.DoesNotExist:
                                pass

            except Exception as e:
                messages.error(request, f"An error occurred while sending the newsletter: {str(e)}")

        return redirect('custom_admin:newsletter_management')

    # GET request
    subscribers = Newsletter.objects.all().order_by('-created_at')

    # Filter by active status if provided
    is_active = request.GET.get('is_active')
    if is_active is not None:
        is_active = is_active == 'true'
        subscribers = subscribers.filter(is_active=is_active)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        subscribers = subscribers.filter(email__icontains=search_query)

    context = {
        'subscribers': subscribers,
        'is_active': is_active,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/newsletter_management.html', context)

@login_required
@user_passes_test(is_admin)
def site_settings(request):
    """View for managing site settings."""
    settings = SiteSettings.get_settings()

    if request.method == 'POST':
        # Update site information
        settings.site_name = request.POST.get('site_name', settings.site_name)
        settings.contact_email = request.POST.get('contact_email', settings.contact_email)
        settings.support_email = request.POST.get('support_email', settings.support_email)

        # Update contact information
        settings.phone_number = request.POST.get('phone_number', settings.phone_number)
        settings.address_line1 = request.POST.get('address_line1', settings.address_line1)
        settings.address_line2 = request.POST.get('address_line2', settings.address_line2)
        settings.city = request.POST.get('city', settings.city)
        settings.state = request.POST.get('state', settings.state)
        settings.postal_code = request.POST.get('postal_code', settings.postal_code)
        settings.country = request.POST.get('country', settings.country)
        settings.business_hours = request.POST.get('business_hours', settings.business_hours)

        # Update branding
        settings.primary_color = request.POST.get('primary_color', settings.primary_color)
        settings.secondary_color = request.POST.get('secondary_color', settings.secondary_color)

        # Update social media
        settings.facebook_url = request.POST.get('facebook_url', settings.facebook_url)
        settings.twitter_url = request.POST.get('twitter_url', settings.twitter_url)
        settings.linkedin_url = request.POST.get('linkedin_url', settings.linkedin_url)
        settings.instagram_url = request.POST.get('instagram_url', settings.instagram_url)

        # Handle file uploads
        if 'site_logo' in request.FILES:
            settings.site_logo = request.FILES['site_logo']

        if 'site_favicon' in request.FILES:
            settings.site_favicon = request.FILES['site_favicon']

        settings.save()
        messages.success(request, _('Site settings updated successfully.'))
        return redirect('custom_admin:site_settings')

    context = {
        'settings': settings,
    }

    return render(request, 'custom_admin/site_settings.html', context)

@login_required
@user_passes_test(is_admin)
def subscription_management(request):
    """View for managing subscription plans and user subscriptions."""
    if request.method == 'POST':
        action = request.POST.get('action')

        # Plan management actions
        if action == 'add_plan':
            name = request.POST.get('name')
            plan_type = request.POST.get('plan_type')
            description = request.POST.get('description')
            price = request.POST.get('price')
            duration_days = request.POST.get('duration_days')
            is_active = request.POST.get('is_active') == 'on'

            # Job seeker features
            resume_builder = request.POST.get('resume_builder') == 'on'
            resume_review = request.POST.get('resume_review') == 'on'
            job_match_recommendations = request.POST.get('job_match_recommendations') == 'on'
            company_recommendations = request.POST.get('company_recommendations') == 'on'
            interview_preparation = request.POST.get('interview_preparation') == 'on'
            salary_insights = request.POST.get('salary_insights') == 'on'
            career_path_planning = request.POST.get('career_path_planning') == 'on'

            # Employer features
            featured_jobs = request.POST.get('featured_jobs') == 'on'
            priority_listing = request.POST.get('priority_listing') == 'on'
            candidate_matching = request.POST.get('candidate_matching') == 'on'
            advanced_analytics = request.POST.get('advanced_analytics') == 'on'
            unlimited_job_posts = request.POST.get('unlimited_job_posts') == 'on'
            applicant_tracking = request.POST.get('applicant_tracking') == 'on'

            try:
                SubscriptionPlan.objects.create(
                    name=name,
                    plan_type=plan_type,
                    description=description,
                    price=price,
                    duration_days=duration_days,
                    is_active=is_active,
                    resume_builder=resume_builder,
                    resume_review=resume_review,
                    job_match_recommendations=job_match_recommendations,
                    company_recommendations=company_recommendations,
                    interview_preparation=interview_preparation,
                    salary_insights=salary_insights,
                    career_path_planning=career_path_planning,
                    featured_jobs=featured_jobs,
                    priority_listing=priority_listing,
                    candidate_matching=candidate_matching,
                    advanced_analytics=advanced_analytics,
                    unlimited_job_posts=unlimited_job_posts,
                    applicant_tracking=applicant_tracking
                )
                messages.success(request, f"Subscription plan '{name}' has been created successfully.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'edit_plan':
            plan_id = request.POST.get('plan_id')
            name = request.POST.get('name')
            plan_type = request.POST.get('plan_type')
            description = request.POST.get('description')
            price = request.POST.get('price')
            duration_days = request.POST.get('duration_days')
            is_active = request.POST.get('is_active') == 'true'

            # Job seeker features
            resume_builder = request.POST.get('resume_builder') == 'on'
            resume_review = request.POST.get('resume_review') == 'on'
            job_match_recommendations = request.POST.get('job_match_recommendations') == 'on'
            company_recommendations = request.POST.get('company_recommendations') == 'on'
            interview_preparation = request.POST.get('interview_preparation') == 'on'
            salary_insights = request.POST.get('salary_insights') == 'on'
            career_path_planning = request.POST.get('career_path_planning') == 'on'

            # Employer features
            featured_jobs = request.POST.get('featured_jobs') == 'on'
            priority_listing = request.POST.get('priority_listing') == 'on'
            candidate_matching = request.POST.get('candidate_matching') == 'on'
            advanced_analytics = request.POST.get('advanced_analytics') == 'on'
            unlimited_job_posts = request.POST.get('unlimited_job_posts') == 'on'
            applicant_tracking = request.POST.get('applicant_tracking') == 'on'

            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
                plan.name = name
                plan.plan_type = plan_type
                plan.description = description
                plan.price = price
                plan.duration_days = duration_days
                plan.is_active = is_active

                # Update job seeker features
                plan.resume_builder = resume_builder
                plan.resume_review = resume_review
                plan.job_match_recommendations = job_match_recommendations
                plan.company_recommendations = company_recommendations
                plan.interview_preparation = interview_preparation
                plan.salary_insights = salary_insights
                plan.career_path_planning = career_path_planning

                # Update employer features
                plan.featured_jobs = featured_jobs
                plan.priority_listing = priority_listing
                plan.candidate_matching = candidate_matching
                plan.advanced_analytics = advanced_analytics
                plan.unlimited_job_posts = unlimited_job_posts
                plan.applicant_tracking = applicant_tracking

                plan.save()
                messages.success(request, f"Subscription plan '{name}' has been updated successfully.")
            except SubscriptionPlan.DoesNotExist:
                messages.error(request, "The subscription plan you are trying to edit does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'activate_plan':
            plan_id = request.POST.get('plan_id')
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
                plan.is_active = True
                plan.save()
                messages.success(request, f"Subscription plan '{plan.name}' has been activated.")
            except SubscriptionPlan.DoesNotExist:
                messages.error(request, "The subscription plan you are trying to activate does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'deactivate_plan':
            plan_id = request.POST.get('plan_id')
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
                plan.is_active = False
                plan.save()
                messages.success(request, f"Subscription plan '{plan.name}' has been deactivated.")
            except SubscriptionPlan.DoesNotExist:
                messages.error(request, "The subscription plan you are trying to deactivate does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        # User subscription management actions
        elif action == 'edit_subscription':
            subscription_id = request.POST.get('subscription_id')
            status = request.POST.get('status')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            auto_renew = request.POST.get('auto_renew') == 'true'
            cancellation_reason = request.POST.get('cancellation_reason', '')
            cancellation_date = request.POST.get('cancellation_date', None)

            try:
                subscription = UserSubscription.objects.get(id=subscription_id)
                old_status = subscription.status

                # Update subscription details
                subscription.status = status

                # Parse dates
                try:
                    subscription.start_date = datetime.strptime(start_date, '%Y-%m-%d')
                except (ValueError, TypeError):
                    pass  # Keep existing date if parsing fails

                try:
                    subscription.end_date = datetime.strptime(end_date, '%Y-%m-%d')
                except (ValueError, TypeError):
                    pass  # Keep existing date if parsing fails

                # Handle cancellation details if applicable
                if status == 'cancelled' and old_status != 'cancelled':
                    if cancellation_date:
                        try:
                            subscription.cancellation_date = datetime.strptime(cancellation_date, '%Y-%m-%d')
                        except (ValueError, TypeError):
                            subscription.cancellation_date = timezone.now()
                    else:
                        subscription.cancellation_date = timezone.now()

                    subscription.cancellation_reason = cancellation_reason

                # Set auto-renewal
                if hasattr(subscription, 'auto_renew'):
                    subscription.auto_renew = auto_renew

                subscription.save()

                # Create notification for the user
                if old_status != status:
                    Notification.objects.create(
                        user=subscription.user,
                        notification_type='subscription',
                        title='Subscription Status Updated',
                        message=f'Your subscription status has been updated to {subscription.get_status_display()}.',
                        related_id=subscription.id
                    )

                messages.success(request, f"Subscription for {subscription.user.get_full_name()} has been updated successfully.")

            except UserSubscription.DoesNotExist:
                messages.error(request, "The subscription you are trying to edit does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'cancel_subscription':
            subscription_id = request.POST.get('subscription_id')

            try:
                subscription = UserSubscription.objects.get(id=subscription_id)

                # Update subscription status
                subscription.status = 'cancelled'
                subscription.cancellation_date = timezone.now()
                subscription.save()

                # Create notification for the user
                Notification.objects.create(
                    user=subscription.user,
                    notification_type='subscription',
                    title='Subscription Cancelled',
                    message='Your subscription has been cancelled by an administrator.',
                    related_id=subscription.id
                )

                messages.success(request, f"Subscription for {subscription.user.get_full_name()} has been cancelled successfully.")

            except UserSubscription.DoesNotExist:
                messages.error(request, "The subscription you are trying to cancel does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'renew_subscription':
            subscription_id = request.POST.get('subscription_id')

            try:
                subscription = UserSubscription.objects.get(id=subscription_id)

                # Calculate new dates
                if subscription.end_date and subscription.end_date > timezone.now():
                    # If subscription hasn't expired, extend from current end date
                    new_start_date = subscription.end_date
                else:
                    # If subscription has expired, start from now
                    new_start_date = timezone.now()

                new_end_date = new_start_date + timedelta(days=subscription.plan.duration_days)

                # Update subscription
                subscription.status = 'active'
                subscription.start_date = new_start_date
                subscription.end_date = new_end_date
                subscription.save()

                # Create notification for the user
                Notification.objects.create(
                    user=subscription.user,
                    notification_type='subscription',
                    title='Subscription Renewed',
                    message=f'Your {subscription.plan.name} subscription has been renewed by an administrator.',
                    related_id=subscription.id
                )

                messages.success(request, f"Subscription for {subscription.user.get_full_name()} has been renewed successfully.")

            except UserSubscription.DoesNotExist:
                messages.error(request, "The subscription you are trying to renew does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:subscription_management')

    # GET request
    plans = SubscriptionPlan.objects.all().order_by('price')
    subscriptions = UserSubscription.objects.all().order_by('-start_date')

    # Filter subscriptions by status if provided
    status = request.GET.get('status')
    if status:
        subscriptions = subscriptions.filter(status=status)

    # Filter subscriptions by plan if provided
    plan_id = request.GET.get('plan')
    if plan_id:
        subscriptions = subscriptions.filter(plan_id=plan_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        subscriptions = subscriptions.filter(
            user__email__icontains=search_query
        ) | subscriptions.filter(
            user__first_name__icontains=search_query
        ) | subscriptions.filter(
            user__last_name__icontains=search_query
        ) | subscriptions.filter(
            plan__name__icontains=search_query
        )

    context = {
        'plans': plans,
        'subscriptions': subscriptions,
        'status': status,
        'plan_id': plan_id,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/subscription_management.html', context)

@login_required
@user_passes_test(is_admin)
def job_category_management(request):
    """View for managing job categories."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            description = request.POST.get('description')

            # Check if category with this slug already exists
            if JobCategory.objects.filter(slug=slug).exists():
                messages.error(request, f"A category with the slug '{slug}' already exists.")
            else:
                JobCategory.objects.create(
                    name=name,
                    slug=slug,
                    description=description
                )
                messages.success(request, f"Category '{name}' has been created successfully.")

        elif action == 'edit':
            category_id = request.POST.get('category_id')
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            description = request.POST.get('description')

            try:
                category = JobCategory.objects.get(id=category_id)

                # Check if slug is being changed and if it already exists
                if category.slug != slug and JobCategory.objects.filter(slug=slug).exists():
                    messages.error(request, f"A category with the slug '{slug}' already exists.")
                else:
                    category.name = name
                    category.slug = slug
                    category.description = description
                    category.save()
                    messages.success(request, f"Category '{name}' has been updated successfully.")

            except JobCategory.DoesNotExist:
                messages.error(request, "The category you are trying to edit does not exist.")

        elif action == 'delete':
            category_id = request.POST.get('category_id')

            try:
                category = JobCategory.objects.get(id=category_id)
                name = category.name
                category.delete()
                messages.success(request, f"Category '{name}' has been deleted successfully.")

            except JobCategory.DoesNotExist:
                messages.error(request, "The category you are trying to delete does not exist.")

        return redirect('custom_admin:job_category_management')

    # GET request
    categories = JobCategory.objects.all().order_by('name')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    context = {
        'categories': categories,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/job_category_management.html', context)

@login_required
@user_passes_test(is_admin)
def job_application_management(request):
    """View for managing job applications."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_status':
            application_id = request.POST.get('application_id')
            status = request.POST.get('status')
            notes = request.POST.get('notes')
            notify_applicant = request.POST.get('notify_applicant') == 'on'

            try:
                application = JobApplication.objects.get(id=application_id)
                old_status = application.status

                # Update application status and notes
                application.status = status
                application.notes = notes
                application.save()

                # Create notification for the applicant
                if notify_applicant:
                    Notification.objects.create(
                        user=application.user,
                        notification_type='application',
                        title='Application Status Updated',
                        message=f'Your application for {application.job.title} has been updated to {application.get_status_display()}.',
                        related_id=application.id
                    )

                messages.success(request, f"Application status has been updated from {old_status} to {status}.")

            except JobApplication.DoesNotExist:
                messages.error(request, "The application you are trying to update does not exist.")

        return redirect('custom_admin:job_application_management')

    # GET request
    applications = JobApplication.objects.all().order_by('-applied_at')

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)

    # Filter by job if provided
    job_id = request.GET.get('job')
    if job_id:
        applications = applications.filter(job_id=job_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        applications = applications.filter(
            job__title__icontains=search_query
        ) | applications.filter(
            user__email__icontains=search_query
        )

    # Get all jobs for filter dropdown
    jobs = JobListing.objects.all().order_by('title')

    context = {
        'applications': applications,
        'jobs': jobs,
        'status': status,
        'job_id': job_id,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/job_application_management.html', context)

@login_required
@user_passes_test(is_admin)
def saved_job_management(request):
    """View for managing saved jobs."""
    saved_jobs = SavedJob.objects.all().order_by('-saved_at')

    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        saved_jobs = saved_jobs.filter(user_id=user_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        saved_jobs = saved_jobs.filter(
            job__title__icontains=search_query
        ) | saved_jobs.filter(
            user__email__icontains=search_query
        )

    context = {
        'saved_jobs': saved_jobs,
        'user_id': user_id,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/saved_job_management.html', context)

@login_required
@user_passes_test(is_admin)
def job_renewal_management(request):
    """View for managing job renewals."""
    renewals = JobRenewal.objects.all().order_by('-updated_at')

    # Filter by job if provided
    job_id = request.GET.get('job')
    if job_id:
        renewals = renewals.filter(job_id=job_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        renewals = renewals.filter(
            job__title__icontains=search_query
        ) | renewals.filter(
            renewed_by__email__icontains=search_query
        )

    context = {
        'renewals': renewals,
        'job_id': job_id,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/job_renewal_management.html', context)

@login_required
@user_passes_test(is_admin)
def job_package_management(request):
    """View for managing job packages."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            # Get basic package details
            name = request.POST.get('name')
            price = request.POST.get('price')
            job_posts = request.POST.get('job_posts')
            duration_days = request.POST.get('duration_days')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active') == 'on'

            # Get feature flags
            featured_jobs = request.POST.get('featured_jobs') == 'on'
            priority_listing = request.POST.get('priority_listing') == 'on'
            highlight_jobs = request.POST.get('highlight_jobs') == 'on'
            job_refresh = request.POST.get('job_refresh') == 'on'

            # Create job package
            JobPackage.objects.create(
                name=name,
                price=price,
                job_posts=job_posts,
                duration_days=duration_days,
                description=description,
                is_active=is_active,
                featured_jobs=featured_jobs,
                priority_listing=priority_listing,
                highlight_jobs=highlight_jobs,
                job_refresh=job_refresh
            )

            messages.success(request, f"Job package '{name}' has been created successfully.")

        elif action == 'edit':
            package_id = request.POST.get('package_id')

            try:
                package = JobPackage.objects.get(id=package_id)

                # Update basic package details
                package.name = request.POST.get('name')
                package.price = request.POST.get('price')
                package.job_posts = request.POST.get('job_posts')
                package.duration_days = request.POST.get('duration_days')
                package.description = request.POST.get('description')
                package.is_active = request.POST.get('is_active') == 'on'

                # Update feature flags
                package.featured_jobs = request.POST.get('featured_jobs') == 'on'
                package.priority_listing = request.POST.get('priority_listing') == 'on'
                package.highlight_jobs = request.POST.get('highlight_jobs') == 'on'
                package.job_refresh = request.POST.get('job_refresh') == 'on'

                package.save()
                messages.success(request, f"Job package '{package.name}' has been updated successfully.")

            except JobPackage.DoesNotExist:
                messages.error(request, "The job package you are trying to edit does not exist.")

        elif action == 'delete':
            package_id = request.POST.get('package_id')

            try:
                package = JobPackage.objects.get(id=package_id)
                name = package.name

                # Check if there are active job listings using this package
                if JobListing.objects.filter(package=package).exists():
                    messages.warning(request, f"Cannot delete package '{name}' because it is being used by active job listings. Consider marking it as inactive instead.")
                else:
                    package.delete()
                    messages.success(request, f"Job package '{name}' has been deleted successfully.")

            except JobPackage.DoesNotExist:
                messages.error(request, "The job package you are trying to delete does not exist.")

        return redirect('custom_admin:job_package_management')

    # GET request
    packages = JobPackage.objects.all().order_by('price')

    # Filter by active status if provided
    is_active = request.GET.get('is_active')
    if is_active is not None:
        is_active = is_active == 'true'
        packages = packages.filter(is_active=is_active)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        packages = packages.filter(
            name__icontains=search_query
        ) | packages.filter(
            description__icontains=search_query
        )

    context = {
        'packages': packages,
        'is_active': is_active,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/job_package_management.html', context)

@login_required
@user_passes_test(is_admin)
def job_analytics_management(request):
    """View for managing job analytics."""
    from django.db.models import Count, F, Q
    from django.utils import timezone
    import json
    from datetime import datetime, timedelta
    import calendar

    # Get filter parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    selected_category = request.GET.get('category')

    # Set default date range to last 6 months if not provided
    today = timezone.now().date()
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            start_date = today - timedelta(days=180)
    else:
        start_date = today - timedelta(days=180)

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            end_date = today
    else:
        end_date = today

    # Base queryset with date filters
    job_queryset = JobListing.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    application_queryset = JobApplication.objects.filter(applied_at__date__gte=start_date, applied_at__date__lte=end_date)

    # Apply category filter if provided
    if selected_category:
        job_queryset = job_queryset.filter(category_id=selected_category)
        application_queryset = application_queryset.filter(job__category_id=selected_category)

    # Get all categories for filter dropdown
    categories = JobCategory.objects.all()

    # Calculate basic metrics
    total_jobs = job_queryset.count()
    active_jobs = job_queryset.filter(status='active').count()
    total_applications = application_queryset.count()

    # Calculate average applications per job
    avg_applications_per_job = round(total_applications / total_jobs, 1) if total_jobs > 0 else 0

    # Calculate growth metrics (compared to previous period)
    previous_start_date = start_date - (end_date - start_date)
    previous_end_date = start_date - timedelta(days=1)

    previous_job_queryset = JobListing.objects.filter(created_at__date__gte=previous_start_date, created_at__date__lte=previous_end_date)
    previous_application_queryset = JobApplication.objects.filter(applied_at__date__gte=previous_start_date, applied_at__date__lte=previous_end_date)

    if selected_category:
        previous_job_queryset = previous_job_queryset.filter(category_id=selected_category)
        previous_application_queryset = previous_application_queryset.filter(job__category_id=selected_category)

    previous_total_jobs = previous_job_queryset.count()
    previous_active_jobs = previous_job_queryset.filter(status='active').count()
    previous_total_applications = previous_application_queryset.count()
    previous_avg_applications = round(previous_total_applications / previous_total_jobs, 1) if previous_total_jobs > 0 else 0

    # Calculate growth percentages
    job_growth = round(((total_jobs - previous_total_jobs) / previous_total_jobs) * 100, 1) if previous_total_jobs > 0 else 0
    active_job_growth = round(((active_jobs - previous_active_jobs) / previous_active_jobs) * 100, 1) if previous_active_jobs > 0 else 0
    application_growth = round(((total_applications - previous_total_applications) / previous_total_applications) * 100, 1) if previous_total_applications > 0 else 0
    avg_applications_growth = round(((avg_applications_per_job - previous_avg_applications) / previous_avg_applications) * 100, 1) if previous_avg_applications > 0 else 0

    # Jobs by Category data
    category_data = job_queryset.values('category__name').annotate(count=Count('id')).order_by('-count')
    category_names = json.dumps([item['category__name'] for item in category_data])
    category_counts = json.dumps([item['count'] for item in category_data])

    # Applications by Month data
    months_data = {}
    for i in range(6):
        month_date = end_date - timedelta(days=30 * i)
        month_name = month_date.strftime('%b %Y')
        months_data[month_name] = 0

    # Get monthly applications data
    monthly_applications_data = []
    for i in range(6):
        month_date = end_date - timedelta(days=30 * i)
        month_start = datetime(month_date.year, month_date.month, 1).date()
        if month_date.month == 12:
            month_end = datetime(month_date.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(month_date.year, month_date.month + 1, 1).date() - timedelta(days=1)

        month_name = month_date.strftime('%b %Y')
        count = application_queryset.filter(
            applied_at__date__gte=month_start,
            applied_at__date__lte=month_end
        ).count()

        months_data[month_name] = count

    months = json.dumps(list(reversed(list(months_data.keys()))))
    monthly_applications = json.dumps(list(reversed(list(months_data.values()))))

    # Top 10 Jobs by Applications
    top_jobs = job_queryset.annotate(
        application_count=Count('applications')
    ).order_by('-application_count')[:10]

    # Application Status Distribution
    status_data = application_queryset.values('status').annotate(count=Count('id')).order_by('status')
    status_mapping = {
        'pending': 'Pending',
        'reviewed': 'Reviewed',
        'interview': 'Interview',
        'hired': 'Hired',
        'rejected': 'Rejected'
    }

    status_counts_dict = {status_mapping.get(item['status'], item['status']): item['count'] for item in status_data}
    status_labels = json.dumps(list(status_counts_dict.keys()))
    status_counts = json.dumps(list(status_counts_dict.values()))

    # Job Posting Trends (last 12 months)
    trend_months_data = {}
    for i in range(12):
        month_date = end_date - timedelta(days=30 * i)
        month_name = month_date.strftime('%b %Y')
        trend_months_data[month_name] = 0

    # Get job posting trends data
    for i in range(12):
        month_date = end_date - timedelta(days=30 * i)
        month_start = datetime(month_date.year, month_date.month, 1).date()
        if month_date.month == 12:
            month_end = datetime(month_date.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(month_date.year, month_date.month + 1, 1).date() - timedelta(days=1)

        month_name = month_date.strftime('%b %Y')
        count = job_queryset.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()

        trend_months_data[month_name] = count

    trend_months = json.dumps(list(reversed(list(trend_months_data.keys()))))
    job_trends = json.dumps(list(reversed(list(trend_months_data.values()))))

    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'avg_applications_per_job': avg_applications_per_job,
        'job_growth': job_growth,
        'active_job_growth': active_job_growth,
        'application_growth': application_growth,
        'avg_applications_growth': avg_applications_growth,
        'category_names': category_names,
        'category_counts': category_counts,
        'months': months,
        'monthly_applications': monthly_applications,
        'top_jobs': top_jobs,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'trend_months': trend_months,
        'job_trends': job_trends,
        'start_date': start_date,
        'end_date': end_date,
        'selected_category': selected_category,
        'categories': categories,
    }

    return render(request, 'custom_admin/job_analytics_management.html', context)

@login_required
@user_passes_test(is_admin)
def export_job_analytics(request):
    """Export job analytics data in various formats."""
    from django.http import HttpResponse
    from django.db.models import Count
    from django.utils import timezone
    import csv
    import json
    from datetime import datetime, timedelta

    # Get filter parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    selected_category = request.GET.get('category')
    export_format = request.GET.get('format', 'csv')

    # Set default date range to last 6 months if not provided
    today = timezone.now().date()
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            start_date = today - timedelta(days=180)
    else:
        start_date = today - timedelta(days=180)

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            end_date = today
    else:
        end_date = today

    # Base queryset with date filters
    job_queryset = JobListing.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    application_queryset = JobApplication.objects.filter(applied_at__date__gte=start_date, applied_at__date__lte=end_date)

    # Apply category filter if provided
    if selected_category:
        job_queryset = job_queryset.filter(category_id=selected_category)
        application_queryset = application_queryset.filter(job__category_id=selected_category)

    # Get category name if provided
    category_name = "All Categories"
    if selected_category:
        try:
            category = JobCategory.objects.get(id=selected_category)
            category_name = category.name
        except JobCategory.DoesNotExist:
            pass

    # Prepare data for export
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="job_analytics_{start_date}_to_{end_date}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Job Analytics Report'])
        writer.writerow([f'Date Range: {start_date} to {end_date}'])
        writer.writerow([f'Category: {category_name}'])
        writer.writerow([])

        # Summary statistics
        writer.writerow(['Summary Statistics'])
        writer.writerow(['Total Jobs', job_queryset.count()])
        writer.writerow(['Active Jobs', job_queryset.filter(status='active').count()])
        writer.writerow(['Total Applications', application_queryset.count()])
        avg_applications = round(application_queryset.count() / job_queryset.count(), 1) if job_queryset.count() > 0 else 0
        writer.writerow(['Average Applications per Job', avg_applications])
        writer.writerow([])

        # Jobs by Category
        writer.writerow(['Jobs by Category'])
        writer.writerow(['Category', 'Count'])
        category_data = job_queryset.values('category__name').annotate(count=Count('id')).order_by('-count')
        for item in category_data:
            writer.writerow([item['category__name'], item['count']])
        writer.writerow([])

        # Top 10 Jobs by Applications
        writer.writerow(['Top 10 Jobs by Applications'])
        writer.writerow(['Job Title', 'Company', 'Category', 'Applications'])
        top_jobs = job_queryset.annotate(
            application_count=Count('applications')
        ).order_by('-application_count')[:10]
        for job in top_jobs:
            writer.writerow([job.title, job.company.name, job.category.name, job.application_count])
        writer.writerow([])

        # Application Status Distribution
        writer.writerow(['Application Status Distribution'])
        writer.writerow(['Status', 'Count'])
        status_data = application_queryset.values('status').annotate(count=Count('id')).order_by('status')
        status_mapping = {
            'pending': 'Pending',
            'reviewed': 'Reviewed',
            'interview': 'Interview',
            'hired': 'Hired',
            'rejected': 'Rejected'
        }
        for item in status_data:
            status_name = status_mapping.get(item['status'], item['status'])
            writer.writerow([status_name, item['count']])

        return response

    elif export_format == 'excel':
        try:
            import xlsxwriter
            from io import BytesIO

            # Create a workbook and add a worksheet
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Job Analytics')

            # Add formats
            title_format = workbook.add_format({'bold': True, 'font_size': 14})
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D9EAD3', 'border': 1})
            cell_format = workbook.add_format({'border': 1})

            # Write title and date range
            worksheet.write(0, 0, 'Job Analytics Report', title_format)
            worksheet.write(1, 0, f'Date Range: {start_date} to {end_date}')
            worksheet.write(2, 0, f'Category: {category_name}')

            # Summary statistics
            worksheet.write(4, 0, 'Summary Statistics', header_format)
            worksheet.write(5, 0, 'Metric', header_format)
            worksheet.write(5, 1, 'Value', header_format)

            worksheet.write(6, 0, 'Total Jobs', cell_format)
            worksheet.write(6, 1, job_queryset.count(), cell_format)

            worksheet.write(7, 0, 'Active Jobs', cell_format)
            worksheet.write(7, 1, job_queryset.filter(status='active').count(), cell_format)

            worksheet.write(8, 0, 'Total Applications', cell_format)
            worksheet.write(8, 1, application_queryset.count(), cell_format)

            avg_applications = round(application_queryset.count() / job_queryset.count(), 1) if job_queryset.count() > 0 else 0
            worksheet.write(9, 0, 'Average Applications per Job', cell_format)
            worksheet.write(9, 1, avg_applications, cell_format)

            # Jobs by Category
            worksheet.write(11, 0, 'Jobs by Category', header_format)
            worksheet.write(12, 0, 'Category', header_format)
            worksheet.write(12, 1, 'Count', header_format)

            category_data = job_queryset.values('category__name').annotate(count=Count('id')).order_by('-count')
            row = 13
            for item in category_data:
                worksheet.write(row, 0, item['category__name'], cell_format)
                worksheet.write(row, 1, item['count'], cell_format)
                row += 1

            # Top 10 Jobs by Applications
            row += 2
            worksheet.write(row, 0, 'Top 10 Jobs by Applications', header_format)
            row += 1
            worksheet.write(row, 0, 'Job Title', header_format)
            worksheet.write(row, 1, 'Company', header_format)
            worksheet.write(row, 2, 'Category', header_format)
            worksheet.write(row, 3, 'Applications', header_format)

            top_jobs = job_queryset.annotate(
                application_count=Count('applications')
            ).order_by('-application_count')[:10]

            row += 1
            for job in top_jobs:
                worksheet.write(row, 0, job.title, cell_format)
                worksheet.write(row, 1, job.company.name, cell_format)
                worksheet.write(row, 2, job.category.name, cell_format)
                worksheet.write(row, 3, job.application_count, cell_format)
                row += 1

            # Application Status Distribution
            row += 2
            worksheet.write(row, 0, 'Application Status Distribution', header_format)
            row += 1
            worksheet.write(row, 0, 'Status', header_format)
            worksheet.write(row, 1, 'Count', header_format)

            status_data = application_queryset.values('status').annotate(count=Count('id')).order_by('status')
            status_mapping = {
                'pending': 'Pending',
                'reviewed': 'Reviewed',
                'interview': 'Interview',
                'hired': 'Hired',
                'rejected': 'Rejected'
            }

            row += 1
            for item in status_data:
                status_name = status_mapping.get(item['status'], item['status'])
                worksheet.write(row, 0, status_name, cell_format)
                worksheet.write(row, 1, item['count'], cell_format)
                row += 1

            # Auto-adjust column widths
            worksheet.set_column(0, 0, 30)
            worksheet.set_column(1, 3, 15)

            workbook.close()

            # Create the response
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="job_analytics_{start_date}_to_{end_date}.xlsx"'

            return response

        except ImportError:
            # If xlsxwriter is not available, fall back to CSV
            messages.warning(request, "Excel export is not available. Falling back to CSV format.")
            return redirect(f"{reverse('custom_admin:export_job_analytics')}?format=csv&start_date={start_date}&end_date={end_date}&category={selected_category}")

    elif export_format == 'pdf':
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from io import BytesIO

            # Create a file-like buffer to receive PDF data
            buffer = BytesIO()

            # Create the PDF object, using the buffer as its "file"
            doc = SimpleDocTemplate(buffer, pagesize=letter)

            # Get the default style sheet
            styles = getSampleStyleSheet()

            # Create the content
            content = []

            # Add title
            title_style = styles['Heading1']
            content.append(Paragraph('Job Analytics Report', title_style))
            content.append(Spacer(1, 12))

            # Add date range and category
            content.append(Paragraph(f'Date Range: {start_date} to {end_date}', styles['Normal']))
            content.append(Paragraph(f'Category: {category_name}', styles['Normal']))
            content.append(Spacer(1, 12))

            # Summary statistics
            content.append(Paragraph('Summary Statistics', styles['Heading2']))
            data = [
                ['Metric', 'Value'],
                ['Total Jobs', str(job_queryset.count())],
                ['Active Jobs', str(job_queryset.filter(status='active').count())],
                ['Total Applications', str(application_queryset.count())],
                ['Average Applications per Job', str(round(application_queryset.count() / job_queryset.count(), 1) if job_queryset.count() > 0 else 0)]
            ]

            table = Table(data, colWidths=[300, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(table)
            content.append(Spacer(1, 12))

            # Jobs by Category
            content.append(Paragraph('Jobs by Category', styles['Heading2']))
            category_data = job_queryset.values('category__name').annotate(count=Count('id')).order_by('-count')
            data = [['Category', 'Count']]
            for item in category_data:
                data.append([item['category__name'], str(item['count'])])

            table = Table(data, colWidths=[300, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(table)
            content.append(Spacer(1, 12))

            # Top 10 Jobs by Applications
            content.append(Paragraph('Top 10 Jobs by Applications', styles['Heading2']))
            top_jobs = job_queryset.annotate(
                application_count=Count('jobapplication')
            ).order_by('-application_count')[:10]

            data = [['Job Title', 'Company', 'Category', 'Applications']]
            for job in top_jobs:
                data.append([job.title, job.company.name, job.category.name, str(job.application_count)])

            table = Table(data, colWidths=[150, 100, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (3, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(table)
            content.append(Spacer(1, 12))

            # Application Status Distribution
            content.append(Paragraph('Application Status Distribution', styles['Heading2']))
            status_data = application_queryset.values('status').annotate(count=Count('id')).order_by('status')
            status_mapping = {
                'pending': 'Pending',
                'reviewed': 'Reviewed',
                'interview': 'Interview',
                'hired': 'Hired',
                'rejected': 'Rejected'
            }

            data = [['Status', 'Count']]
            for item in status_data:
                status_name = status_mapping.get(item['status'], item['status'])
                data.append([status_name, str(item['count'])])

            table = Table(data, colWidths=[300, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(table)

            # Build the PDF
            doc.build(content)

            # Get the value of the BytesIO buffer and write it to the response
            pdf = buffer.getvalue()
            buffer.close()

            # Create the HTTP response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="job_analytics_{start_date}_to_{end_date}.pdf"'
            response.write(pdf)

            return response

        except ImportError:
            # If reportlab is not available, fall back to CSV
            messages.warning(request, "PDF export is not available. Falling back to CSV format.")
            return redirect(f"{reverse('custom_admin:export_job_analytics')}?format=csv&start_date={start_date}&end_date={end_date}&category={selected_category}")

    else:
        # Default to CSV if format is not recognized
        messages.warning(request, f"Export format '{export_format}' is not supported. Falling back to CSV format.")
        return redirect(f"{reverse('custom_admin:export_job_analytics')}?format=csv&start_date={start_date}&end_date={end_date}&category={selected_category}")

@login_required
@user_passes_test(is_admin)
def company_connection_management(request):
    """View for managing company connections."""
    if request.method == 'POST':
        action = request.POST.get('action')
        connection_id = request.POST.get('connection_id')

        try:
            connection = CompanyConnection.objects.get(id=connection_id)
            user_name = connection.user.get_full_name()
            company_name = connection.company.name

            if action == 'approve':
                # Approve the connection
                connection.status = 'approved'
                connection.save()

                # Create a notification for the user
                Notification.objects.create(
                    user=connection.user,
                    title="Connection Approved",
                    message=f"Your connection request to {company_name} has been approved.",
                    notification_type="connection_approved"
                )

                messages.success(request, f"Connection between {user_name} and {company_name} has been approved.")

            elif action == 'reject':
                # Reject the connection
                connection.status = 'rejected'
                connection.save()

                # Create a notification for the user
                Notification.objects.create(
                    user=connection.user,
                    title="Connection Rejected",
                    message=f"Your connection request to {company_name} has been rejected.",
                    notification_type="connection_rejected"
                )

                messages.success(request, f"Connection between {user_name} and {company_name} has been rejected.")

            elif action == 'delete':
                # Delete the connection
                connection.delete()

                messages.success(request, f"Connection between {user_name} and {company_name} has been deleted.")

        except CompanyConnection.DoesNotExist:
            messages.error(request, "The connection you are trying to manage does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:company_connection_management')

    # GET request
    connections = CompanyConnection.objects.all().order_by('-created_at')

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        connections = connections.filter(status=status)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        connections = connections.filter(
            company__name__icontains=search_query
        ) | connections.filter(
            user__email__icontains=search_query
        ) | connections.filter(
            user__first_name__icontains=search_query
        ) | connections.filter(
            user__last_name__icontains=search_query
        )

    # Add recent applications to each connection
    for connection in connections:
        connection.recent_applications = JobApplication.objects.filter(
            job__company=connection.company,
            applicant=connection.user
        ).order_by('-applied_at')[:3]

    context = {
        'connections': connections,
        'status': status,
        'search_query': search_query,
    }

    return render(request, 'custom_admin/company_connection_management.html', context)

@login_required
@user_passes_test(is_admin)
def company_follower_management(request):
    """View for managing company followers."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            follower_id = request.POST.get('follower_id')

            try:
                follower = CompanyFollower.objects.get(id=follower_id)
                user_name = follower.user.get_full_name()
                company_name = follower.company.name

                # Delete the follower relationship
                follower.delete()

                messages.success(request, f"{user_name} has been removed as a follower of {company_name}.")

            except CompanyFollower.DoesNotExist:
                messages.error(request, "The follower relationship you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:company_follower_management')

    # GET request
    followers = CompanyFollower.objects.all().order_by('-created_at')

    # Filter by company if provided
    company_id = request.GET.get('company')
    if company_id:
        followers = followers.filter(company_id=company_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        followers = followers.filter(
            company__name__icontains=search_query
        ) | followers.filter(
            user__email__icontains=search_query
        ) | followers.filter(
            user__first_name__icontains=search_query
        ) | followers.filter(
            user__last_name__icontains=search_query
        )

    # Get all companies for filter dropdown
    all_companies = Company.objects.filter(
        id__in=CompanyFollower.objects.values_list('company_id', flat=True).distinct()
    ).order_by('name')

    # Add recent applications to each follower
    for follower in followers:
        follower.recent_applications = JobApplication.objects.filter(
            job__company=follower.company,
            applicant=follower.user
        ).order_by('-applied_at')[:3]

    context = {
        'followers': followers,
        'company_id': company_id,
        'search_query': search_query,
        'all_companies': all_companies,
    }

    return render(request, 'custom_admin/company_follower_management.html', context)

@login_required
@user_passes_test(is_admin)
def hero_section_management(request):
    """View for managing hero sections."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'edit':
            hero_id = request.POST.get('hero_id')
            title = request.POST.get('title')
            subtitle = request.POST.get('subtitle')
            is_active = request.POST.get('is_active') == 'on'

            try:
                hero = HeroSection.objects.get(id=hero_id)
                hero.title = title
                hero.subtitle = subtitle
                hero.is_active = is_active

                # Handle background image upload
                if 'background_image' in request.FILES:
                    hero.background_image = request.FILES['background_image']

                # Handle mobile background image upload
                if 'mobile_background_image' in request.FILES:
                    hero.mobile_background_image = request.FILES['mobile_background_image']

                hero.save()
                messages.success(request, f"Hero section for {hero.get_section_type_display()} has been updated successfully.")

            except HeroSection.DoesNotExist:
                messages.error(request, "The hero section you are trying to edit does not exist.")

        return redirect('custom_admin:hero_section_management')

    # GET request
    hero_sections = HeroSection.objects.all().order_by('section_type')

    # Create default hero sections if they don't exist
    section_types = [choice[0] for choice in HeroSection.SECTION_TYPE_CHOICES]
    existing_types = hero_sections.values_list('section_type', flat=True)

    for section_type in section_types:
        if section_type not in existing_types:
            HeroSection.objects.create(section_type=section_type)

    # Refresh the queryset to include newly created sections
    hero_sections = HeroSection.objects.all().order_by('section_type')

    context = {
        'hero_sections': hero_sections,
    }

    return render(request, 'custom_admin/hero_section_management.html', context)

@login_required
@user_passes_test(is_admin)
def legal_page_management(request):
    """View for managing legal pages."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            title = request.POST.get('title')
            slug = request.POST.get('slug')
            page_type = request.POST.get('page_type')
            content = request.POST.get('content')
            is_active = request.POST.get('is_active') == 'on'

            # Check if page with this slug already exists
            if LegalPage.objects.filter(slug=slug).exists():
                messages.error(request, f"A legal page with the slug '{slug}' already exists.")
            else:
                LegalPage.objects.create(
                    title=title,
                    slug=slug,
                    page_type=page_type,
                    content=content,
                    is_active=is_active
                )
                messages.success(request, f"Legal page '{title}' has been created successfully.")

        elif action == 'edit':
            page_id = request.POST.get('page_id')
            title = request.POST.get('title')
            slug = request.POST.get('slug')
            page_type = request.POST.get('page_type')
            content = request.POST.get('content')
            is_active = request.POST.get('is_active') == 'on'

            try:
                legal_page = LegalPage.objects.get(id=page_id)

                # Check if slug is being changed and if it already exists
                if legal_page.slug != slug and LegalPage.objects.filter(slug=slug).exists():
                    messages.error(request, f"A legal page with the slug '{slug}' already exists.")
                else:
                    legal_page.title = title
                    legal_page.slug = slug
                    legal_page.page_type = page_type
                    legal_page.content = content
                    legal_page.is_active = is_active
                    legal_page.save()
                    messages.success(request, f"Legal page '{title}' has been updated successfully.")

            except LegalPage.DoesNotExist:
                messages.error(request, "The legal page you are trying to edit does not exist.")

        elif action == 'delete':
            page_id = request.POST.get('page_id')

            try:
                legal_page = LegalPage.objects.get(id=page_id)
                title = legal_page.title
                legal_page.delete()
                messages.success(request, f"Legal page '{title}' has been deleted successfully.")

            except LegalPage.DoesNotExist:
                messages.error(request, "The legal page you are trying to delete does not exist.")

        return redirect('custom_admin:legal_page_management')

    # GET request
    legal_pages = LegalPage.objects.all().order_by('title')

    # Filter by page type if provided
    page_type = request.GET.get('page_type')
    if page_type:
        legal_pages = legal_pages.filter(page_type=page_type)

    # Filter by active status if provided
    is_active = request.GET.get('is_active')
    if is_active is not None:
        is_active = is_active == 'true'
        legal_pages = legal_pages.filter(is_active=is_active)

    context = {
        'legal_pages': legal_pages,
        'page_type': page_type,
        'is_active': is_active,
    }

    return render(request, 'custom_admin/legal_page_management.html', context)

@login_required
@user_passes_test(is_admin)
def notification_management(request):
    """View for managing notifications."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            title = request.POST.get('title')
            message = request.POST.get('message')
            notification_type = request.POST.get('notification_type')
            recipient_type = request.POST.get('recipient_type')

            if recipient_type == 'specific':
                user_id = request.POST.get('user_id')
                if user_id:
                    try:
                        user = CustomUser.objects.get(id=user_id)
                        Notification.objects.create(
                            user=user,
                            title=title,
                            message=message,
                            notification_type=notification_type
                        )
                        messages.success(request, f"Notification has been sent to {user.get_full_name()}.")
                    except CustomUser.DoesNotExist:
                        messages.error(request, "The selected user does not exist.")
                else:
                    messages.error(request, "Please select a user.")
            else:
                # Create notifications for multiple users
                if recipient_type == 'all':
                    users = CustomUser.objects.all()
                elif recipient_type == 'job_seekers':
                    users = CustomUser.objects.filter(user_type='job_seeker')
                elif recipient_type == 'employers':
                    users = CustomUser.objects.filter(user_type='employer')

                # Create a notification for each user
                notification_count = 0
                for user in users:
                    Notification.objects.create(
                        user=user,
                        title=title,
                        message=message,
                        notification_type=notification_type
                    )
                    notification_count += 1

                messages.success(request, f"{notification_count} notifications have been sent successfully.")

        elif action == 'mark_read':
            notification_id = request.POST.get('notification_id')

            try:
                notification = Notification.objects.get(id=notification_id)
                notification.is_read = True
                notification.save()
                messages.success(request, "Notification has been marked as read.")

            except Notification.DoesNotExist:
                messages.error(request, "The notification you are trying to update does not exist.")

        elif action == 'mark_all_read':
            # Mark all unread notifications as read
            count = Notification.objects.filter(is_read=False).update(is_read=True)
            messages.success(request, f"{count} notifications have been marked as read.")

        elif action == 'delete':
            notification_id = request.POST.get('notification_id')

            try:
                notification = Notification.objects.get(id=notification_id)
                notification.delete()
                messages.success(request, "Notification has been deleted successfully.")

            except Notification.DoesNotExist:
                messages.error(request, "The notification you are trying to delete does not exist.")

        return redirect('custom_admin:notification_management')

    # GET request
    notifications = Notification.objects.all().order_by('-created_at')

    # Filter by notification type if provided
    notification_type = request.GET.get('notification_type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)

    # Filter by read status if provided
    is_read = request.GET.get('is_read')
    if is_read is not None:
        is_read = is_read == 'true'
        notifications = notifications.filter(is_read=is_read)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        notifications = notifications.filter(
            title__icontains=search_query
        ) | notifications.filter(
            message__icontains=search_query
        ) | notifications.filter(
            user__email__icontains=search_query
        )

    # Get all users for the specific user dropdown
    all_users = CustomUser.objects.all().order_by('first_name', 'last_name')

    context = {
        'notifications': notifications,
        'notification_type': notification_type,
        'is_read': is_read,
        'search_query': search_query,
        'all_users': all_users,
    }

    return render(request, 'custom_admin/notification_management.html', context)

@login_required
@user_passes_test(is_admin)
def subscription_plan_management(request):
    """View for managing subscription plans."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            # Get basic plan details
            name = request.POST.get('name')
            plan_type = request.POST.get('plan_type')
            price = request.POST.get('price')
            duration_days = request.POST.get('duration_days')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active') == 'on'

            # Get feature flags based on plan type
            if plan_type == 'job_seeker':
                resume_builder = request.POST.get('resume_builder') == 'on'
                resume_review = request.POST.get('resume_review') == 'on'
                job_match_recommendations = request.POST.get('job_match_recommendations') == 'on'
                company_recommendations = request.POST.get('company_recommendations') == 'on'

                # Create job seeker plan
                SubscriptionPlan.objects.create(
                    name=name,
                    plan_type=plan_type,
                    price=price,
                    duration_days=duration_days,
                    description=description,
                    is_active=is_active,
                    resume_builder=resume_builder,
                    resume_review=resume_review,
                    job_match_recommendations=job_match_recommendations,
                    company_recommendations=company_recommendations
                )
            else:
                featured_jobs = request.POST.get('featured_jobs') == 'on'
                priority_listing = request.POST.get('priority_listing') == 'on'
                candidate_matching = request.POST.get('candidate_matching') == 'on'
                advanced_analytics = request.POST.get('advanced_analytics') == 'on'

                # Create employer plan
                SubscriptionPlan.objects.create(
                    name=name,
                    plan_type=plan_type,
                    price=price,
                    duration_days=duration_days,
                    description=description,
                    is_active=is_active,
                    featured_jobs=featured_jobs,
                    priority_listing=priority_listing,
                    candidate_matching=candidate_matching,
                    advanced_analytics=advanced_analytics
                )

            messages.success(request, f"Subscription plan '{name}' has been created successfully.")

        elif action == 'edit':
            plan_id = request.POST.get('plan_id')

            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)

                # Update basic plan details
                plan.name = request.POST.get('name')
                plan.plan_type = request.POST.get('plan_type')
                plan.price = request.POST.get('price')
                plan.duration_days = request.POST.get('duration_days')
                plan.description = request.POST.get('description')
                plan.is_active = request.POST.get('is_active') == 'on'

                # Update feature flags based on plan type
                if plan.plan_type == 'job_seeker':
                    plan.resume_builder = request.POST.get('resume_builder') == 'on'
                    plan.resume_review = request.POST.get('resume_review') == 'on'
                    plan.job_match_recommendations = request.POST.get('job_match_recommendations') == 'on'
                    plan.company_recommendations = request.POST.get('company_recommendations') == 'on'

                    # Reset employer features
                    plan.featured_jobs = False
                    plan.priority_listing = False
                    plan.candidate_matching = False
                    plan.advanced_analytics = False
                else:
                    plan.featured_jobs = request.POST.get('featured_jobs') == 'on'
                    plan.priority_listing = request.POST.get('priority_listing') == 'on'
                    plan.candidate_matching = request.POST.get('candidate_matching') == 'on'
                    plan.advanced_analytics = request.POST.get('advanced_analytics') == 'on'

                    # Reset job seeker features
                    plan.resume_builder = False
                    plan.resume_review = False
                    plan.job_match_recommendations = False
                    plan.company_recommendations = False

                plan.save()
                messages.success(request, f"Subscription plan '{plan.name}' has been updated successfully.")

            except SubscriptionPlan.DoesNotExist:
                messages.error(request, "The subscription plan you are trying to edit does not exist.")

        elif action == 'delete':
            plan_id = request.POST.get('plan_id')

            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
                name = plan.name

                # Check if there are active subscriptions
                if plan.subscriptions.count() > 0:
                    messages.warning(request, f"Cannot delete plan '{name}' because it has active subscriptions. Consider marking it as inactive instead.")
                else:
                    plan.delete()
                    messages.success(request, f"Subscription plan '{name}' has been deleted successfully.")

            except SubscriptionPlan.DoesNotExist:
                messages.error(request, "The subscription plan you are trying to delete does not exist.")

        return redirect('custom_admin:subscription_plan_management')

    # GET request
    plans = SubscriptionPlan.objects.all().order_by('price')

    # Filter by plan type if provided
    plan_type = request.GET.get('plan_type')
    if plan_type:
        plans = plans.filter(plan_type=plan_type)

    # Filter by active status if provided
    is_active = request.GET.get('is_active')
    if is_active is not None:
        is_active = is_active == 'true'
        plans = plans.filter(is_active=is_active)

    context = {
        'plans': plans,
        'plan_type': plan_type,
        'is_active': is_active,
    }

    return render(request, 'custom_admin/subscription_plan_management.html', context)

@login_required
@user_passes_test(is_admin)
def user_subscription_management(request):
    """View for managing user subscriptions."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            user_id = request.POST.get('user_id')
            plan_id = request.POST.get('plan_id')
            start_date = request.POST.get('start_date')
            duration = request.POST.get('duration')
            notify_user = request.POST.get('notify_user') == 'on'

            try:
                user = CustomUser.objects.get(id=user_id)
                plan = SubscriptionPlan.objects.get(id=plan_id)

                # Calculate end date based on duration
                from datetime import datetime, timedelta
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = start_date_obj + timedelta(days=int(duration))

                # Create subscription
                subscription = UserSubscription.objects.create(
                    user=user,
                    plan=plan,
                    start_date=start_date_obj,
                    end_date=end_date_obj,
                    status='active',
                    amount_paid=plan.price
                )

                # Create notification for the user
                if notify_user:
                    Notification.objects.create(
                        user=user,
                        notification_type='subscription',
                        title='New Subscription Added',
                        message=f'You have been subscribed to the {plan.name} plan by an administrator.',
                        related_id=subscription.id
                    )

                messages.success(request, f"Subscription for {user.get_full_name()} has been created successfully.")

            except CustomUser.DoesNotExist:
                messages.error(request, "The selected user does not exist.")
            except SubscriptionPlan.DoesNotExist:
                messages.error(request, "The selected plan does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'edit':
            subscription_id = request.POST.get('subscription_id')
            plan_id = request.POST.get('plan_id')
            status = request.POST.get('status')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            notify_user = request.POST.get('notify_user') == 'on'

            try:
                subscription = UserSubscription.objects.get(id=subscription_id)
                old_status = subscription.status
                old_plan = subscription.plan

                # Update subscription details
                subscription.plan = SubscriptionPlan.objects.get(id=plan_id)
                subscription.status = status
                subscription.start_date = start_date
                subscription.end_date = end_date
                subscription.save()

                # Create notification for the user
                if notify_user:
                    if old_status != status:
                        Notification.objects.create(
                            user=subscription.user,
                            notification_type='subscription',
                            title='Subscription Status Updated',
                            message=f'Your subscription status has been updated to {subscription.get_status_display()}.',
                            related_id=subscription.id
                        )
                    elif old_plan.id != int(plan_id):
                        Notification.objects.create(
                            user=subscription.user,
                            notification_type='subscription',
                            title='Subscription Plan Changed',
                            message=f'Your subscription plan has been changed to {subscription.plan.name}.',
                            related_id=subscription.id
                        )
                    else:
                        Notification.objects.create(
                            user=subscription.user,
                            notification_type='subscription',
                            title='Subscription Updated',
                            message=f'Your subscription details have been updated by an administrator.',
                            related_id=subscription.id
                        )

                messages.success(request, f"Subscription for {subscription.user.get_full_name()} has been updated successfully.")

            except UserSubscription.DoesNotExist:
                messages.error(request, "The subscription you are trying to edit does not exist.")
            except SubscriptionPlan.DoesNotExist:
                messages.error(request, "The selected plan does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'cancel':
            subscription_id = request.POST.get('subscription_id')

            try:
                subscription = UserSubscription.objects.get(id=subscription_id)

                # Update subscription status
                subscription.status = 'cancelled'
                subscription.save()

                # Create notification for the user
                Notification.objects.create(
                    user=subscription.user,
                    notification_type='subscription',
                    title='Subscription Cancelled',
                    message='Your subscription has been cancelled by an administrator.',
                    related_id=subscription.id
                )

                messages.success(request, f"Subscription for {subscription.user.get_full_name()} has been cancelled successfully.")

            except UserSubscription.DoesNotExist:
                messages.error(request, "The subscription you are trying to cancel does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:user_subscription_management')

    # GET request
    subscriptions = UserSubscription.objects.all().order_by('-start_date')

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        subscriptions = subscriptions.filter(status=status)

    # Filter by plan if provided
    plan_id = request.GET.get('plan')
    if plan_id:
        subscriptions = subscriptions.filter(plan_id=plan_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        subscriptions = subscriptions.filter(
            user__email__icontains=search_query
        ) | subscriptions.filter(
            user__first_name__icontains=search_query
        ) | subscriptions.filter(
            user__last_name__icontains=search_query
        ) | subscriptions.filter(
            plan__name__icontains=search_query
        )

    # Get all plans for filter dropdown
    all_plans = SubscriptionPlan.objects.all().order_by('plan_type', 'price')

    # Get all users for add subscription form
    all_users = CustomUser.objects.all().order_by('first_name', 'last_name')

    # Get today's date for default start date
    from django.utils import timezone
    today = timezone.now().date()

    context = {
        'subscriptions': subscriptions,
        'status': status,
        'plan_id': plan_id,
        'search_query': search_query,
        'all_plans': all_plans,
        'all_users': all_users,
        'today': today,
    }

    return render(request, 'custom_admin/user_subscription_management.html', context)

@login_required
@user_passes_test(is_admin)
def paystack_config_management(request):
    """View for managing Paystack configuration."""
    config = PaystackConfig.get_config()

    if request.method == 'POST':
        # Update configuration
        config.public_key = request.POST.get('public_key')
        config.secret_key = request.POST.get('secret_key')
        config.is_live_mode = request.POST.get('is_live_mode') == 'on'
        config.webhook_secret = request.POST.get('webhook_secret')

        # Handle currency
        currency = request.POST.get('currency')
        if currency:
            config.currency = currency

        config.save()
        messages.success(request, "Paystack configuration has been updated successfully.")
        return redirect('custom_admin:paystack_config_management')

    # Generate webhook and callback URLs
    webhook_url = request.build_absolute_uri(reverse('subscriptions:paystack_webhook'))
    callback_url = request.build_absolute_uri(reverse('subscriptions:payment_callback'))

    context = {
        'config': config,
        'webhook_url': webhook_url,
        'callback_url': callback_url,
    }

    return render(request, 'custom_admin/paystack_config_management.html', context)

@login_required
@user_passes_test(is_admin)
def test_paystack_payment(request):
    """View for testing Paystack payment."""
    # Redirect to the simple test page
    return redirect('custom_admin:simple_paystack_test')


@login_required
@user_passes_test(is_admin)
def simple_paystack_test(request):
    """Simple standalone Paystack test page."""
    context = {
        'email': request.user.email
    }
    return render(request, 'custom_admin/paystack_test.html', context)


@login_required
@user_passes_test(is_admin)
def paystack_test_success(request):
    """Success page for Paystack test payment."""
    reference = request.GET.get('reference', 'N/A')
    context = {
        'reference': reference
    }
    return render(request, 'custom_admin/paystack_test_success.html', context)

@login_required
@user_passes_test(is_admin)
def resume_analysis_management(request):
    """View for managing resume analyses."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            analysis_id = request.POST.get('analysis_id')

            try:
                analysis = ResumeAnalysis.objects.get(id=analysis_id)
                user_name = analysis.user.get_full_name()

                # Delete the analysis
                analysis.delete()

                messages.success(request, f"Resume analysis for {user_name} has been deleted successfully.")

            except ResumeAnalysis.DoesNotExist:
                messages.error(request, "The resume analysis you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:resume_analysis_management')

    # GET request
    analyses = ResumeAnalysis.objects.all().order_by('-created_at')

    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        analyses = analyses.filter(user_id=user_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        analyses = analyses.filter(
            user__email__icontains=search_query
        ) | analyses.filter(
            user__first_name__icontains=search_query
        ) | analyses.filter(
            user__last_name__icontains=search_query
        )

    # Get all users for filter dropdown
    all_users = CustomUser.objects.filter(
        id__in=ResumeAnalysis.objects.values_list('user_id', flat=True).distinct()
    ).order_by('first_name', 'last_name')

    context = {
        'analyses': analyses,
        'user_id': user_id,
        'search_query': search_query,
        'all_users': all_users,
    }

    return render(request, 'custom_admin/resume_analysis_management.html', context)

@login_required
@user_passes_test(is_admin)
def resume_builder_management(request):
    """View for managing resume builders."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            builder_id = request.POST.get('builder_id')

            try:
                builder = ResumeBuilder.objects.get(id=builder_id)
                user_name = builder.user.get_full_name()

                # Delete the resume builder
                builder.delete()

                messages.success(request, f"Resume for {user_name} has been deleted successfully.")

            except ResumeBuilder.DoesNotExist:
                messages.error(request, "The resume you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:resume_builder_management')

    # GET request
    builders = ResumeBuilder.objects.all().order_by('-created_at')

    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        builders = builders.filter(user_id=user_id)

    # Filter by job if provided
    job_id = request.GET.get('job')
    if job_id:
        builders = builders.filter(job_listing_id=job_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        builders = builders.filter(
            user__email__icontains=search_query
        ) | builders.filter(
            user__first_name__icontains=search_query
        ) | builders.filter(
            user__last_name__icontains=search_query
        ) | builders.filter(
            job_listing__title__icontains=search_query
        ) | builders.filter(
            title__icontains=search_query
        )

    # Get all users for filter dropdown
    all_users = CustomUser.objects.filter(
        id__in=ResumeBuilder.objects.values_list('user_id', flat=True).distinct()
    ).order_by('first_name', 'last_name')

    # Get all jobs for filter dropdown
    all_jobs = JobListing.objects.filter(
        id__in=ResumeBuilder.objects.values_list('job_listing_id', flat=True).distinct()
    ).order_by('title')

    context = {
        'builders': builders,
        'user_id': user_id,
        'job_id': job_id,
        'search_query': search_query,
        'all_users': all_users,
        'all_jobs': all_jobs,
    }

    return render(request, 'custom_admin/resume_builder_management.html', context)

@login_required
@user_passes_test(is_admin)
def job_match_score_management(request):
    """View for managing job match scores."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            score_id = request.POST.get('score_id')

            try:
                score = JobMatchScore.objects.get(id=score_id)
                user_name = score.user.get_full_name()
                job_title = score.job.title

                # Delete the job match score
                score.delete()

                messages.success(request, f"Job match score for {user_name} and job '{job_title}' has been deleted successfully.")

            except JobMatchScore.DoesNotExist:
                messages.error(request, "The job match score you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:job_match_score_management')

    # GET request
    scores = JobMatchScore.objects.all().order_by('-overall_match')

    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        scores = scores.filter(user_id=user_id)

    # Filter by job if provided
    job_id = request.GET.get('job')
    if job_id:
        scores = scores.filter(job_id=job_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        scores = scores.filter(
            user__email__icontains=search_query
        ) | scores.filter(
            user__first_name__icontains=search_query
        ) | scores.filter(
            user__last_name__icontains=search_query
        ) | scores.filter(
            job__title__icontains=search_query
        ) | scores.filter(
            job__company__name__icontains=search_query
        )

    # Get all users for filter dropdown
    all_users = CustomUser.objects.filter(
        id__in=JobMatchScore.objects.values_list('user_id', flat=True).distinct()
    ).order_by('first_name', 'last_name')

    # Get all jobs for filter dropdown
    all_jobs = JobListing.objects.filter(
        id__in=JobMatchScore.objects.values_list('job_id', flat=True).distinct()
    ).order_by('title')

    context = {
        'scores': scores,
        'user_id': user_id,
        'job_id': job_id,
        'search_query': search_query,
        'all_users': all_users,
        'all_jobs': all_jobs,
    }

    return render(request, 'custom_admin/job_match_score_management.html', context)

@login_required
@user_passes_test(is_admin)
def company_match_score_management(request):
    """View for managing company match scores."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            score_id = request.POST.get('score_id')

            try:
                score = CompanyMatchScore.objects.get(id=score_id)
                user_name = score.user.get_full_name()
                company_name = score.company.name

                # Delete the company match score
                score.delete()

                messages.success(request, f"Company match score for {user_name} and company '{company_name}' has been deleted successfully.")

            except CompanyMatchScore.DoesNotExist:
                messages.error(request, "The company match score you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:company_match_score_management')

    # GET request
    scores = CompanyMatchScore.objects.all().order_by('-overall_match')

    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        scores = scores.filter(user_id=user_id)

    # Filter by company if provided
    company_id = request.GET.get('company')
    if company_id:
        scores = scores.filter(company_id=company_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        scores = scores.filter(
            user__email__icontains=search_query
        ) | scores.filter(
            user__first_name__icontains=search_query
        ) | scores.filter(
            user__last_name__icontains=search_query
        ) | scores.filter(
            company__name__icontains=search_query
        ) | scores.filter(
            company__industry__icontains=search_query
        )

    # Get all users for filter dropdown
    all_users = CustomUser.objects.filter(
        id__in=CompanyMatchScore.objects.values_list('user_id', flat=True).distinct()
    ).order_by('first_name', 'last_name')

    # Get all companies for filter dropdown
    all_companies = Company.objects.filter(
        id__in=CompanyMatchScore.objects.values_list('company_id', flat=True).distinct()
    ).order_by('name')

    context = {
        'scores': scores,
        'user_id': user_id,
        'company_id': company_id,
        'search_query': search_query,
        'all_users': all_users,
        'all_companies': all_companies,
    }

    return render(request, 'custom_admin/company_match_score_management.html', context)

@login_required
@user_passes_test(is_admin)
def social_account_management(request):
    """View for managing social accounts."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            account_id = request.POST.get('account_id')

            try:
                account = SocialAccount.objects.get(id=account_id)
                user_name = account.user.get_full_name()
                provider_name = account.provider.title()

                # Delete the social account
                account.delete()

                messages.success(request, f"{provider_name} account for {user_name} has been deleted successfully.")

            except SocialAccount.DoesNotExist:
                messages.error(request, "The social account you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:social_account_management')

    # GET request
    accounts = SocialAccount.objects.all().order_by('-date_joined')

    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        accounts = accounts.filter(user_id=user_id)

    # Filter by provider if provided
    provider_name = request.GET.get('provider')
    if provider_name:
        accounts = accounts.filter(provider=provider_name)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        accounts = accounts.filter(
            user__email__icontains=search_query
        ) | accounts.filter(
            user__first_name__icontains=search_query
        ) | accounts.filter(
            user__last_name__icontains=search_query
        ) | accounts.filter(
            uid__icontains=search_query
        )

    # Get all users for filter dropdown
    all_users = CustomUser.objects.filter(
        id__in=SocialAccount.objects.values_list('user_id', flat=True).distinct()
    ).order_by('first_name', 'last_name')

    # Get all providers for filter dropdown
    all_providers = SocialAccount.objects.values_list('provider', flat=True).distinct()

    context = {
        'accounts': accounts,
        'user_id': user_id,
        'provider_name': provider_name,
        'search_query': search_query,
        'all_users': all_users,
        'all_providers': all_providers,
    }

    return render(request, 'custom_admin/social_account_management.html', context)

@login_required
@user_passes_test(is_admin)
def social_app_token_management(request):
    """View for managing social application tokens."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            token_id = request.POST.get('token_id')

            try:
                token = SocialToken.objects.get(id=token_id)
                user_name = token.account.user.get_full_name()
                app_name = token.app.name

                # Delete the social token
                token.delete()

                messages.success(request, f"{app_name} token for {user_name} has been deleted successfully.")

            except SocialToken.DoesNotExist:
                messages.error(request, "The social token you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:social_app_token_management')

    # GET request
    tokens = SocialToken.objects.all()

    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        tokens = tokens.filter(account__user_id=user_id)

    # Filter by app if provided
    app_id = request.GET.get('app')
    if app_id:
        tokens = tokens.filter(app_id=app_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        tokens = tokens.filter(
            account__user__email__icontains=search_query
        ) | tokens.filter(
            account__user__first_name__icontains=search_query
        ) | tokens.filter(
            account__user__last_name__icontains=search_query
        ) | tokens.filter(
            app__name__icontains=search_query
        ) | tokens.filter(
            token__icontains=search_query
        )

    # Get all users for filter dropdown
    all_users = CustomUser.objects.filter(
        id__in=SocialToken.objects.values_list('account__user_id', flat=True).distinct()
    ).order_by('first_name', 'last_name')

    # Get all apps for filter dropdown
    all_apps = SocialApp.objects.filter(
        id__in=SocialToken.objects.values_list('app_id', flat=True).distinct()
    ).order_by('name')

    # Get current time for token expiration check
    from django.utils import timezone
    now = timezone.now()

    context = {
        'tokens': tokens,
        'user_id': user_id,
        'app_id': app_id,
        'search_query': search_query,
        'all_users': all_users,
        'all_apps': all_apps,
        'now': now,
    }

    return render(request, 'custom_admin/social_app_token_management.html', context)

@login_required
@user_passes_test(is_admin)
def social_application_management(request):
    """View for managing social applications."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            provider = request.POST.get('provider')
            name = request.POST.get('name')
            client_id = request.POST.get('client_id')
            secret = request.POST.get('secret')
            key = request.POST.get('key', '')
            sites = request.POST.getlist('sites')

            try:
                # Create the social application
                app = SocialApp.objects.create(
                    provider=provider,
                    name=name,
                    client_id=client_id,
                    secret=secret,
                    key=key
                )

                # Add sites
                site_ids = request.POST.getlist('sites')
                if site_ids:
                    from django.contrib.sites.models import Site
                    sites = Site.objects.filter(id__in=site_ids)
                    app.sites.set(sites)
                else:
                    # Add default site (id=1) if no sites are selected
                    from django.contrib.sites.models import Site
                    default_site = Site.objects.get(id=1)
                    app.sites.add(default_site)

                messages.success(request, f"Social application '{name}' has been created successfully.")

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'edit':
            app_id = request.POST.get('app_id')

            try:
                app = SocialApp.objects.get(id=app_id)

                # Update application details
                app.provider = request.POST.get('provider')
                app.name = request.POST.get('name')
                app.client_id = request.POST.get('client_id')
                app.secret = request.POST.get('secret')

                if request.POST.get('key'):
                    app.key = request.POST.get('key')

                app.save()

                # Update sites
                site_ids = request.POST.getlist('sites')
                if site_ids:
                    from django.contrib.sites.models import Site
                    sites = Site.objects.filter(id__in=site_ids)
                    app.sites.set(sites)
                else:
                    # Make sure at least the default site (id=1) is associated
                    from django.contrib.sites.models import Site
                    default_site = Site.objects.get(id=1)
                    app.sites.add(default_site)

                messages.success(request, f"Social application '{app.name}' has been updated successfully.")

            except SocialApp.DoesNotExist:
                messages.error(request, "The social application you are trying to edit does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif action == 'delete':
            app_id = request.POST.get('app_id')

            try:
                app = SocialApp.objects.get(id=app_id)
                name = app.name

                # Check if there are connected accounts
                if app.socialaccount_set.exists():
                    messages.warning(request, f"Cannot delete application '{name}' because it has connected user accounts. Please disconnect these accounts first.")
                else:
                    app.delete()
                    messages.success(request, f"Social application '{name}' has been deleted successfully.")

            except SocialApp.DoesNotExist:
                messages.error(request, "The social application you are trying to delete does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('custom_admin:social_application_management')

    # GET request
    applications = SocialApp.objects.all().order_by('name')

    # Filter by provider if provided
    provider = request.GET.get('provider')
    if provider:
        applications = applications.filter(provider=provider)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        applications = applications.filter(
            name__icontains=search_query
        ) | applications.filter(
            client_id__icontains=search_query
        )

    # Get all providers for filter dropdown
    all_providers = SocialApp.objects.values_list('provider', flat=True).distinct()

    # Get all sites for form dropdowns
    from django.contrib.sites.models import Site
    all_sites = Site.objects.all()

    context = {
        'applications': applications,
        'provider': provider,
        'search_query': search_query,
        'all_providers': all_providers,
        'all_sites': all_sites,
    }

    return render(request, 'custom_admin/social_application_management.html', context)
