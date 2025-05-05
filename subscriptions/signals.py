from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import UserSubscription
from jobs.models import Notification


@receiver(post_save, sender=UserSubscription)
def subscription_status_changed(sender, instance, created, **kwargs):
    """Send notifications when subscription status changes."""
    if created:
        # New subscription created
        Notification.objects.create(
            user=instance.user,
            notification_type='system',
            title='Subscription Created',
            message=f'Your subscription to {instance.plan.name} has been created and is pending payment.'
        )
    else:
        # Check for status changes
        if instance.status == 'active' and instance.start_date and instance.end_date:
            # Subscription activated
            Notification.objects.create(
                user=instance.user,
                notification_type='system',
                title='Subscription Activated',
                message=f'Your {instance.plan.name} subscription is now active until {instance.end_date.strftime("%B %d, %Y")}.'
            )
        elif instance.status == 'cancelled':
            # Subscription cancelled
            Notification.objects.create(
                user=instance.user,
                notification_type='system',
                title='Subscription Cancelled',
                message=f'Your {instance.plan.name} subscription has been cancelled.'
            )
        elif instance.status == 'expired':
            # Subscription expired
            Notification.objects.create(
                user=instance.user,
                notification_type='system',
                title='Subscription Expired',
                message=f'Your {instance.plan.name} subscription has expired. Renew now to continue enjoying pro features.'
            )


@receiver(post_save, sender=UserSubscription)
def check_subscription_expiry(sender, instance, **kwargs):
    """Check if subscription has expired and update status."""
    if instance.status == 'active' and instance.end_date and instance.end_date < timezone.now():
        instance.status = 'expired'
        instance.save(update_fields=['status'])


@receiver(post_save, sender=UserSubscription)
def update_user_pro_status(sender, instance, **kwargs):
    """Update the user's pro status based on subscription status."""
    # Update the user's pro status
    user = instance.user
    user.update_pro_status()

    # If this is an active subscription, make sure the user has pro status
    if instance.status == 'active' and instance.end_date and instance.end_date > timezone.now():
        if not user.is_pro or not user.pro_expiry_date or user.pro_expiry_date < instance.end_date:
            user.is_pro = True
            user.pro_expiry_date = instance.end_date
            user.save(update_fields=['is_pro', 'pro_expiry_date'])
