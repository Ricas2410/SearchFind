import json
import hmac
import hashlib
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.db.models import Q

from .models import SubscriptionPlan, UserSubscription, PaystackConfig
from .ai_models import ResumeAnalysis, JobMatchScore, CompanyMatchScore, ResumeBuilder
from .forms import ResumeBuilderForm, ResumeUploadForm, PaystackConfigForm
from jobs.models import JobListing, Company, Notification


@login_required
def subscription_plans(request):
    """View for displaying available subscription plans."""
    user_type = request.user.user_type

    # Get active plans for the user's type
    plans = SubscriptionPlan.objects.filter(
        is_active=True,
        plan_type=user_type
    ).order_by('price')

    # Get user's active subscription if any
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()

    context = {
        'plans': plans,
        'active_subscription': active_subscription,
        'user_type': user_type
    }

    return render(request, 'subscriptions/plans.html', context)


@login_required
def subscribe(request, plan_id):
    """View for subscribing to a plan."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    # Check if plan is for the user's type
    if plan.plan_type != request.user.user_type:
        messages.error(request, _('This subscription plan is not available for your account type.'))
        return redirect('subscriptions:plans')

    # Check if user already has an active subscription
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()

    if active_subscription:
        messages.warning(request, _('You already have an active subscription. Please cancel it before subscribing to a new plan.'))
        return redirect('subscriptions:plans')

    # Create a pending subscription
    subscription = UserSubscription.objects.create(
        user=request.user,
        plan=plan,
        status='pending',
        amount_paid=plan.price
    )

    # Redirect to payment page
    return redirect('subscriptions:process_payment', subscription_id=subscription.id)


@login_required
def process_payment(request, subscription_id):
    """View for processing payment for a subscription."""
    subscription = get_object_or_404(UserSubscription, id=subscription_id, user=request.user)

    # Check if subscription is still pending
    if subscription.status != 'pending':
        messages.error(request, _('This subscription has already been processed.'))
        return redirect('subscriptions:plans')

    # Get Paystack configuration
    paystack_config = PaystackConfig.get_config()

    if request.method == 'POST':
        # Check if we have a Paystack reference from the frontend
        paystack_reference = request.POST.get('paystack_reference')

        if paystack_reference:
            # Payment was processed on the frontend, verify the transaction
            try:
                headers = {
                    'Authorization': f'Bearer {paystack_config.secret_key}'
                }

                url = f'https://api.paystack.co/transaction/verify/{paystack_reference}'

                response = requests.get(url, headers=headers)
                response_data = response.json()

                if response.status_code == 200 and response_data.get('status'):
                    # Transaction was successful
                    transaction_data = response_data.get('data', {})

                    # Activate the subscription
                    subscription.status = 'active'
                    subscription.start_date = timezone.now()
                    subscription.end_date = subscription.start_date + timezone.timedelta(days=subscription.plan.duration_days)
                    subscription.payment_method = 'paystack'
                    subscription.transaction_id = paystack_reference
                    subscription.save()

                    # Update user's pro status if applicable
                    if hasattr(request.user, 'is_pro'):
                        request.user.is_pro = True
                        request.user.pro_expiry_date = subscription.end_date
                        request.user.save(update_fields=['is_pro', 'pro_expiry_date'])

                    messages.success(request, _('Payment successful! Your subscription is now active.'))

                    # Redirect based on user type
                    if request.user.user_type == 'job_seeker':
                        return redirect('jobs:job_seeker_dashboard')
                    else:
                        return redirect('jobs:employer_dashboard')
                else:
                    # Transaction failed
                    error_message = response_data.get('message', 'Payment verification failed.')
                    messages.error(request, _(error_message))
            except Exception as e:
                messages.error(request, _(f'Payment verification failed: {str(e)}'))
        else:
            # No reference provided, this is the initial form submission
            # We'll let the frontend handle the payment now
            pass

        # For development/testing only - hidden fallback option
        if settings.DEBUG and request.GET.get('debug_mode') == 'activate':
            # Simulate a successful payment (only in development)
            subscription.status = 'active'
            subscription.start_date = timezone.now()
            subscription.end_date = subscription.start_date + timezone.timedelta(days=subscription.plan.duration_days)
            subscription.payment_method = 'paystack'
            subscription.transaction_id = f"DEMO-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            subscription.save()

            # Update user's pro status if applicable
            if hasattr(request.user, 'is_pro'):
                request.user.is_pro = True
                request.user.pro_expiry_date = subscription.end_date
                request.user.save(update_fields=['is_pro', 'pro_expiry_date'])

            messages.success(request, _('Your subscription is now active.'))

            # Redirect based on user type
            if request.user.user_type == 'job_seeker':
                return redirect('jobs:job_seeker_dashboard')
            else:
                return redirect('jobs:employer_dashboard')

    # Convert USD to GHS for Paystack (using a fixed exchange rate for simplicity)
    # In a production environment, you would use a real-time exchange rate API
    usd_to_ghs_rate = 12.5  # Example rate: 1 USD = 12.5 GHS
    amount_in_ghs = round(float(subscription.amount_paid) * usd_to_ghs_rate)

    # Make sure we're using the correct Paystack test keys and GHS currency
    # This is critical as your Paystack account requires GHS
    if not paystack_config.is_live:
        # Force test keys and GHS currency for test mode
        paystack_config.public_key = 'pk_test_3e58947994e1d69561d4f58adae8960f49fbdcae'
        paystack_config.secret_key = 'sk_test_64854aaaedd7c3a36ccb741ddfd4b553e3f95901'
        paystack_config.currency = 'GHS'  # Must be GHS for your Paystack account
        paystack_config.save()

    # Log payment details for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Processing payment for subscription {subscription.id}")
    logger.info(f"Amount: ${subscription.amount_paid} USD / GH₵{amount_in_ghs} GHS")
    logger.info(f"Using Paystack test keys with GHS currency")

    # Generate a unique payment reference
    import random
    payment_reference = f"sf_{subscription.id}_{int(timezone.now().timestamp())}_{random.randint(1000, 9999)}"
    logger.info(f"Generated payment reference: {payment_reference}")

    context = {
        'subscription': subscription,
        'amount_paid_in_ngn': amount_in_ghs,  # Using the same template variable name for compatibility
        'debug': settings.DEBUG,
        'payment_reference': payment_reference  # Pass reference to template
    }

    return render(request, 'subscriptions/process_payment.html', context)


def payment_callback(request):
    """Callback view for Paystack payment."""
    # Get the reference from the URL parameters
    reference = request.GET.get('reference')

    if not reference:
        messages.error(request, _('Payment reference not found.'))
        return redirect('subscriptions:plans')

    # Get Paystack configuration
    paystack_config = PaystackConfig.get_config()

    # Check if this is a test payment from admin
    is_test_payment = reference.startswith('test_')

    # Verify the transaction with Paystack
    try:
        # Use the configured secret key
        headers = {
            'Authorization': f'Bearer {paystack_config.secret_key}'
        }

        url = f'https://api.paystack.co/transaction/verify/{reference}'

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status'):
            # Transaction was successful
            transaction_data = response_data.get('data', {})

            # Log successful transaction for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Payment successful for reference: {reference}")
            logger.info(f"Transaction data: {transaction_data}")

            # Handle test payment from admin dashboard
            if is_test_payment:
                # Log successful test payment
                logger.info(f"Test payment successful! Reference: {reference}")

                # Show success message
                messages.success(request, _('Test payment successful! Your Paystack integration is working correctly.'))

                # Always redirect to admin dashboard for test payments
                return redirect('custom_admin:paystack_config_management')

            # Handle regular subscription payment
            # Get the subscription from the reference
            subscription_id = None
            if reference.startswith('sf_'):
                # Extract subscription ID from our custom reference format
                parts = reference.split('_')
                if len(parts) > 1:
                    subscription_id = parts[1]

            if not subscription_id:
                # Try to get from metadata
                metadata = transaction_data.get('metadata', {})
                subscription_id = metadata.get('subscription_id')

            if subscription_id:
                try:
                    subscription = UserSubscription.objects.get(id=subscription_id)

                    # Activate the subscription
                    subscription.status = 'active'
                    subscription.start_date = timezone.now()
                    subscription.end_date = subscription.start_date + timezone.timedelta(days=subscription.plan.duration_days)
                    subscription.payment_method = 'paystack'
                    subscription.transaction_id = reference
                    subscription.save()

                    messages.success(request, _('Payment successful! Your subscription is now active.'))

                    # Redirect based on user type
                    if request.user.is_authenticated:
                        if request.user.user_type == 'job_seeker':
                            return redirect('jobs:job_seeker_dashboard')
                        else:
                            return redirect('jobs:employer_dashboard')
                    else:
                        return redirect('jobs:home')

                except UserSubscription.DoesNotExist:
                    messages.error(request, _('Subscription not found.'))
            else:
                messages.error(request, _('Subscription reference not found in transaction data.'))
        else:
            # Transaction failed
            error_message = response_data.get('message', 'Payment verification failed.')
            messages.error(request, _(error_message))

            # Log failed transaction for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Payment verification failed for reference: {reference}")
            logger.error(f"Response: {response_data}")

    except Exception as e:
        messages.error(request, _(f'Payment verification failed: {str(e)}'))

        # Log exception for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Exception during payment verification: {str(e)}")

    # If user is admin, redirect to admin dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('custom_admin:paystack_config_management')
    else:
        return redirect('subscriptions:plans')


@login_required
def cancel_subscription(request, subscription_id):
    """View for cancelling a subscription."""
    subscription = get_object_or_404(UserSubscription, id=subscription_id, user=request.user)

    if request.method == 'POST':
        subscription.cancel()
        messages.success(request, _('Your subscription has been cancelled.'))

        # Redirect based on user type
        if request.user.user_type == 'job_seeker':
            return redirect('jobs:job_seeker_dashboard')
        else:
            return redirect('jobs:employer_dashboard')

    context = {
        'subscription': subscription
    }

    return render(request, 'subscriptions/cancel_subscription.html', context)


@csrf_exempt
def paystack_webhook(request):
    """Webhook for Paystack payment notifications."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Get Paystack configuration
    paystack_config = PaystackConfig.get_config()

    # Verify webhook signature - using hardcoded test secret for consistency
    signature = request.headers.get('X-Paystack-Signature')
    if signature:
        # Compute HMAC with SHA512
        import hmac
        import hashlib

        computed_signature = hmac.new(
            b'sk_test_64854aaaedd7c3a36ccb741ddfd4b553e3f95901',  # Use test secret key
            request.body,
            hashlib.sha512
        ).hexdigest()

        if signature != computed_signature:
            return HttpResponse(status=401)

    # Parse the event data
    try:
        event_data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    event = event_data.get('event')

    # Log the webhook event for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Received Paystack webhook: {event}")

    if event == 'charge.success':
        # Handle successful payment
        data = event_data.get('data', {})
        reference = data.get('reference')

        # Find the subscription with this reference
        subscription = UserSubscription.objects.filter(transaction_id=reference).first()

        if subscription:
            # Activate the subscription
            subscription.status = 'active'
            subscription.start_date = timezone.now()
            subscription.end_date = subscription.start_date + timezone.timedelta(days=subscription.plan.duration_days)
            subscription.payment_method = 'paystack'
            subscription.save()

            # Update user's pro status
            user = subscription.user
            user.is_pro = True
            user.pro_expiry_date = subscription.end_date
            user.save(update_fields=['is_pro', 'pro_expiry_date'])

            # Create notification for user
            from jobs.models import Notification
            Notification.objects.create(
                user=user,
                notification_type='system',
                title=_('Subscription Activated'),
                message=_(f'Your {subscription.plan.name} subscription has been activated and is valid until {subscription.end_date.strftime("%B %d, %Y")}.'),
            )

            logger.info(f"Subscription {subscription.id} activated for user {user.id}")

    elif event == 'subscription.create':
        # Handle subscription creation
        data = event_data.get('data', {})
        reference = data.get('reference')
        subscription_code = data.get('subscription_code')

        # Find the subscription with this reference
        subscription = UserSubscription.objects.filter(transaction_id=reference).first()

        if subscription:
            # Update subscription with Paystack subscription code
            subscription.transaction_id = subscription_code
            subscription.save(update_fields=['transaction_id'])

            logger.info(f"Subscription {subscription.id} updated with code {subscription_code}")

    elif event == 'subscription.disable':
        # Handle subscription cancellation
        data = event_data.get('data', {})
        subscription_code = data.get('subscription_code')

        # Find the subscription with this code
        subscription = UserSubscription.objects.filter(transaction_id=subscription_code).first()

        if subscription:
            # Cancel the subscription
            subscription.status = 'cancelled'
            subscription.save(update_fields=['status'])

            # Update user's pro status
            user = subscription.user
            user.is_pro = False
            user.save(update_fields=['is_pro'])

            # Create notification for user
            from jobs.models import Notification
            Notification.objects.create(
                user=user,
                notification_type='system',
                title=_('Subscription Cancelled'),
                message=_(f'Your {subscription.plan.name} subscription has been cancelled.'),
            )

            logger.info(f"Subscription {subscription.id} cancelled for user {user.id}")

    return HttpResponse(status=200)


# AI Features for Pro Users

@login_required
def resume_builder(request):
    """View for AI resume builder feature."""
    # Check if user has an active pro subscription
    has_pro = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__resume_builder=True
    ).exists()

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    if request.method == 'POST':
        form = ResumeBuilderForm(request.POST)
        if form.is_valid():
            resume_builder = form.save(commit=False)
            resume_builder.user = request.user
            resume_builder.save()

            # Use the real AI implementation to generate resume content
            from .ai_services import ResumeBuilderService

            # Get user data for resume generation
            user_data = {
                'name': request.user.get_full_name() or request.user.username,
                'original_content': resume_builder.original_content,
                'skills': request.user.skills if hasattr(request.user, 'skills') else '',
                'experience': request.user.experience if hasattr(request.user, 'experience') else '',
                'education': request.user.education if hasattr(request.user, 'education') else '',
                'bio': request.user.bio if hasattr(request.user, 'bio') else ''
            }

            # Get job listing if specified
            job_listing = None
            if resume_builder.target_job_id:
                try:
                    job_listing = JobListing.objects.get(id=resume_builder.target_job_id)
                except JobListing.DoesNotExist:
                    pass

            # Generate resume using the service
            resume_data = ResumeBuilderService.generate_resume(
                user_data=user_data,
                job_listing=job_listing,
                template_style=resume_builder.template_style or 'standard'
            )

            # Update the resume builder with the generated content
            resume_builder.generated_summary = resume_data.get('generated_summary', '')
            resume_builder.generated_skills = resume_data.get('generated_skills', [])
            resume_builder.generated_experience = resume_data.get('generated_experience', [])
            resume_builder.generated_education = resume_data.get('generated_education', [])
            resume_builder.save()

            return redirect('subscriptions:resume_builder_result', builder_id=resume_builder.id)
    else:
        form = ResumeBuilderForm()

    # Get user's job listings for targeting resume
    if request.user.user_type == 'job_seeker':
        job_listings = JobListing.objects.filter(status='published')[:10]
    else:
        job_listings = []

    context = {
        'form': form,
        'job_listings': job_listings
    }

    return render(request, 'subscriptions/resume_builder.html', context)


@login_required
def resume_builder_result(request, builder_id):
    """View for displaying AI resume builder results."""
    resume_builder = get_object_or_404(ResumeBuilder, id=builder_id, user=request.user)

    context = {
        'resume_builder': resume_builder
    }

    return render(request, 'subscriptions/resume_builder_result.html', context)


@login_required
def resume_analysis(request):
    """View for AI resume analysis feature."""
    # Check if user has an active pro subscription
    has_pro = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__resume_review=True
    ).exists()

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = form.cleaned_data['resume_file']

            # Create a new resume analysis
            analysis = ResumeAnalysis.objects.create(
                user=request.user,
                resume_file=resume_file
            )

            # Use the real AI implementation to analyze the resume
            from .ai_services import ResumeAnalysisService

            # Analyze the resume using our real AI implementation
            analysis_results = ResumeAnalysisService.analyze_resume(resume_file=resume_file)

            # Check if the file is a valid resume
            if not analysis_results.get('is_valid', False):
                error_message = analysis_results.get('error', 'The uploaded file does not appear to be a valid resume.')
                messages.error(request, error_message)
                messages.warning(request, 'Please ensure you upload a proper resume file (PDF, DOCX, or TXT) with relevant professional information.')
                analysis.delete()  # Delete the invalid analysis
                return redirect('subscriptions:resume_analysis')

            # Update the analysis with the results
            analysis.skill_score = analysis_results.get('skill_score', 0)
            analysis.experience_score = analysis_results.get('experience_score', 0)
            analysis.education_score = analysis_results.get('education_score', 0)
            analysis.overall_score = analysis_results.get('overall_score', 0)

            # Update parsed data
            analysis.parsed_skills = analysis_results.get('parsed_skills', {})
            analysis.parsed_experience = analysis_results.get('parsed_experience', [])
            analysis.parsed_education = analysis_results.get('parsed_education', [])

            # Update suggestions
            analysis.suggestions = analysis_results.get('suggestions', [])

            analysis.save()

            return redirect('subscriptions:resume_analysis_result', analysis_id=analysis.id)
    else:
        form = ResumeUploadForm()

    # Get user's previous analyses
    previous_analyses = ResumeAnalysis.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'form': form,
        'previous_analyses': previous_analyses
    }

    return render(request, 'subscriptions/resume_analysis.html', context)


@login_required
def resume_analysis_result(request, analysis_id):
    """View for displaying AI resume analysis results."""
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, user=request.user)

    context = {
        'analysis': analysis
    }

    return render(request, 'subscriptions/resume_analysis_result.html', context)


@login_required
def job_match_score(request, job_id):
    """View for displaying job match score for a specific job."""
    job = get_object_or_404(JobListing, id=job_id, status='published')

    # Check if user is a job seeker
    if request.user.user_type != 'job_seeker':
        messages.error(request, _('This feature is only available for job seekers.'))
        return redirect('jobs:job_detail', job_id=job_id)

    # Check if user has an active pro subscription with job match feature
    has_pro = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__job_match_recommendations=True
    ).exists()

    # Get or create job match score
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

    # If user has pro subscription or this is a new match, calculate the score
    if has_pro or created:
        # Use the real AI implementation to calculate job match score
        from .ai_services import JobMatchService

        # Calculate match score using our candidate matching system
        match_results = JobMatchService.calculate_match_score(user=request.user, job=job)

        # Update match score with the results
        match_score.skills_match = match_results.get('skills_match', 0)
        match_score.experience_match = match_results.get('experience_match', 0)
        match_score.education_match = match_results.get('education_match', 0)
        match_score.overall_match = match_results.get('overall_match', 0)
        match_score.matching_skills = match_results.get('matching_skills', [])
        match_score.missing_skills = match_results.get('missing_skills', [])
        match_score.save()

    context = {
        'job': job,
        'match_score': match_score,
        'has_pro': has_pro
    }

    return render(request, 'subscriptions/job_match_score.html', context)


# Admin views for Paystack configuration

@login_required
def admin_paystack_config(request):
    """Admin view for configuring Paystack settings."""
    # Check if user is an admin
    if not request.user.is_superuser:
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('jobs:home')

    # Get current configuration
    config = PaystackConfig.get_config()

    if request.method == 'POST':
        form = PaystackConfigForm(request.POST)
        if form.is_valid():
            # Update configuration
            config.public_key = form.cleaned_data['public_key']
            config.secret_key = form.cleaned_data['secret_key']
            config.is_live = form.cleaned_data['is_live']
            config.currency = form.cleaned_data['currency']

            if form.cleaned_data['webhook_secret']:
                config.webhook_secret = form.cleaned_data['webhook_secret']

            config.save()

            messages.success(request, _('Paystack configuration updated successfully.'))
            return redirect('admin:index')
    else:
        form = PaystackConfigForm(initial={
            'public_key': config.public_key,
            'secret_key': config.secret_key,
            'webhook_secret': config.webhook_secret,
            'is_live': config.is_live,
            'currency': config.currency
        })

    # Generate webhook URL
    webhook_url = request.build_absolute_uri(reverse('subscriptions:paystack_webhook'))

    context = {
        'form': form,
        'config': config,
        'webhook_url': webhook_url
    }

    return render(request, 'subscriptions/admin_paystack_config.html', context)
