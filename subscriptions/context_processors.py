from .models import UserSubscription
from django.utils import timezone

def subscription_context(request):
    """
    Context processor to add subscription information to all templates.
    """
    context = {
        'has_pro': False,
        'active_subscription': None,
    }
    
    if request.user.is_authenticated:
        # Check if user has an active subscription
        active_subscription = UserSubscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).first()
        
        context['active_subscription'] = active_subscription
        context['has_pro'] = request.user.has_active_pro()
    
    return context
