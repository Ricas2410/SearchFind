from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import requests
import json

from .models import SubscriptionPlan, UserSubscription, PaystackConfig


@login_required
def manage_subscription(request):
    """View for managing user's subscription."""
    # Check and update the user's subscription status
    from .utils import check_and_update_subscription_status
    has_pro = check_and_update_subscription_status(request.user, request)

    # Get user's active subscription
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()

    # Get user's subscription history
    subscription_history = UserSubscription.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Get available plans for the user's type
    available_plans = SubscriptionPlan.objects.filter(
        is_active=True,
        plan_type=request.user.user_type
    ).order_by('price')

    context = {
        'active_subscription': active_subscription,
        'subscription_history': subscription_history,
        'available_plans': available_plans,
        'has_pro': has_pro
    }

    return render(request, 'subscriptions/manage_subscription.html', context)


@login_required
def upgrade_subscription(request, plan_id):
    """View for upgrading to a different subscription plan."""
    # Get the new plan
    new_plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    # Check if plan is for the user's type
    if new_plan.plan_type != request.user.user_type:
        messages.error(request, _('This subscription plan is not available for your account type.'))
        return redirect('subscriptions:manage_subscription')

    # Get user's active subscription
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()

    if active_subscription:
        # Check if new plan is different from current plan
        if active_subscription.plan.id == new_plan.id:
            messages.warning(request, _('You are already subscribed to this plan.'))
            return redirect('subscriptions:manage_subscription')

        if request.method == 'POST':
            # Create a new subscription with the new plan
            new_subscription = UserSubscription.objects.create(
                user=request.user,
                plan=new_plan,
                status='pending',
                amount_paid=new_plan.price
            )

            # Cancel the current subscription at the end of the billing period
            active_subscription.status = 'cancelled'
            active_subscription.save()

            messages.success(request, _('Your subscription will be upgraded after payment is processed.'))

            # Redirect to payment page
            return redirect('subscriptions:process_payment', subscription_id=new_subscription.id)
    else:
        # User doesn't have an active subscription, redirect to subscribe
        return redirect('subscriptions:subscribe', plan_id=plan_id)

    context = {
        'active_subscription': active_subscription,
        'new_plan': new_plan
    }

    return render(request, 'subscriptions/upgrade_subscription.html', context)


@login_required
def downgrade_subscription(request, plan_id):
    """View for downgrading to a different subscription plan."""
    # Get the new plan
    new_plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    # Check if plan is for the user's type
    if new_plan.plan_type != request.user.user_type:
        messages.error(request, _('This subscription plan is not available for your account type.'))
        return redirect('subscriptions:manage_subscription')

    # Get user's active subscription
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()

    if not active_subscription:
        messages.error(request, _('You do not have an active subscription to downgrade.'))
        return redirect('subscriptions:manage_subscription')

    # Check if new plan is different from current plan
    if active_subscription.plan.id == new_plan.id:
        messages.warning(request, _('You are already subscribed to this plan.'))
        return redirect('subscriptions:manage_subscription')

    # Check if new plan is cheaper than current plan
    if new_plan.price >= active_subscription.plan.price:
        messages.warning(request, _('The selected plan is not a downgrade. Please use the upgrade option instead.'))
        return redirect('subscriptions:manage_subscription')

    if request.method == 'POST':
        # Schedule the downgrade for the end of the current billing period
        active_subscription.status = 'downgrading'
        active_subscription.save()

        # Create a new pending subscription with the new plan
        new_subscription = UserSubscription.objects.create(
            user=request.user,
            plan=new_plan,
            status='scheduled',
            start_date=active_subscription.end_date,
            end_date=active_subscription.end_date + timezone.timedelta(days=new_plan.duration_days),
            amount_paid=new_plan.price
        )

        messages.success(request, _('Your subscription will be downgraded at the end of your current billing period.'))
        return redirect('subscriptions:manage_subscription')

    context = {
        'active_subscription': active_subscription,
        'new_plan': new_plan
    }

    return render(request, 'subscriptions/downgrade_subscription.html', context)


@login_required
def renew_subscription(request, subscription_id):
    """View for renewing an expired or cancelled subscription."""
    subscription = get_object_or_404(UserSubscription, id=subscription_id, user=request.user)

    # Check if subscription is expired or cancelled
    if subscription.status not in ['expired', 'cancelled']:
        messages.error(request, _('This subscription cannot be renewed.'))
        return redirect('subscriptions:manage_subscription')

    # Check if plan is still active
    if not subscription.plan.is_active:
        messages.error(request, _('This subscription plan is no longer available.'))
        return redirect('subscriptions:plans')

    if request.method == 'POST':
        # Create a new subscription with the same plan
        new_subscription = UserSubscription.objects.create(
            user=request.user,
            plan=subscription.plan,
            status='pending',
            amount_paid=subscription.plan.price
        )

        messages.success(request, _('Your subscription will be renewed after payment is processed.'))

        # Redirect to payment page
        return redirect('subscriptions:process_payment', subscription_id=new_subscription.id)

    context = {
        'subscription': subscription
    }

    return render(request, 'subscriptions/renew_subscription.html', context)


@require_POST
@login_required
def cancel_subscription_api(request):
    """API view for cancelling a subscription."""
    subscription_id = request.POST.get('subscription_id')

    if not subscription_id:
        return JsonResponse({'success': False, 'message': _('Subscription ID is required.')})

    try:
        subscription = UserSubscription.objects.get(id=subscription_id, user=request.user)

        # Check if subscription is active
        if subscription.status != 'active':
            return JsonResponse({'success': False, 'message': _('This subscription cannot be cancelled.')})

        # Cancel the subscription
        subscription.status = 'cancelled'
        subscription.save()

        # If using Paystack, cancel the subscription there too
        if subscription.payment_method == 'paystack' and subscription.transaction_id:
            try:
                # Get Paystack configuration
                paystack_config = PaystackConfig.get_config()

                # Cancel subscription with Paystack
                headers = {
                    'Authorization': f'Bearer {paystack_config.secret_key}',
                    'Content-Type': 'application/json'
                }

                url = f'https://api.paystack.co/subscription/{subscription.transaction_id}/disable'

                response = requests.post(url, headers=headers)
                response_data = response.json()

                if not response.status_code == 200 or not response_data.get('status'):
                    # Log the error but continue with local cancellation
                    print(f"Error cancelling Paystack subscription: {response_data.get('message')}")
            except Exception as e:
                # Log the error but continue with local cancellation
                print(f"Error cancelling Paystack subscription: {str(e)}")

        # Update user's pro status
        request.user.is_pro = False
        request.user.save(update_fields=['is_pro'])

        return JsonResponse({
            'success': True,
            'message': _('Your subscription has been cancelled. You will have access to pro features until the end of your current billing period.')
        })
    except UserSubscription.DoesNotExist:
        return JsonResponse({'success': False, 'message': _('Subscription not found.')})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def subscription_invoice(request, subscription_id):
    """View for displaying a subscription invoice."""
    subscription = get_object_or_404(UserSubscription, id=subscription_id, user=request.user)

    context = {
        'subscription': subscription,
        'company_name': 'SearchFind',
        'company_address': '123 Main Street, City, Country',
        'company_email': 'billing@searchfind.com',
        'invoice_number': f'INV-{subscription.id}',
        'invoice_date': subscription.created_at.date(),
        'due_date': subscription.created_at.date(),
        'subtotal': subscription.amount_paid,
        'tax_rate': 0,
        'tax_amount': 0,
        'total': subscription.amount_paid
    }

    return render(request, 'subscriptions/invoice.html', context)
