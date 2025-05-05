from .models import Notification, JobCategory, SiteSettings

def base_context(request):
    """Add common context variables to all templates."""
    context = {}

    # Add site settings
    site_settings = SiteSettings.get_settings()
    context['site_settings'] = site_settings

    # Add unread notifications count for authenticated users
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        context['unread_notifications_count'] = unread_notifications_count

        # Check if user has an active pro subscription
        has_pro = False
        if hasattr(request.user, 'has_active_pro'):
            try:
                # Import the utility function to check and update subscription status
                from subscriptions.utils import check_and_update_subscription_status
                has_pro = check_and_update_subscription_status(request.user)
            except ImportError:
                # Fall back to the user's has_active_pro method
                has_pro = request.user.has_active_pro()

        context['has_pro'] = has_pro

    # Add job categories for navigation
    categories = JobCategory.objects.all()
    context['categories'] = categories

    return context
